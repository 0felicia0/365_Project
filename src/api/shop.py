from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum
from urllib.error import HTTPError
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewShop(BaseModel):
    store_name: str

@router.post("/create_shop")
def  create_shop(account_id: int, new_shop: NewShop):
    try: 
        with db.engine.begin() as connection:
            # check if account exists
            account = connection.execute(sqlalchemy.text("""
                                                        SELECT users.name
                                                        FROM users
                                                        WHERE users.user_id = :user_id
                                                        """), {"user_id": account_id}).first()
            if account is None:
                raise ValueError("Account does not exist. Cannot create a shop.") 
            
            # check if user already has a shop
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT shops.user_id
                                                        FROM shops
                                                        WHERE shops.user_id = :user_id
                                                        """), {"user_id": account_id}).first()
            
            # if account already has a shop, they cannot have another one
            if result is not None:
                raise ValueError("A shop already exists with the account. Cannot have more than one shop active.")
   
            shop_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO shops (user_id, store_name)
                    VALUES(:user_id, :store_name)
                    ON CONFLICT (store_name)
                    DO NOTHING
                    RETURNING shop_id
                    """
                ),
                [{"user_id": account_id, "store_name": new_shop.store_name}]
            ).scalar_one_or_none()
            
        if shop_id is None:
            raise ValueError("Integrity error with shop_name. Must be unique. Try Again.")

        return {"shop_id": shop_id}
            
    except Exception as v:
        return {f"Error in creating a shop: {v}"}


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
    breakpoint = 5
    
    with db.engine.begin() as connection:
        try:
            timesSold = connection.execute(
                sqlalchemy.text(
                    """
                        SELECT COUNT(*)
                        FROM shoe_inventory_ledger
                        WHERE quantity < 0 AND shop_id = :shop_id
                    """
                ),
                [{"shop_id": shop_id}]
            ).scalar()
            
            if timesSold >= breakpoint:
                return shop_id
            else:
                return "Failed Verification"
        except Exception as e:
            print("Error while posting application: ", e)

# Set the status of the given shop_id to Verified (True)
@router.post("/update_verification")
def update_verification(shop_id: int, status: bool):
    with db.engine.begin() as connection:
        try:
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
        except Exception as e:
            print("Error while updating verification status: ", e)

# Return verification status for a given shop_id
@router.get("/verification_status")
def verification_status(shop_id: int):
    with db.engine.begin() as connection:
        try:
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
        except Exception as e:
            print("Error while retrieving verification status: ", e)
            
# Flash Sale EPs

@router.get("/start_flash_sale")
def start_flash_sale(shop_id: int, disCounter: int, priceModifier: float):
    with db.engine.begin() as connection:
        try:
            # update discounter_counter in shops to disCounter
            connection.execute(
                sqlalchemy.text(
                    """
                        UPDATE shops
                        SET discounter_counter = :disCounter, price_modifier = :priceModifier
                        WHERE shop_id = :shop_id
                    """
                ),
                [{
                    "disCounter": disCounter,
                    "priceModifier": priceModifier,
                    "shop_id": shop_id
                }]
            )
            
            return "Sale started for shop %d for %d shoes at %d%% price.", shop_id, disCounter, (priceModifier * 100)
        except Exception as e:
            print("Error while starting flash sale: ", e)