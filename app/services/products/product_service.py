"""Product service — full CRUD with species / breed tagging."""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.breeds import Breed
from app.models.pet_species import PetSpecies
from app.models.products import Product
from app.repositories.product_brands import product_brand_repository
from app.repositories.product_categories import product_category_repository
from app.repositories.product_repository import product_repository
from app.schemas.products import ProductCreate, ProductUpdate

logger = structlog.get_logger(__name__)


class ProductService:
    # ── User-facing (active only) ──────────────────────────────────────

    async def get_active_products(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        species_id: UUID | None = None,
        search: str | None = None,
    ) -> Sequence[Product]:
        return await product_repository.get_active(
            db,
            skip=skip,
            limit=limit,
            brand_id=brand_id,
            category_id=category_id,
            species_id=species_id,
            search=search,
        )

    async def count_active_products(
        self,
        db: AsyncSession,
        *,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        search: str | None = None,
    ) -> int:
        return await product_repository.count_active(
            db, brand_id=brand_id, category_id=category_id, search=search
        )

    async def get_product_for_user(
        self, db: AsyncSession, product_id: Any
    ) -> Product:
        product = await product_repository.get(db, product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return product

    # ── Admin ──────────────────────────────────────────────────────────

    async def get_all_products(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> Sequence[Product]:
        return await product_repository.get_all_admin(
            db,
            skip=skip,
            limit=limit,
            brand_id=brand_id,
            category_id=category_id,
            is_active=is_active,
            search=search,
        )

    async def count_all_products(
        self,
        db: AsyncSession,
        *,
        brand_id: UUID | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> int:
        return await product_repository.count_all_admin(
            db,
            brand_id=brand_id,
            category_id=category_id,
            is_active=is_active,
            search=search,
        )

    async def get_product(self, db: AsyncSession, product_id: Any) -> Product:
        product = await product_repository.get(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return product

    async def create_product(
        self, db: AsyncSession, *, obj_in: ProductCreate
    ) -> Product:
        # Validate SKU uniqueness
        if await product_repository.get_by_sku(db, obj_in.sku):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with this SKU already exists",
            )

        # Validate brand exists
        brand = await product_brand_repository.get(db, obj_in.brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Brand not found"
            )

        # Validate category exists
        category = await product_category_repository.get(
            db, obj_in.product_category_id
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found"
            )

        # Resolve species tags
        species_list = await self._resolve_species(db, obj_in.species_ids)
        # Resolve breed tags
        breed_list = await self._resolve_breeds(db, obj_in.breed_ids)

        # Create product
        product_data = obj_in.model_dump(exclude={"species_ids", "breed_ids"})
        new_product = Product(**product_data)
        new_product.species = list(species_list)
        new_product.breeds = list(breed_list)

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        logger.info(
            "product_created",
            product_id=str(new_product.product_id),
            sku=new_product.sku,
            product_name=new_product.product_name,
            brand_id=str(obj_in.brand_id),
            category_id=str(obj_in.product_category_id),
            species_count=len(species_list),
            breed_count=len(breed_list),
        )
        return new_product

    async def update_product(
        self, db: AsyncSession, *, product_id: Any, obj_in: ProductUpdate
    ) -> Product:
        product = await self.get_product(db, product_id)

        # Check SKU uniqueness if changed
        if obj_in.sku and obj_in.sku != product.sku:
            if await product_repository.get_by_sku(db, obj_in.sku):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Product with this SKU already exists",
                )

        # Validate brand if changed
        if obj_in.brand_id is not None:
            brand = await product_brand_repository.get(db, obj_in.brand_id)
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Brand not found"
                )

        # Validate category if changed
        if obj_in.product_category_id is not None:
            category = await product_category_repository.get(
                db, obj_in.product_category_id
            )
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found"
                )

        # Update species tags if provided
        if obj_in.species_ids is not None:
            product.species = list(
                await self._resolve_species(db, obj_in.species_ids)
            )

        # Update breed tags if provided
        if obj_in.breed_ids is not None:
            product.breeds = list(
                await self._resolve_breeds(db, obj_in.breed_ids)
            )

        # Apply scalar field changes
        update_data = obj_in.model_dump(
            exclude_unset=True, exclude={"species_ids", "breed_ids"}
        )
        for field, value in update_data.items():
            setattr(product, field, value)

        await db.commit()
        await db.refresh(product)

        logger.info(
            "product_updated",
            product_id=str(product.product_id),
            sku=product.sku,
            fields_updated=list(update_data.keys()),
        )
        return product

    async def delete_product(
        self, db: AsyncSession, *, product_id: Any
    ) -> Product:
        product = await self.get_product(db, product_id)
        deleted = await product_repository.delete(db, id=product.product_id)
        logger.info(
            "product_deleted",
            product_id=str(product.product_id),
            sku=product.sku,
        )
        return deleted

    # ── Internal helpers ───────────────────────────────────────────────

    async def _resolve_species(
        self, db: AsyncSession, species_ids: list[UUID]
    ) -> Sequence[PetSpecies]:
        if not species_ids:
            return []
        stmt = select(PetSpecies).where(PetSpecies.species_id.in_(species_ids))
        result = await db.execute(stmt)
        species = result.scalars().all()
        if len(species) != len(species_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more species IDs are invalid",
            )
        return species

    async def _resolve_breeds(
        self, db: AsyncSession, breed_ids: list[UUID]
    ) -> Sequence[Breed]:
        if not breed_ids:
            return []
        stmt = select(Breed).where(Breed.breed_id.in_(breed_ids))
        result = await db.execute(stmt)
        breeds = result.scalars().all()
        if len(breeds) != len(breed_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more breed IDs are invalid",
            )
        return breeds


product_service = ProductService()
