from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PriceBar(Base):
    __tablename__ = "price_bars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    __table_args__ = (
        UniqueConstraint("asset_id", "timestamp", name="uq_asset_time"),
    )

class IngestionState(Base):
    __tablename__ = "ingestion_state"

    asset_id = Column(String, primary_key=True)
    last_timestamp = Column(DateTime, nullable=True)
