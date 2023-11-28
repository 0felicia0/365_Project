from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum
from urllib.error import HTTPError
from sqlalchemy.exc import IntegrityError

# hi
router = APIRouter(
    prefix="/carts",
    tags=["carts"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCart(BaseModel):
    user_id: int

@router.post("/user_id/{user_id}/new_cart")
def create_cart(new_cart: NewCart):

    """ """            
    try:
        # plan: see if any active carts available
        #       if none, create cart, else return the active one
        # see if other exceptions have a message field, can cause issues if not -> update the exception block

        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT cart_id, user_id, active
                                                        FROM carts
                                                        WHERE active = TRUE AND user_id = :user_id
                                                        """), 
                                                        {"user_id": new_cart.user_id}).first()

            if result is None:
                print("No active cart with user_id:", new_cart.user_id, "| Creating new cart.")
                cart_id = connection.execute(sqlalchemy.text("""
                                                            INSERT INTO carts (user_id, active)
                                                            VALUES (:user_id, TRUE)
                                                            RETURNING cart_id;"""), 
                                                            {"user_id": new_cart.user_id}).scalar()
                return {"cart_id": cart_id}
            
            raise HTTPError(url=None, code=400, msg="Cart already active with given user_id. Checkout before activating another cart.", hdrs={}, fp=None)

    except HTTPError as e:
        return e.msg

    except Exception as e:
        print("Error in the process of creating a new cart: ", e)
    
    

@router.get("/user_id/{user_id}/get_cart")
def get_cart(user_id: int):

    """ """            
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT cart_id
                                                        FROM carts
                                                        WHERE active = TRUE AND user_id = :user_id
                                                        """), 
                                                        {"user_id": user_id}).first()

            if result is not None:
                return {"cart_id": result.cart_id}
            
            raise HTTPError(url=None, code=400, msg="No active cart found with given user_id.", hdrs={}, fp=None)

    except HTTPError as e:
        return e.msg
    
    except Exception as e:
        print("Error in the process of getting an active/existing cart: ", e)
    

@router.post("/{cart_id}/listing/{listing_id}/quantity/{quantity}")
def set_item_quantity(cart_id: int, listing_id: int, quantity: int):
    """Update DB to reflect adding a shoe to a specific cart"""

    # make sure cart is active, listing exists, and enough quantity available

    try:
        with db.engine.begin() as connection:
            # check if cart is active / exists, else raise 400 error (bad request)
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT cart_id, user_id, active
                                                        FROM carts
                                                        WHERE cart_id = :cart_id AND active = TRUE
                                                        """)
                                                        , {"cart_id": cart_id}).first()
            if result is None:
                raise HTTPError(url=None, code=400, msg="No active cart found with the given cart_id. Try making a new cart.", hdrs={}, fp=None)

            #check if listing exists and has enough inventory, else raise 400 error
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT listings.listing_id, SUM(shoe_inventory_ledger.quantity)
                                                        FROM listings
                                                        JOIN shoe_inventory_ledger on listings.listing_id = shoe_inventory_ledger.listing_id
                                                        WHERE listings.listing_id = :listing_id
                                                        GROUP BY listings.listing_id
                                                        HAVING SUM(shoe_inventory_ledger.quantity) >= :quantity
                                                        """)
                                                        , {"listing_id": listing_id, "quantity": quantity}).first()
            if result is None:
                raise HTTPError(url=None, code=400, msg="No listing found with the given listing_id and desired quantity.", hdrs={}, fp=None)

            
            # at this point we have valid inputs and sufficient quantity, add to the cart
            connection.execute(sqlalchemy.text("""
                                                INSERT INTO cart_items (listing_id, cart_id, quantity)
                                                VALUES (:listing_id, :cart_id, :quantity)
                                                """), 
                                                {"listing_id": listing_id, "cart_id": cart_id, "quantity": quantity})  

            return {"Item added to cart!"}
    
    except HTTPError as e:
        return e.msg
    
    except Exception as e:
        print("Error in the process of adding an item to a cart: ", e)


@router.post("/checkout")
def checkout(cart_id: int):

 # have to update ledgers, create transaction,

    with db.engine.begin() as connection:

        try:    
            res = connection.execute(sqlalchemy.text("""
                                                     SELECT carts.active 
                                                     FROM carts 
                                                     WHERE carts.cart_id = :cart_id 
                                                           AND carts.active = TRUE"""), {"cart_id": cart_id}).first()

            if res is None:
                raise HTTPError(url=None, code=400, msg="No active cart found with the given cart_id.", hdrs={}, fp=None)
            

            description = f"Checkout for cart_id: {cart_id}"
            tag = "CHECKOUT"

            # SQL query to get cart items with listing information

            cart_items_info = connection.execute(sqlalchemy.text("""
                SELECT
                    cart_items.quantity AS quantity,
                    cart_items.listing_id AS listing_id,
                    listings.shop_id AS shop_id,
                    listings.price AS price
                FROM
                    cart_items
                JOIN
                    listings ON cart_items.listing_id = listings.listing_id
                WHERE
                    cart_items.cart_id = :cart_id"""), {"cart_id": cart_id}).fetchall()

            for row in cart_items_info:
                quantity, listing_id, shop_id, price = row
                balance = 0

                # Check if there is enough stock
                inventory = connection.execute(sqlalchemy.text("""
                    SELECT SUM(quantity) AS inventory
                    FROM shoe_inventory_ledger
                    WHERE shop_id = :shop_id AND listing_id = :listing_id"""), {"shop_id": shop_id, "listing_id": listing_id}).scalar()
                
                if inventory < quantity:
                    raise IntegrityError("Not enough stock for listing_id {}".format(listing_id), None, None)

                    #---
                transaction_id = connection.execute(sqlalchemy.text("""
                    INSERT INTO transactions (description, tag)
                    VALUES (:description, :tag) RETURNING id"""), {"description": description, "tag": tag}).scalar()

                # Update shoe inventory ledger
                connection.execute(sqlalchemy.text("""
                    INSERT INTO shoe_inventory_ledger (shop_id, listing_id, transaction_id, quantity)
                    VALUES (:shop_id, :listing_id, :transaction_id, :quantity)
                """), {"shop_id": shop_id, "listing_id": listing_id, "transaction_id": transaction_id, "quantity": -quantity})
     
                
                # retrieve sale_start
                saleInfo = connection.execute(sqlalchemy.text(
                    """
                        SELECT discount_counter, price_modifier, sale_start
                        FROM shops
                        WHERE shop_id = :shop_id
                    """
                ),
                                   [{
                                       "shop_id": shop_id
                                   }]
                )
                # identify if any listings in cart are from shops with sales
                    # count transations since sale's start date, compare to disCounter
                amtDiscounted = connection.execute(sqlalchemy.text(
                    """
                        SELECT
                            SUM(quantity)
                        FROM shoe_inventory_ledger
                        WHERE shop_id = :shop_id AND quantity < 0
                        AND DATEDIFF(created_at, :startTime) > 0
                    """
                ),
                                   [{
                                       "shop_id": shop_id,
                                       "startTime": saleInfo.sale_start
                                   }]
                                   ).scalar()
                if amtDiscounted < saleInfo.discount_counter:
                # if sale, check remaining discounted sales and compare to shoes
                    discPrice = price * saleInfo.price_modifier
                    discountsLeft =  saleInfo.discount_counter - amtDiscounted
                    
                    # 3 shoes to buy, 5 discounts left
                    if discountsLeft >= quantity:
                        balance += (quantity * discPrice)
                    # 5 shoes to but, 3 discounts left
                    else:
                        balance += (discountsLeft * discPrice)
                        balance += ((quantity - discountsLeft) * price)
                else:
                # reached if no active sale
                    balance += quantity * price
                
                balance = int(balance)
                
                # Update shop balance ledger
                connection.execute(sqlalchemy.text("""
                    INSERT INTO shop_balance_ledger (balance, shop_id)
                    VALUES (:balance, :shop_id)
                """), {"balance": balance, "shop_id": shop_id})
                
            
            connection.execute(sqlalchemy.text("""
                UPDATE carts
                SET active = :active
                WHERE cart_id = :cart_id"""), {"active": False, "cart_id": cart_id})
            
            return {"Cart checkout complete!"}
        
        except HTTPError as h:
            return h.msg
                    
        except Exception as e:
            connection.execute(sqlalchemy.text("""
                UPDATE carts
                SET active = :active
                WHERE cart_id = :cart_id"""), {"active": False, "cart_id": cart_id})
            return {"Error during checkout{}".format(str(e))}