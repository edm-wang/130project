# Don't Delete the comments below
# [GenAI Usage] Codex Prompt
# R1: If i want to create a post recommendation method and the created model needs to be compatible with SQL. How shall i just define a class with BaseModel to implement FastAPI ORM?
# R1 [GenAI Response]: 
# Not quite. If the model needs to be compatible with SQL, a plain BaseModel is usually not enough ... 
# For SQL compatibility, use one of these: SQLAlchemy ORM model (example 1) ...  Or SQLModel, if you want Pydantic-style models that also map to SQL (example 2) ...
# R2: I see your point. Use SQLModel to generate a class that's compatible with recommendation-related tables defined in supabase defined here: supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql
# R2 [GenAI Response]:

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class RecommendationFeedback(SQLModel, table=True):
    __tablename__ = "recommendation_feedback"
    __table_args__ = (
        CheckConstraint("feedback_value in (-1, 1)"),
        UniqueConstraint("user_id", "paper_id"),
    )

    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
    )
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("app_users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    paper_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("papers.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    feedback_value: int = Field(
        sa_column=Column(SmallInteger, nullable=False),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        ),
    )


class RecommendationBatch(SQLModel, table=True):
    __tablename__ = "recommendation_batches"
    __table_args__ = (
        CheckConstraint("status in ('pending', 'completed', 'failed')"),
        CheckConstraint("candidate_count is null or candidate_count >= 0"),
        CheckConstraint("final_count is null or final_count >= 0"),
    )

    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
    )
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("app_users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    status: str = Field(
        default="pending",
        sa_column=Column(
            Text,
            nullable=False,
            server_default=text("'pending'"),
        ),
    )
    algorithm_version: str = Field(
        default="multi_vector_v1",
        sa_column=Column(
            Text,
            nullable=False,
            server_default=text("'multi_vector_v1'"),
        ),
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(
            JSONB,
            nullable=False,
            server_default=text("'{}'::jsonb"),
        ),
    )
    candidate_count: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer),
    )
    final_count: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer),
    )
    error_message: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        ),
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )


class Recommendation(SQLModel, table=True):
    __tablename__ = "recommendations"
    __table_args__ = (
        CheckConstraint("rank_position > 0"),
        UniqueConstraint("batch_id", "paper_id"),
        UniqueConstraint("batch_id", "rank_position"),
    )

    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
    )
    batch_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("recommendation_batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    paper_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("papers.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    rank_position: int = Field(
        sa_column=Column(Integer, nullable=False),
    )
    final_score: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(
            Numeric(10, 5),
            nullable=False,
            server_default=text("0"),
        ),
    )
    interest_score: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(
            Numeric(10, 5),
            nullable=False,
            server_default=text("0"),
        ),
    )
    saved_paper_score: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(
            Numeric(10, 5),
            nullable=False,
            server_default=text("0"),
        ),
    )
    upvote_score: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(
            Numeric(10, 5),
            nullable=False,
            server_default=text("0"),
        ),
    )
    downvote_penalty: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(
            Numeric(10, 5),
            nullable=False,
            server_default=text("0"),
        ),
    )
    freshness_score: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(
            Numeric(10, 5),
            nullable=False,
            server_default=text("0"),
        ),
    )
    explanation_summary: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        ),
    )

# Don't delete comments below
# [Gen AI Usage] Reflection
# Th reason I utilzie GenAI to generate this script is because it is purely a lengthy "adapter" script that does not add any value, except for converting predefined sql interface into FastAPI
# Workflow:
# 1. I was not sure how to achieve sql-compatible ORM design. So I inqury Codex for possible design decisions, before writing any code.
# 2. Based on its response in round 1, I understand the ORM tool that is helpful is sqlalchemy and SQLModel. 
# 3. Therefore, I tell Codex the exact design choices (sqlalchemy, SQLModel) and pinpoint the database schema with relative path so that LLM would know the exact schemas
# In the end, I verfied the GenAI written code via a top-down approach. I read the class name first to understand which sql table that it is converting from. 
# Then I look into the primary key and foreign key into those tables. They are all corectly matched. 
# Finally, I look into the field definition, field type, and validation constraint if any. 
# After thorough and careful code review, I believe the generated code is correct.