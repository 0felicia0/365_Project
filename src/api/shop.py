from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
    dependencies=[Depends(auth.get_api_key)],
)
class NewAccount(BaseModel):
    name: str
    email: str
    password: str
    date_of_birth: str

@router.post("/create_account")
def create_account(new_account: NewAccount):
    #for testing purposes:
    print("in create_account endpoint")
    print("new_account: ", new_account)
    #inserting information into the database
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO accounts
                (name, email, password, date_of_birth)
                VALUES(:email, :password, :date_of_birth)
                """
            ),
            [{"email": new_account.email, "password": new_account.password, "date_of_birth": new_account.date_of_birth}]
        )
    return "OK"

class NewShop(BaseModel):
    store_name: str

@router.post("/create_shop")
def  create_shop(account_id: int, new_shop: NewShop):
    #for testing purposes
    print("in create_shop endpoint")
    print("account_id: ", account_id, "new_shop: ", new_shop)

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO shops (seller_id, store_name)
                VALUES(:seller_id, :store_name)
                """
            ),
            [{"seller_id": account_id, "store_name": new_shop.store_name}]
        )
    return "OK"