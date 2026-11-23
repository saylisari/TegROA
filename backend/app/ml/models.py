from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class AIFlowPrediction(Base):
    __tablename__ = "ai_flow_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    source_ip: Mapped[str] = mapped_column(String(45))
    destination_ip: Mapped[str] = mapped_column(String(45))
    destination_port: Mapped[int] = mapped_column(Integer)
    prediction: Mapped[str] = mapped_column(String(30))
    confidence: Mapped[float] = mapped_column(Float)
