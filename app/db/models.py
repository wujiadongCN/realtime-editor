import sqlalchemy as sa
from sqlalchemy import func
from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Document(Base):
    __tablename__ = "documents"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = sa.Column(sa.String(255), nullable=False, default="Untitled")
    content = sa.Column(sa.Text, nullable=False, default="")
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
