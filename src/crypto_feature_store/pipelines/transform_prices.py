from datetime import datetime

import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema
import polars as pl
from sqlalchemy import text

from crypto_feature_store.db.session import engine

# ---------- Pandera schema for validation ----------

features_schema = DataFrameSchema(
    {
        "asset_id": Column(str, nullable=False),
        "timestamp": Column(pa.DateTime, nullable=False),
        "close": Column(float, nullable=False),
        "return_1": Column(float, nullable=True),
        "rolling_mean_24": Column(float, nullable=True),
        "rolling_std_24": Column(float, nullable=True),
    },
    coerce=True,
    strict=True,
)


# ---------- Core functions ----------

def load_price_bars() -> pd.DataFrame:
    """Load raw price bars from Postgres into a pandas DataFrame."""
    query = text(
        """
        SELECT asset_id, timestamp, close
        FROM price_bars
        ORDER BY asset_id, timestamp
        """
    )
    df = pd.read_sql(query, engine)
    return df


def add_features_polars(df: pd.DataFrame) -> pd.DataFrame:
    """Use Polars to compute returns and rolling features."""
    if df.empty:
        return df

    pl_df = pl.from_pandas(df)

    pl_df = (
        pl_df
        .sort(["asset_id", "timestamp"])
        .with_columns(
            [
                # simple 1-step return (row-based)
                pl.col("close")
                .pct_change()
                .over("asset_id")
                .alias("return_1"),

                # rolling mean over last 24 rows within each asset
                pl.col("close")
                .rolling_mean(window_size=24)
                .over("asset_id")
                .alias("rolling_mean_24"),

                # rolling std over last 24 rows within each asset
                pl.col("close")
                .rolling_std(window_size=24)
                .over("asset_id")
                .alias("rolling_std_24"),
            ]
        )
    )

    # Back to pandas for Pandera + to_sql
    return pl_df.to_pandas()


def validate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run Pandera validation on the feature dataframe."""
    if df.empty:
        print("No data to validate.")
        return df
    return features_schema.validate(df)


def write_features(df: pd.DataFrame):
    """Write features to Postgres as table price_features (full refresh)."""
    if df.empty:
        print("No data to write.")
        return

    # Full refresh: drop & recreate table each time
    df.to_sql(
        "price_features",
        engine,
        if_exists="replace",  # change to 'append' if you later add watermarking
        index=False,
    )
    print(f"Wrote {len(df)} rows into price_features.")


def run_transform():
    print("Loading raw data...")
    raw_df = load_price_bars()
    print(f"Loaded {len(raw_df)} rows from price_bars.")

    print("Adding Polars features...")
    feat_df = add_features_polars(raw_df)

    print("Validating with Pandera...")
    feat_df = validate_features(feat_df)

    print("Writing features to Postgres...")
    write_features(feat_df)

    print("Done.")


if __name__ == "__main__":
    run_transform()
