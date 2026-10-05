from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(120))
    customer_email: Mapped[str] = mapped_column(String(120))
    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    ml_category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ml_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ml_problem_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ml_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="NEW")
    assignee: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )