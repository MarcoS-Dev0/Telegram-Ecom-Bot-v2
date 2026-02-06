"""
Product document schemas for MongoDB.

Defines Pydantic models for product CRUD operations,
variant management, and catalog search indexing.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class ProductStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    OUT_OF_STOCK = "out_of_stock"


class ProductVariant(BaseModel):
    """Single product variant (size, color, etc.)."""

    sku: str = Field(..., min_length=3, max_length=32)
    name: str = Field(..., max_length=128)
    price_cents: int = Field(..., gt=0, description="Price in smallest currency unit")
    stock: int = Field(default=0, ge=0)
    attributes: dict[str, str] = Field(default_factory=dict)

    @field_validator("sku")
    @classmethod
    def sku_uppercase(cls, v: str) -> str:
        return v.upper().strip()

    @property
    def price(self) -> Decimal:
        return Decimal(self.price_cents) / 100


class ProductImage(BaseModel):
    """Product image with Telegram file_id reference."""

    file_id: str
    url: Optional[str] = None
    alt_text: str = ""
    is_primary: bool = False


class ProductBase(BaseModel):
    """Shared fields for product creation and updates."""

    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=2048)
    category: str = Field(..., max_length=64)
    tags: list[str] = Field(default_factory=list)
    variants: list[ProductVariant] = Field(default_factory=list, max_length=20)
    images: list[ProductImage] = Field(default_factory=list, max_length=10)
    status: ProductStatus = ProductStatus.DRAFT
    metadata: dict[str, str] = Field(default_factory=dict)


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for partial product updates (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2048)
    category: Optional[str] = Field(None, max_length=64)
    tags: Optional[list[str]] = None
    variants: Optional[list[ProductVariant]] = None
    images: Optional[list[ProductImage]] = None
    status: Optional[ProductStatus] = None
    metadata: Optional[dict[str, str]] = None


class ProductInDB(ProductBase):
    """Product as stored in MongoDB with DB-generated fields."""

    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

    @property
    def default_variant(self) -> Optional[ProductVariant]:
        return self.variants[0] if self.variants else None

    @property
    def min_price_cents(self) -> int:
        if not self.variants:
            return 0
        return min(v.price_cents for v in self.variants)

    @property
    def total_stock(self) -> int:
        return sum(v.stock for v in self.variants)

    @property
    def is_available(self) -> bool:
        return self.status == ProductStatus.ACTIVE and self.total_stock > 0


class ProductResponse(ProductBase):
    """API / bot response schema with computed fields."""

    id: str
    created_at: datetime
    updated_at: datetime
    min_price: str = ""
    total_stock: int = 0

    @classmethod
    def from_db(cls, product: ProductInDB) -> ProductResponse:
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            category=product.category,
            tags=product.tags,
            variants=product.variants,
            images=product.images,
            status=product.status,
            metadata=product.metadata,
            created_at=product.created_at,
            updated_at=product.updated_at,
            min_price=f"{product.min_price_cents / 100:.2f}",
            total_stock=product.total_stock,
        )
