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
                INSERT INTO users
                (name, email, password)
                VALUES(:name, :email, :password)
                """
            ),
            [{"name": new_account.name, "email": new_account.email, "password": new_account.password}]
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
                INSERT INTO shops (user_id, store_name)
                VALUES(:user_id, :store_name)
                """
            ),
            [{"user_id": account_id, "store_name": new_shop.store_name}]
        )
    return "OK"

class Shoe(BaseModel):
    brand: str
    color: str
    style: str

class Listing(BaseModel):
    shop_id: int
    quantity: int
    price:int
    size:int

@router.post("/create_listing")
def create_listing(shoe: Shoe, listing: Listing):
    #for testing purposes
    print("in create_listing")
    print("shoe info: ", shoe)
    print("listing info: ", listing)

    with db.engine.begin() as connection:
        #create a new transaction
        
        description = "shoe uploaded: " + shoe.color + ",  " + shoe.brand + ", " + shoe.style
        
        transaction_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transactions (description, tag)
                VALUES(:description, 'LISTING')
                RETURNING id
                """
            ),
            [{"description": description}])
        transaction_id = transaction_id.first()[0]
        
        
        
        
        #check if shoe is in shoe catalog, if it is, return ID
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM shoes
                WHERE brand = :brand AND color = :color AND style = :style
                """
            ), [{"brand": shoe.brand, "color": shoe.color, "style": shoe.style}]
        )

        row = result.fetchone()

        if row:
            shoe_id = row[0]
        else: 
            #if shoe isn't in catalog, add it, return ID
            shoe_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO shoes (brand, color, style, transaction_id)
                    VALUES (:brand, :color, :style, :transaction_id)
                    RETURNING shoe_id
                    """
                ),
                [{"brand": shoe.brand, "color": shoe.color, "style": shoe.style, "transaction_id": transaction_id}]
            )
            shoe_id = shoe_id.fetchone()[0]
        
        #insert listing into table
        listing_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO listings (shop_id, shoe_id, price, size, transaction_id)
                VALUES (:shop_id, :shoe_id, :price, :size, :transaction_id)
                RETURNING listing_id
                """    
            ),
            [{"shop_id": listing.shop_id, "shoe_id": shoe_id, "quantity": listing.quantity, "price": listing.price, "size": listing.size, "transaction_id": transaction_id}]
        )
        listing_id = listing_id.fetchone()[0]
        #update shoe_inventory ledger
        connection.execute(
            sqlalchemy.text(
                """
                INSERT into shoe_inventory_ledger(shop_id, listing_id, transaction_id, quantity)
                VALUES (:shop_id, :listing_id, :transaction_id, :quantity )
                """
            ),
            [{"shop_id": listing.shop_id, "listing_id": listing_id, "transaction_id": transaction_id, "quantity": listing.quantity}]
        )

        return "OK"