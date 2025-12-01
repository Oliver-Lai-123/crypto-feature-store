from datetime import datetime, timedelta

from typing import List
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse, FileResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from crypto_feature_store.db.session import get_db
from crypto_feature_store.models.api_schemas import PriceResponse, FeatureResponse
from crypto_feature_store.db.session import engine
from crypto_feature_store.models.dbmodels import Base

app = FastAPI(
    title="Crypto Feature Store API",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    """
    Automatically create tables when the API starts.
    This replaces the need to run 'initdb.py' manually.
    """
    print("Checking database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables verified.")

@app.get("/health")
def health():
    return {"status": "ok"}


# Redirect root to the interactive docs
@app.get("/")
def root():
    return RedirectResponse(url="/docs")


# Optional: serve a favicon if you place one at src/static/favicon.ico
@app.get("/favicon.ico")
def favicon():
    static_favicon = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "static", "favicon.ico")
    )
    if os.path.exists(static_favicon):
        return FileResponse(static_favicon)
    return Response(status_code=204)


@app.get(
    "/v1/prices/{asset_id}",
    response_model=List[PriceResponse],
)
def get_prices(
    asset_id: str,
    hours: int = Query(24, ge=1, le=24 * 30, description="Lookback window in hours"),
    db: Session = Depends(get_db),
):
    """Return raw OHLC prices for the last N hours using a raw SQL query."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    sql = text(
        """
        SELECT asset_id, timestamp, open, high, low, close, volume
        FROM price_bars
        WHERE asset_id = :asset_id
          AND timestamp >= :cutoff
        ORDER BY timestamp
        """
    )

    result = db.execute(sql, {"asset_id": asset_id, "cutoff": cutoff})
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No data for this asset/time window")

    responses: List[PriceResponse] = []
    for row in rows:
        data = dict(row._mapping)
        responses.append(PriceResponse(**data))

    return responses
