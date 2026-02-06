"""
Cart document schema — MongoDB collection: carts

Each cart is scoped to a single Telegram user and holds line items with
product references, quantities, and cached unit prices. A TTL index on
`expires_at` ensures abandoned carts are garbage-collected automatically.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class CartItem(BaseModel):
    """Single line item inside a shopping cart."""

    product_id: str = Field(..., description="Reference to products collection")
    product_name: str = Field(..., description="Cached display name at add-time")
    variant: Optional[str] = Field(None, description="Size / colour / SKU variant")
    quantity: int = Field(1, ge=1, le=99)
    unit_price: float = Field(..., ge=0, description="Price in EUR at add-time")

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.unit_price, 2)


class CartDocument(BaseModel):
    """
    Root document persisted in the `carts` collection.

    Index strategy:
        - unique index on `telegram_user_id`  (one active cart per user)
        - TTL index on `expires_at`           (auto-delete stale carts)
    """

    telegram_user_id: int = Field(..., description="Telegram numeric user ID")
    items: List[CartItem] = Field(default_factory=list)
    currency: str = Field("EUR", pattern=r"^[A-Z]{3}$")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=72),
        description="TTL expiration — configurable via CART_TTL_HOURS env var",
    )

    # ── Computed helpers ────────────────────────────────────────────

    @property
    def total(self) -> float:
        """Sum of all line-item subtotals."""
        return round(sum(item.subtotal for item in self.items), 2)

    @property
    def item_count(self) -> int:
        """Total number of units (not distinct products)."""
        return sum(item.quantity for item in self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    # ── Mutation helpers ────────────────────────────────────────────

    def add_item(self, item: CartItem) -> None:
        """Add a product or increment quantity if already in cart."""
        for existing in self.items:
            if existing.product_id == item.product_id and existing.variant == item.variant:
                existing.quantity = min(existing.quantity + item.quantity, 99)
                self._touch()
                return
        self.items.append(item)
        self._touch()

    def remove_item(self, product_id: str, variant: Optional[str] = None) -> bool:
        """Remove a line item entirely. Returns True if found and removed."""
        before = len(self.items)
        self.items = [
            i for i in self.items
            if not (i.product_id == product_id and i.variant == variant)
        ]
        removed = len(self.items) < before
        if removed:
            self._touch()
        return removed

    def clear(self) -> None:
        """Empty the cart."""
        self.items.clear()
        self._touch()

    def _touch(self) -> None:
        """Bump updated_at timestamp on every mutation."""
        self.updated_at = datetime.now(timezone.utc)

    class Config:
        json_schema_extra = {
            "example": {
                "telegram_user_id": 123456789,
                "items": [
                    {
                        "product_id": "64a7f2e1b3c4d5e6f7890123",
                        "product_name": "Wireless Earbuds Pro",
                        "variant": "Black",
                        "quantity": 2,
                        "unit_price": 49.99,
                    }
                ],
                "currency": "EUR",
            }
        }
