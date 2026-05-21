# [GenAI Usage] Codex Prompt:
# Following the orm model for 3 recommendation tables (backend/app/models/recommendation.py) as an example, you can also write the orms for the paper-related tables into ORM models in backend/models/paper.py?
# The relative path where the schemas is defined: supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql
# [GenAI Usage] Response Starts:
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import UserDefinedType
from sqlmodel import Field, SQLModel


class Vector(UserDefinedType):
    cache_ok = True

    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def get_col_spec(self, **kw: Any) -> str:
        return f"vector({self.dimensions})"


class Paper(SQLModel, table=True):
    __tablename__ = "papers"
    __table_args__ = (
        CheckConstraint("source in ('arxiv', 'semantic_scholar', 'manual')"),
        CheckConstraint("length(btrim(source_id)) > 0"),
        CheckConstraint("length(btrim(title)) > 0"),
        UniqueConstraint("source", "source_id"),
    )

    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
    )
    source: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    source_id: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    title: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    abstract: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    authors_text: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    categories: List[str] = Field(
        default_factory=list,
        sa_column=Column(
            ARRAY(Text),
            nullable=False,
            server_default=text("'{}'::text[]"),
        ),
    )
    source_url: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    pdf_url: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    published_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )
    source_updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
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


class PaperEmbedding(SQLModel, table=True):
    __tablename__ = "paper_embeddings"

    paper_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("papers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    embedding_model: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    embedding: List[float] = Field(
        sa_column=Column(Vector(1536), nullable=False),
    )
    embedded_text: str = Field(
        sa_column=Column(Text, nullable=False),
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


class SavedPaper(SQLModel, table=True):
    __tablename__ = "saved_papers"
    __table_args__ = (
        CheckConstraint("category_source in ('auto', 'manual')"),
        CheckConstraint(
            "category_confidence is null or category_confidence between 0 and 1"
        ),
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
    category: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    category_source: str = Field(
        default="auto",
        sa_column=Column(
            Text,
            nullable=False,
            server_default=text("'auto'"),
        ),
    )
    category_confidence: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(4, 3)),
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

# Don't delete all comments below
# [GenAI Usage] Response Ends:
# [GenAI Usage] Reflection
# Again, the reason that I utilize Codex here is because creating ORM models is just to create an adaptor interface that is repetitive work. 
# I follow the similiar workflow as recommendation.py and write clear prompt. 
# After code generation, I still use a top-down code-review approach. I inspect the paper-related models name (Paper, SavedPaper, PaperEmbedding) first. 
# I then check if PK and Fk are correct. Finally, I check if all fields are present, in consistent type, and with correct default value or validator if any.
# After careful and thorough review, everything looks good to me. And the code shall be accepted