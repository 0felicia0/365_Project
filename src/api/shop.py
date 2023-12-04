from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime
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
            raise ValueError("Shop name must be unique. Try Again.")

        return {"shop_id": shop_id}
            
    except Exception as e:
        return {f"Error in creating a shop: {e}"}

# For shops to purchase a promotion tier to boost their listings
class PromotionTiers(str, Enum):
    Tier1 = "Tier1" #500
    Tier2 = "Tier2" #750
    Tier3 = "Tier3" #1000

class Payment(BaseModel):
    name: str
    credit_card: str
    exp_date: str
    security_code: int

# apply boost to all shoes, or something else??
# would be cool to turn into a subscription based promotional feature
@router.put("/{shop_id}/payment/{payment}/purchase_promotion_tier")
def purchase_promotion_tier(shop_id: int, requested_tier: PromotionTiers, payment: Payment):
    t = 0
    if requested_tier == PromotionTiers.Tier1:
        t = 1
    elif requested_tier == PromotionTiers.Tier2:
        t = 2
    elif requested_tier == PromotionTiers.Tier3:
        t = 3
    
    try: 
        # check if payment is valid

        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT shops.shop_id
                                                        FROM shops
                                                        WHERE shops.shop_id = :shop_id
                                                        """), {"shop_id": shop_id}).first()
            # shop does not exist
            if result is None:
                raise ValueError("No shop exists with given shop_id. Cannot purchase a promotion tier")
            
            # check if the promotion is already applied -> can only increase, cannot decrease tier (no point)
            # set the promotion value to tier requested
            result = connection.execute(sqlalchemy.text("""
                                                UPDATE shops
                                                SET promotion_tier = :t
                                                WHERE shop_id = :shop_id and :t > promotion_tier
                                                RETURNING 1
                                                """), {"t": t, "shop_id": shop_id}).fetchone()
            
            if result:
                return {"Promotional tier successfully purchased and applied!"}
            else:
                return {"The current promotional tier applied to the shop is already greater than or equal to the one you want to purchase."}
            
        
    except Exception as e:
        return {f"Error in purchasing a promotion tier: {e}"}

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
                        SELECT COUNT(*) AS sold, shop_id
                        FROM shoe_inventory_ledger
                        WHERE quantity < 0 AND shop_id = :shop_id
                        GROUP BY shop_id
                    """
                ),
                [{"shop_id": shop_id}]
            ).first()
            if timesSold is None:
                raise Exception("Invalid shop id for posting application.")
            if timesSold.sold >= breakpoint:
                return timesSold.shop_id
            else:
                return "Failed Verification"
        except Exception as e:
            print("Error while posting application:", e)

# Set the status of the given shop_id to Verified (True)
@router.post("/update_verification")
def update_verification(shop_id: int, status: bool):
    with db.engine.begin() as connection:
        try:
            id = connection.execute(
                sqlalchemy.text(
                    """
                        UPDATE shops
                        SET verified = :status
                        WHERE shop_id = :shop_id
                        RETURNING shop_id
                    """
                ),
                [{
                    "status": status,
                    "shop_id": shop_id
                }]
            ).scalar()
            
            if id is None:
                raise Exception("Invalid shop id for updating verification.")
            
            return id
        except Exception as e:
            print("Error while updating verification status:", e)

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
            if status is None:
                raise Exception("Invalid shop id for retrieving verifcation status.")
            return status
        except Exception as e:
            print("Error while retrieving verification status:", e)
            
# Flash Sale EPs

@router.get("/start_flash_sale")
def start_flash_sale(shop_id: int, disCounter: int, pricePercentage: int):
    with db.engine.begin() as connection:
        try:
            # check if sale is currently ongoing
            # retrieve sale_start
            saleInfo = connection.execute(sqlalchemy.text(
                """
                    SELECT 
                        discount_counter,
                        price_percentage,
                        EXTRACT(epoch FROM sale_start)::int
                    FROM shops
                    WHERE shop_id = :shop_id
                """
                ),
                    [{
                        "shop_id": shop_id
                    }]
                ).first()
            if saleInfo is None:
                    raise Exception("Invalid shop id for starting flash sale.")

            # retrieve amount discounted
            discountInfo = connection.execute(sqlalchemy.text(
                    """
                        SELECT
                            SUM(quantity) as amtDiscounted, shop_id
                        FROM shoe_inventory_ledger
                        WHERE shop_id = :shop_id AND quantity < 0
                        AND (EXTRACT(epoch FROM created_at)::int - :startTime) > 0
                        GROUP BY shop_id
                    """
                ),
                                   [{
                                       "shop_id": shop_id,
                                       "startTime": saleInfo[1]
                                   }]
                                   ).scalar()
            if discountInfo is None:
                amtDiscounted = 0
            else:
                amtDiscounted = abs(discountInfo.amtDiscounted)
            
            # sale is still active, can't start new sale.
            if amtDiscounted < saleInfo.discount_counter:    
                return "Sale for shop %d is still active for %d more shoe(s) at %d%% price." % (shop_id, (saleInfo.discount_counter - amtDiscounted), pricePercentage)
            
            # update discounter_counter in shops to disCounter
            else:
                connection.execute(
                    sqlalchemy.text(
                        """
                            UPDATE shops
                            SET 
                                discount_counter = :disCounter,
                                price_percentage = :pricePercentage,
                                sale_start = :startTime
                            WHERE shop_id = :shop_id
                        """
                    ),
                    [{
                        "disCounter": disCounter,
                        "pricePercentage": pricePercentage,
                        "shop_id": shop_id,
                        "startTime": datetime.now().astimezone()
                    }]
                )
                return "Sale started for shop %d for %d shoe(s) at %d%% price." % (shop_id, disCounter, pricePercentage)
        except Exception as e:
            print("Error while starting flash sale: ", e)