from crypto_feature_store.db.session import engine
from crypto_feature_store.models.dbmodels import Base

print("Creating tables...")
Base.metadata.create_all(engine)
print("Done.")