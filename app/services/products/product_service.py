from typing import Any, Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.products import Product
from app.models.pet_species import PetSpecies
from app.models.breeds import Breed
from app.repositories.product_repository import product_repository
from app.repositories.product_brands import product_brand_repository
from app.repositories.product_categories import product_category_repository

from app.schemas.products import ProductCreate, ProductUpdate

class ProductService:
    async def get_all_products(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        return await product_repository.get_multi(db, skip=skip, limit=limit)

    async def get_product(self, db: AsyncSession, product_id: Any) -> Product:
        product = await product_repository.get(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def create_product(self, db: AsyncSession, *, obj_in: ProductCreate) -> Product:
        # Check SKU unique
        if await product_repository.get_by_sku(db, obj_in.sku):
            raise HTTPException(status_code=400, detail="Product with this SKU already exists")

        # Check references
        brand = await product_brand_repository.get(db, obj_in.brand_id)
        if not brand:
            raise HTTPException(status_code=400, detail="Brand not found")

        category = await product_category_repository.get(db, obj_in.product_category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

        # Fetch Relational Tags
        species_list = []
        if obj_in.species_ids:
            stmt = select(PetSpecies).where(PetSpecies.species_id.in_(obj_in.species_ids))
            result = await db.execute(stmt)
            species_list = result.scalars().all()
            if len(species_list) != len(obj_in.species_ids):
                raise HTTPException(status_code=400, detail="One or more Species IDs are invalid")

        breed_list = []
        if obj_in.breed_ids:
            stmt = select(Breed).where(Breed.breed_id.in_(obj_in.breed_ids))
            result = await db.execute(stmt)
            breed_list = result.scalars().all()
            if len(breed_list) != len(obj_in.breed_ids):
                raise HTTPException(status_code=400, detail="One or more Breed IDs are invalid")

        # Construct raw payload excluding lists to map manually
        product_data = obj_in.model_dump(exclude={"species_ids", "breed_ids"})
        new_product = Product(**product_data)
        
        # Hydrate associations
        new_product.species = list(species_list)
        new_product.breeds = list(breed_list)

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product

    async def update_product(self, db: AsyncSession, *, product_id: Any, obj_in: ProductUpdate) -> Product:
        product = await self.get_product(db, product_id)
        
        if obj_in.sku and obj_in.sku != product.sku:
            if await product_repository.get_by_sku(db, obj_in.sku):
                raise HTTPException(status_code=400, detail="Product with this SKU already exists")
        
        # Tags processing if provided
        if obj_in.species_ids is not None:
            if not obj_in.species_ids:
                product.species = []
            else:
                stmt = select(PetSpecies).where(PetSpecies.species_id.in_(obj_in.species_ids))
                result = await db.execute(stmt)
                species_list = result.scalars().all()
                if len(species_list) != len(obj_in.species_ids):
                    raise HTTPException(status_code=400, detail="Invalid species_ids provided")
                product.species = list(species_list)
                
        if obj_in.breed_ids is not None:
            if not obj_in.breed_ids:
                product.breeds = []
            else:
                stmt = select(Breed).where(Breed.breed_id.in_(obj_in.breed_ids))
                result = await db.execute(stmt)
                breed_list = result.scalars().all()
                if len(breed_list) != len(obj_in.breed_ids):
                    raise HTTPException(status_code=400, detail="Invalid breed_ids provided")
                product.breeds = list(breed_list)

        update_data = obj_in.model_dump(exclude_unset=True, exclude={"species_ids", "breed_ids"})
        for field, value in update_data.items():
            setattr(product, field, value)
            
        await db.commit()
        await db.refresh(product)
        return product

    async def delete_product(self, db: AsyncSession, *, product_id: Any) -> Product:
        product = await self.get_product(db, product_id)
        return await product_repository.delete(db, id=product.product_id)

product_service = ProductService()
