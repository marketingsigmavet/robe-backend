"""TopicQuestion service — CRUD with species/breed/product tagging."""

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
from app.models.topic_questions import TopicQuestion
from app.repositories.question_repository import question_repository
from app.schemas.topics import QuestionCreate, QuestionUpdate

logger = structlog.get_logger(__name__)


class QuestionService:
    # ── User-facing ────────────────────────────────────────────────────

    async def get_questions_for_user(
        self,
        db: AsyncSession,
        topic_id: UUID,
        *,
        species_id: UUID | None = None,
    ) -> Sequence[TopicQuestion]:
        """Active questions under a topic, optionally filtered by species."""
        return await question_repository.get_for_user(
            db, topic_id, species_id=species_id
        )

    async def get_question_for_user(
        self, db: AsyncSession, question_id: UUID
    ) -> TopicQuestion:
        q = await question_repository.get(db, question_id)
        if not q or not q.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )
        return q

    # ── Admin ──────────────────────────────────────────────────────────

    async def get_questions(
        self, db: AsyncSession, topic_id: UUID
    ) -> Sequence[TopicQuestion]:
        """All non-deleted questions under a topic (admin)."""
        return await question_repository.get_by_topic(db, topic_id)

    async def get_question(
        self, db: AsyncSession, question_id: UUID
    ) -> TopicQuestion:
        q = await question_repository.get(db, question_id)
        if not q:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )
        return q

    async def create_question(
        self,
        db: AsyncSession,
        *,
        topic_id: UUID,
        obj_in: QuestionCreate,
    ) -> TopicQuestion:
        # Resolve tags
        species_list = await self._resolve_species(db, obj_in.species_ids)
        breed_list = await self._resolve_breeds(db, obj_in.breed_ids)
        product_list = await self._resolve_products(db, obj_in.product_ids)

        data = obj_in.model_dump(exclude={"species_ids", "breed_ids", "product_ids"})
        question = TopicQuestion(topic_id=topic_id, **data)
        question.species = list(species_list)
        question.breeds = list(breed_list)
        question.products = list(product_list)

        db.add(question)
        await db.commit()
        await db.refresh(question)

        logger.info(
            "question_created",
            question_id=str(question.question_id),
            topic_id=str(topic_id),
            question_text=question.question_text[:80],
            species_count=len(species_list),
            breed_count=len(breed_list),
            product_count=len(product_list),
        )
        return question

    async def update_question(
        self,
        db: AsyncSession,
        *,
        question_id: UUID,
        obj_in: QuestionUpdate,
    ) -> TopicQuestion:
        question = await self.get_question(db, question_id)

        # Update tags if provided
        if obj_in.species_ids is not None:
            question.species = list(
                await self._resolve_species(db, obj_in.species_ids)
            )
        if obj_in.breed_ids is not None:
            question.breeds = list(
                await self._resolve_breeds(db, obj_in.breed_ids)
            )
        if obj_in.product_ids is not None:
            question.products = list(
                await self._resolve_products(db, obj_in.product_ids)
            )

        # Apply scalar fields
        update_data = obj_in.model_dump(
            exclude_unset=True,
            exclude={"species_ids", "breed_ids", "product_ids"},
        )
        for field, value in update_data.items():
            setattr(question, field, value)

        await db.commit()
        await db.refresh(question)

        logger.info(
            "question_updated",
            question_id=str(question.question_id),
            fields_updated=list(update_data.keys()),
        )
        return question

    async def delete_question(
        self, db: AsyncSession, *, question_id: UUID
    ) -> TopicQuestion:
        question = await self.get_question(db, question_id)
        deleted = await question_repository.delete(db, id=question.question_id)
        logger.info(
            "question_deleted",
            question_id=str(question.question_id),
            topic_id=str(question.topic_id),
        )
        return deleted

    # ── Internal helpers ───────────────────────────────────────────────

    async def _resolve_species(
        self, db: AsyncSession, ids: list[UUID]
    ) -> Sequence[PetSpecies]:
        if not ids:
            return []
        stmt = select(PetSpecies).where(PetSpecies.species_id.in_(ids))
        result = await db.execute(stmt)
        items = result.scalars().all()
        if len(items) != len(ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more species IDs are invalid",
            )
        return items

    async def _resolve_breeds(
        self, db: AsyncSession, ids: list[UUID]
    ) -> Sequence[Breed]:
        if not ids:
            return []
        stmt = select(Breed).where(Breed.breed_id.in_(ids))
        result = await db.execute(stmt)
        items = result.scalars().all()
        if len(items) != len(ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more breed IDs are invalid",
            )
        return items

    async def _resolve_products(
        self, db: AsyncSession, ids: list[UUID]
    ) -> Sequence[Product]:
        if not ids:
            return []
        stmt = select(Product).where(Product.product_id.in_(ids))
        result = await db.execute(stmt)
        items = result.scalars().all()
        if len(items) != len(ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more product IDs are invalid",
            )
        return items


question_service = QuestionService()
