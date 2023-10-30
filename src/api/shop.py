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
                VALUES(:name, :email, :password, :date_of_birth)
                """
            ),
            [{"name": new_account.name, "email": new_account.email, "password": new_account.password, "date_of_birth": new_account.date_of_birth}]
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

class Shoe(BaseModel):
    brand: str
    color: str
    size: int
    style: str

class Listing(BaseModel):
    shop_id: int
    quantity: int
    price:int

@router.post("/create_listing")
def create_listing(shoe: Shoe, listing: Listing):
    #for testing purposes
    print("in create_listing")
    print("shoe info: ", shoe)
    print("listing info: ", listing)

    with db.engine.begin() as connection:
        #check if shoe is in shoe catalog, if it is, return ID
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM test_shoes
                WHERE brand = :brand AND color = :color AND size = :size AND style = :style
                """
            ), [{"brand": shoe.brand, "color": shoe.color, "size": shoe.size, "style": shoe.style}]
        )

        row = result.fetchone()

        if row:
            shoe_id = row[0]
        else: 
            #if shoe isn't in catalog, add it, return ID
            shoe_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO test_shoes (brand, color, size, style)
                    VALUES (:brand, :color, :size, :style)
                    RETURNING shoe_id
                    """
                ),
                [{"brand": shoe.brand, "color": shoe.color, "size": shoe.size, "style": shoe.style}]
            )
            shoe_id = shoe_id.fetchone()[0]
        #insert listing into table
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO test_listings (shop_id, shoe_id, quantity, price)
                VALUES (:shop_id, :shoe_id, :quantity, :price)
                """    
            ),
            [{"shop_id": listing.shop_id, "shoe_id": shoe_id, "quantity": listing.quantity, "price": listing.price}]
        )

        return "OK"