from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum
from urllib.error import HTTPError

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
    dependencies=[Depends(auth.get_api_key)],
)
# class NewAccount(BaseModel):
#     name: str
#     email: str
#     password: str
   

# @router.post("/create_account")
# def create_account(new_account: NewAccount):
#     # plan: check if account already exists with the email bc emails are generally unique
#     #       if so, raise error that account already exists
#     #       else, create the account
#     #       potential upgrade -> restrict password in a certain way
#     #       ENCRYPT PASSWORD!!!!! 

#     try:
#         with db.engine.begin() as connection:
#             result = connection.execute(sqlalchemy.text("""
#                                                         SELECT user_id, email
#                                                         FROM users
#                                                         WHERE email = :email
#                                                         """)
#                                                         , {"email": new_account.email}).first()

#             # if the account exists, return message indicating so, otherwise make an account
#             if result is None:
#                 # create new account because email not already in the DB
#                 # encrypt password
#                 user_id = connection.execute(sqlalchemy.text("""
#                                                     INSERT INTO users (name, email, password)
#                                                     VALUES(:name, :email, :password)
#                                                     RETURNING user_id
#                                                     """
#                                                 ),
#                                                 [{"name": new_account.name, "email": new_account.email, "password": new_account.password}]).scalar()
#                 return {"user_id": user_id}

#             else:
#                 raise HTTPError(url=None, code=400, msg="Account already exists with given email. Try a different email, or login with existing account.", hdrs={}, fp=None)
        
#     except Exception as e:
#         print("Error occured during create_account execution: ", e)
#         return {"Email already in use."}



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

class colors(str, Enum):
    Black = "Black"
    Grey = "Grey"
    White = "White"
    Ivory = "Ivory"
    Beige = "Beige"
    Brown = "Brown"
    Metallic = "Metallic"
    Purple = "Purple"
    Blue = "Blue"
    Green = "Green"
    Yellow = "Yellow"
    Orange = "Orange"
    Pink = "Pink"
    Red = "Red"
    Burgundy = "Burgundy"
    Other = "Other"

class genders(str, Enum):
    Youth = "Youth"
    Women = "Women"
    Men = "Men"
    Unisex = "Unisex"

class condition(str, Enum):
    new = "new"
    used = "used"

class Shoe(BaseModel):
    brand: str
    color: colors
    style: str

class Listing(BaseModel):
    shop_id: int
    quantity: int
    price:int
    size:int
    condition: condition
    gender: genders

@router.post("/create_listing")
def create_listing(shoe: Shoe, listing: Listing):
    try:
        with db.engine.begin() as connection:
        #with db.engine.connect().execution_options(isolation_level="Serializable") as connection:
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
                
            shoe_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO shoes (brand, color, style, transaction_id)
                    VALUES (:brand, :color, :style, :transaction_id)
                    ON CONFLICT (brand, color, style)
                    DO UPDATE SET (brand, color, style, transaction_id) = 
                        (:brand, :color, :style, :transaction_id)
                    RETURNING shoe_id
                    """
                ),
                [{"brand": shoe.brand, "color": shoe.color, "style": shoe.style, "transaction_id": transaction_id}]
            ).fetchone()[0]
            
            #insert listing into table
            listing_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO listings (shop_id, shoe_id, price, size, transaction_id, gender, condition)
                    VALUES (:shop_id, :shoe_id, :price, :size, :transaction_id, :gender, :condition)
                    RETURNING listing_id
                    """    
                ),
                [{"shop_id": listing.shop_id, "shoe_id": shoe_id, "price": listing.price, "size": listing.size, "transaction_id": transaction_id, "gender": listing.gender, "condition" : listing.condition}]
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
            
            return "successfully created listing"
    
    except HTTPError as h:
        return h.msg

    except Exception as e:
        print("Error creating listing: ", e)

# Verification EPs
@router.post("/post_application")

# If more than X shoes sold, return shop_id to send to update_verification
def post_application(shop_id: int):
    # arbitrary number
    soldBreakpoint = 1
    
    with db.engine.begin() as connection:
        shoesSold = connection.execute(
            sqlalchemy.text(
                """
                    SELECT SUM(quantity)
                    FROM shoe_inventory_ledger
                    WHERE shop_id = :shop_id
                """
            ),
            [{"shop_id": shop_id}]
        ).scalar()
        
        if shoesSold >= soldBreakpoint:
            return shop_id
        else:
            return "Failed Verification"

# Set the status of the given shop_id to Verified (True)
@router.post("/update_verification")
def update_verification(shop_id: int, status: bool):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                    UPDATE shops
                    SET verified = :status
                    WHERE shop_id = :shop_id
                """
            ),
            [{
                "status": status,
                "shop_id": shop_id
            }]
        )
        
    return "OK"

# Return verification status for a given shop_id
@router.post("/verification_status")
def verification_status(shop_id: int):
    with db.engine.begin() as connection:
        status = connection.execute(
            sqlalchemy.text(
                """
                    SELECT verified
                    FROM shops
                    WHERE shop_id = :shop_id
                """
            ),
            [{
                "shop_id": shop_id
            }]
        ).scalar()
        
        return status