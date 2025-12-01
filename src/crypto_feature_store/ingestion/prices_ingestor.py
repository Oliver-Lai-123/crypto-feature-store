from datetime import datetime, timezone
from typing import Optional, List, Dict

import httpx
from sqlalchemy.orm import Session

from crypto_feature_store.db.session import get_session
from crypto_feature_store.models.dbmodels import PriceBar, IngestionState

# === Config ===
COIN_ID = "bitcoin"        # CoinGecko coin id
ASSET_ID = "BTC"           #  internal asset code
VS_CURRENCY = "usd"
API_URL = f"https://api.coingecko.com/api/v3/coins/{COIN_ID}/market_chart"


def fetch_prices(last_timestamp: Optional[datetime]) -> List[Dict]:
    """
    Fetch price points from CoinGecko.
    We request last 1 day and then filter in Python using last_timestamp.
    """
    params = {
        "vs_currency": VS_CURRENCY,
        "days": "1",  # last 1 day; you can change to "max" or "7" later
    }

    response = httpx.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    prices = []
    for ts_ms, price in data["prices"]:
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

        # incremental: skip anything we've already seen
        if last_timestamp is not None and ts <= last_timestamp:
            continue

        prices.append(
            {
                "asset_id": ASSET_ID,
                "timestamp": ts,
                "open": float(price),
                "high": float(price),
                "low": float(price),
                "close": float(price),
                "volume": 0.0,  # we ignore volume for now
            }
        )

    return prices


def run_ingestion():
    session: Session = get_session()
    try:
        # 1. Read last ingested timestamp for this asset
        state: Optional[IngestionState] = session.get(IngestionState, ASSET_ID)
        last_ts = state.last_timestamp.replace(tzinfo=timezone.utc) if state and state.last_timestamp else None
        print(f"Last ingested timestamp for {ASSET_ID}: {last_ts}")

        # 2. Fetch new prices from API
        rows = fetch_prices(last_ts)
        if not rows:
            print("No new data to ingest.")
            return

        # 3. Insert new rows
        for row in rows:
            pb = PriceBar(**row)
            session.add(pb)

        # 4. Update ingestion state (watermark)
        latest_ts = max(r["timestamp"] for r in rows)
        if state is None:
            state = IngestionState(asset_id=ASSET_ID, last_timestamp=latest_ts)
            session.add(state)
        else:
            state.last_timestamp = latest_ts

        # 5. Commit
        session.commit()
        print(f"Inserted {len(rows)} rows up to {latest_ts}.")

    except Exception as e:
        session.rollback()
        print("Error during ingestion:", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_ingestion()
