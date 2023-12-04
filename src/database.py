import os
import dotenv
from sqlalchemy import create_engine
import sqlalchemy


def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

metadata_obj = sqlalchemy.MetaData()
#transactions = sqlalchemy.Table("transactions", metadata_obj, autoload_with=engine)
shoes = sqlalchemy.Table("shoes", metadata_obj, autoload_with= engine)
listings = sqlalchemy.Table("listings", metadata_obj, autoload_with = engine)
shoe_inventory_ledger = sqlalchemy.Table("shoe_inventory_ledger", metadata_obj, autoload_with = engine)
shops = sqlalchemy.Table("shops", metadata_obj, autoload_with= engine)