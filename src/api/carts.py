from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum
from urllib.error import HTTPError
# hi
router = APIRouter(
    prefix="/carts",
    tags=["carts"],
    dependencies=[Depends(auth.get_api_key)],
)

class filter_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/filters")
def filter(
    brand: str = "",
    size: int = "",
    color: str = "",
    style: str = "",
    min_price: int = 1,
    max_price: int = "",
    sort_order: filter_sort_order = filter_sort_order.desc,
):
    order_by = db.listings.c.price
    if sort_order== filter_sort_order.desc:
        order_by = order_by.desc()
    else:
        order_by = order_by.asc()

         
    res= (
        sqlalchemy.select(
                db.shoes.c.shoe_id,
                db.shoes.c.brand,
                db.shoes.c.color,
                db.shoes.c.style,
                db.shoes.c.transaction_id,
                db.listings.c.listing_id,
                db.listings.c.price,
                db.listings.c.size,
                db.shoe_inventory_ledger.c.quantity
        )
        .select_from(db.shoes
            .join(db.listings, db.shoes.c.shoe_id == db.listings.c.shoe_id)         
            .join(db.shoe_inventory_ledger, db.shoe_inventory_ledger.c.transaction_id == db.listings.c.transaction_id)
            
        )
        .where(db.listings.c.price>=min_price)
        .order_by(order_by)
    )
    
    if max_price != "":
        res = res.where(db.listings.c.price<=max_price)
    if brand != "":
        res = res.where(db.shoes.c.brand.ilike(f"%{brand}%"))
    if size != "":
        res = res.where(db.listings.c.size == size)
    if color != "":
        res = res.where(db.shoes.c.color.ilike(f"%{color}%"))
    if style != "":
        res = res.where(db.shoes.c.style.ilike(f"%{style}%"))

    ans = []
    with db.engine.connect() as conn:
        results = conn.execute(res)
        for row in results:
            result_item = {
                "listing_id": row.listing_id,
                "quantity": row.quantity,
                "price": row.price
            }
            ans.append(result_item)
    return ans


class NewCart(BaseModel):
    user_id: int

@router.post("/user_id/{user_id}/new_cart")
def create_cart(new_cart: NewCart):

    """ """            
    try:
        # plan: see if any active carts available
        #       if none, create cart, else return the active one

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
            else:
                cart_id = result.cart_id

    except Exception as e:
        print("Error occured during execution of create_cart: ", e)
    
    return {"cart_id": cart_id}


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

    except Exception as e:
        print("Error occured during execution of set_tem_quantity: ", e)

    return {"Item added to cart!"}

@router.post("/checkout")
def checkout(cart_id: int):
    # have to update ledgers, create transaction,
    with db.engine.begin() as connection:
        description = f"Checkout for cart_id: {cart_id}"
        tag = "CHECKOUT"


        res = connection.execute(sqlalchemy.text("""SELECT cart_items.quantity AS quantity, cart_items.listing_id AS listing_id
                                                  FROM cart_items WHERE cart_items.cart_id = :cart_id"""), {"cart_id": cart_id})
        first_row = res.first()
        quantity = first_row.quantity
        listing_id = first_row.listing_id

        res = connection.execute(sqlalchemy.text("""SELECT listings.shop_id AS shop_id, listings.price AS balance FROM listings JOIN cart_items 
                                                 ON listings.listing_id = cart_items.listing_id
                                                WHERE cart_items.listing_id = :listing_id"""), {"listing_id": listing_id})
        first_row = res.first()
        shop_id = first_row.shop_id
        balance = first_row.balance

        #check if there is enough stock
        res = connection.execute(sqlalchemy.text("""SELECT SUM(shoe_inventory_ledger.quantity) AS inventory
                                                  FROM shoe_inventory_ledger WHERE shop_id = :shop_id AND listing_id = :listing_id"""), 
                                                  {"shop_id": shop_id, "listing_id": listing_id})
        first_row = res.first()
        inventory = first_row.inventory

        if inventory >= quantity:
            res = connection.execute(sqlalchemy.text("""INSERT INTO transactions (description, tag)
                                            VALUES (:description, :tag) RETURNING id"""),
                                            {"description": description, "tag": tag})
        
            transaction_id = res.fetchone()[0]

            connection.execute(sqlalchemy.text("""INSERT INTO shoe_inventory_ledger (shop_id, listing_id, transaction_id, quantity)
                                            VALUES (:shop_id, :listing_id, :transaction_id, :quantity)"""),
                                            {"shop_id": shop_id, "listing_id": listing_id, "transaction_id": transaction_id, "quantity": -quantity})

            connection.execute(sqlalchemy.text("""INSERT INTO shop_balance_ledger (balance, shop_id)
                                            VALUES (:balance, :shop_id)"""),
                                            {"balance": balance, "shop_id": shop_id})
            
            return True
        
        return False