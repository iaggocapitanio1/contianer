# Python imports
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel
# Pip imports
from pydantic import Extra
from tortoise.queryset import QuerySet

# Internal imports
from src.database.models.inventory.container_inventory import ContainerInventory

from tortoise.contrib.pydantic import pydantic_model_creator

from src.database.models.inventory.depot import Depot

DepotSerializer = pydantic_model_creator(
    Depot,
    name="DepotSerializer",
    include=("id", "name", "street_address", "city", "state", "zip", "primary_email", "primary_phone"),
)

# =========================
# Config for Pydantic models
# =========================
class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


# =========================
# VendorOut Serializer (Nested)
# =========================
class PickupRegion(str, Enum):
    A = "PU A"
    B = "PU B"
    C = "PU C"


class Region(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class ProductCategoryOut(BaseModel):
    id: UUID
    name: Optional[str] = None
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True  # Enables automatic conversion from ORM models
        extra = 'allow'  # Allows additional fields if necessary


class LocationPriceOut(BaseModel):
    id: UUID
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    pickup_region: Optional[PickupRegion] = None
    average_delivery_days: int = 15

    class Config:
        orm_mode = True  # Enables automatic conversion from ORM models
        extra = 'allow'  # Allows additional fields if necessary


class AccountOut(BaseModel):
    id: int
    created_at: datetime
    modified_at: datetime
    name: str
    is_active: bool
    cms_attributes: Optional[Dict[str, Any]] = None
    integrations: Optional[Dict[str, Any]] = None
    external_integrations: Optional[Dict[str, Any]] = None
    order_status_selection: Optional[Dict[str, Any]] = None
    order_status_options: Optional[Dict[str, Any]] = None
    pod_contract: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    terms_and_conditions_paid: bool

    class Config:
        orm_mode = True  # Enables automatic conversion from Tortoise ORM



    class Config:
        orm_mode = True



class ContainerProductOut(BaseModel):
    id: UUID
    created_at: datetime
    modified_at: datetime
    condition: Optional[str] = None
    container_size: Optional[str] = None
    product_type: Optional[str] = None
    location: Optional[LocationPriceOut] = None
    name: str



    @property
    def title(self) -> str:
        # Implement your logic to compute the title here
        # For example:
        return f"{self.container_size} - {self.name}"

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['title'] = self.title
        return data

    def json(self, *args, **kwargs):
        data = self.dict(*args, **kwargs)
        import json
        return json.dumps(data, *args, **kwargs)

    class Config:
        orm_mode = True

    @property
    def title(self) -> str:
        components = [
            f"{self.container_size}'" if self.container_size else "",
            self.condition or "",
            self.product_type or ""
        ]
        # Filter out empty components and join them with spaces
        return " ".join(filter(None, components)).strip()


class VendorOut(BaseModel):
    id: UUID
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    account_id: Optional[int] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None
    secondary_phone: Optional[str] = None
    secondary_email: Optional[str] = None
    country: Optional[str] = None
    country_code_primary: Optional[str] = None
    country_code_secondary: Optional[str] = None

    class Config:
        orm_mode = True  # Enables automatic ORM conversion


# =========================
# ContainerInventoryOut Serializer
# =========================
class ContainerInventorySimplerOut(BaseModel):
    id: str
    total_cost: Optional[Decimal] = None
    status: Optional[str] = None
    purchase_type: Optional[str] = None
    invoice_number: Optional[str] = None
    invoiced_at: Optional[datetime] = None
    pickup_at: Optional[datetime] = None
    payment_type: Optional[str] = None
    paid_at: Optional[datetime] = None
    container_number: Optional[str] = None
    container_release_number: Optional[str] = None
    vendor: Optional[VendorOut] = None  # Nested Vendor serializer
    account_id: Optional[int] = None
    depot_id: Optional[int] = None
    container_color: Optional[str] = None
    image_urls: Optional[List[str]] = None
    metadata: Optional[dict] = None
    description: Optional[str] = None
    revenue: Optional[Decimal] = None
    product: Optional[ContainerProductOut] = None  # Nested Product serializer
    depot: Optional[DepotSerializer] = None  # Nested Depot serializer
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    @classmethod
    async def from_queryset(cls, queryset: QuerySet[ContainerInventory]) -> List["ContainerInventorySimplerOut"]:
        """
        Convert a Tortoise ORM queryset into a list of Pydantic models.
        """
        results = []
        data = await queryset.prefetch_related("vendor", "product", "depot", "product__location")

        for obj in data:
            vendor_data = VendorOut.from_orm(obj.vendor) if obj.vendor else None
            depot_data = DepotSerializer.from_orm(obj.depot) if obj.depot else None
            product_data = None

            if obj.product:
                location = LocationPriceOut.from_orm(obj.product.location)
                product_data = ContainerProductOut(
                    id=obj.product.id,
                    created_at=obj.product.created_at,
                    modified_at=obj.product.modified_at,
                    condition=obj.product.condition,
                    container_size=obj.product.container_size,
                    product_type=obj.product.product_type,
                    location=location,
                    name=obj.product.name,
                )

            container_data = cls(
                id=str(obj.pk),
                total_cost=obj.total_cost,
                status=obj.status,
                purchase_type=obj.purchase_type,
                invoice_number=obj.invoice_number,
                invoiced_at=obj.invoiced_at,
                pickup_at=obj.pickup_at,
                payment_type=obj.payment_type,
                paid_at=obj.paid_at,
                container_number=obj.container_number,
                container_release_number=obj.container_release_number,
                vendor=vendor_data,
                account_id=obj.account_id,
                depot_id=obj.depot_id,
                container_color=obj.container_color,
                image_urls=obj.image_urls,
                metadata=obj.metadata,
                description=obj.description,
                revenue=obj.revenue,
                product=product_data,
                depot=depot_data,
                created_at=obj.created_at,
                modified_at=obj.modified_at,
            )
            results.append(container_data)

        return results

    class Config:
        orm_mode = True  # Enables conversion from Tortoise ORM models
        extra = Extra.allow  # Allows additional fields if necessary
