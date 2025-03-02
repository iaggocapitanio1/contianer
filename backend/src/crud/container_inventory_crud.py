# Python imports
from datetime import datetime, timedelta
from typing import cast

# Pip imports
from tortoise.expressions import Q
from tortoise.models import Model
from tortoise.queryset import QuerySet

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.inventory.container_inventory import ContainerInventory
from src.schemas.container_inventory import ContainerInventoryIn, ContainerInventoryOut, ContainerInventoryUpdateIn

from ._types import PAGINATION
from loguru import logger


class ContainerInventoryCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ContainerInventoryOut
        self.create_schema = ContainerInventoryIn
        self.update_schema = ContainerInventoryUpdateIn
        self.db_model = ContainerInventory
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=1000)

    async def get_inventory_by_depot(self, account_id: int, depot_id: str) -> Model:

        query = (
            self.db_model.filter(account_id=account_id)
            .filter(depot_id=depot_id)
            .filter(status="Available")
            .order_by("-created_at")
        )

        return await self.schema.from_queryset(query)

    async def get_count(self) -> int:
        return await self.get_queryset().count()

    async def get_by_status_type(
        self, account_id: int, status: str, purchase_type: str, pagination: PAGINATION
    ) -> Model:
        skip, limit = pagination.get("skip", 0), pagination.get("limit", None)

        # Start with base queryset filtered by account_id
        queryset: QuerySet[Model] = self.db_model.filter(account_id=account_id)

        # Apply purchase_type filter if not "ALL"
        if purchase_type and purchase_type != "ALL":
            queryset = queryset.filter(purchase_type__in=[purchase_type])

        # Apply status filter if not "All"
        if status != "All":
            queryset = queryset.filter(status=status)

        # Apply ordering
        queryset = queryset.order_by("-created_at")
        self.set_queryset(queryset)

        # Apply pagination at the end
        queryset = queryset.offset(cast(int, skip))
        if limit:
            queryset = queryset.limit(limit)

        logger.info(queryset.sql())
        # log what other relations are being used
        # self.schema.from_queryset(query)
        # log the relations
        # logger.info(self.db_model.sql())
        #         backend-1       |   File "/app/src/crud/container_inventory_crud.py", line 67, in get_by_status_type
        # backend-1       |     logger.info(self.db_model.sql())
        # backend-1       | AttributeError: type object 'ContainerInventory' has no attribute 'sql'
        logger.info(self.db_model.all().sql())

        return await self.schema.from_queryset(queryset)

    async def get_one_prefix(self, account_id: int, item_id: str) -> Model:
        if self.has_account_id():
            model = await self.db_model.filter(account_id=account_id).filter(id__startswith=item_id).first()
        else:
            model = await self.db_model.filter(id__startswith=item_id).first()
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_containers_without_container_numbers(self, account_id: int):
        query = self.db_model.filter(account_id=account_id)
        query = query.filter(Q(container_number__isnull=True) | Q(container_number=""))
        today = datetime.utcnow().date()
        # 30 days or older
        query = query.filter(Q(created_at__lte=today - timedelta(days=30)))

        return await self.schema.from_queryset(query)

    async def search_inventory(
        self,
        account_id: int,
        container_release: str = None,
        container_number: str = None,
        container_availability: str = None,
    ) -> Model:

        query = self.db_model.filter(account_id=account_id)

        if container_release:
            query = query.filter(container_release_number__icontains=container_release)

        if container_number:
            query = query.filter(container_number__icontains=container_number)

        if container_availability and container_availability != 'All':
            query = query.filter(status=container_availability)

        query = query.order_by("-created_at")
        return await self.schema.from_queryset(query)

    async def get_one_container_number(self, account_id: int, container_number: str) -> Model:
        if self.has_account_id():
            model = await self.db_model.filter(account_id=account_id).filter(container_number=container_number).first()
        else:
            model = await self.db_model.filter(container_number=container_number).first()
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            return None

    async def search_related_inventory(
        self,
        account_id: int,
        container_release: str = None,
    ):

        query = self.db_model.filter(account_id=account_id)
        if container_release:
            query = query.filter(container_release_number=container_release)
        query = query.order_by("-created_at")
        return await self.schema.from_queryset(query)


container_inventory_crud = ContainerInventoryCRUD()
