from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["carts"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCart(BaseModel):
    user_id: int

@router.post("/creat_cart")
def create_cart(new_cart: NewCart):

    """ """
    with db.engine.begin() as connection:
            
            result = connection.execute(sqlalchemy.text("""INSERT INTO carts (user_id)
                                                            VALUES (:user_id)
                                                            RETURNING cart_id"""), {"user_id": new_cart.user_id})
            
            cart_id = result.scalar()

    print(" cart_id: ", cart_id)
    return {"cart_id": cart_id}


@router.post("/set_item_quantity")
def set_item_quantity(cart_id: int, listing_id: int, quantity: int):
    """Update DB to reflect adding a shoe to a specific cart"""
    with db.engine.begin() as connection:
            
            result = connection.execute(sqlalchemy.text("""INSERT INTO cart_items (listing_id, cart_id, quantity)
                                                            VALUES (:listing_id, :cart_id, :quantity)
                                                            """), {"listing_id": listing_id, "cart_id": cart_id, "quantity": quantity}) 
    return "OK"

@router.post("/checkout")
def checkout(cart_id: int):
    # have to update ledgers, create transaction,
    with db.engine.begin() as connection:
        description = f"Checkout for cart_id: {cart_id}"
        tag = "CHECKOUT"

        res = connection.execute(sqlalchemy.text("""INSERT INTO transactions (description, tag)
                                            VALUES (:description, :tag) RETURNING id"""),
                                            {"description": description, "tag": tag})
        
        transaction_id = res.fetchone()[0]

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

        connection.execute(sqlalchemy.text("""INSERT INTO shoe_inventory_ledger (shop_id, listing_id, transaction_id, quantity)
                                            VALUES (:shop_id, :listing_id, :transaction_id, :quantity)"""),
                                            {"shop_id": shop_id, "listing_id": listing_id, "transaction_id": transaction_id, "quantity": -quantity})

        connection.execute(sqlalchemy.text("""INSERT INTO shop_balance_ledger (balance, shop_id)
                                            VALUES (:balance, :shop_id)"""),
                                            {"balance": balance, "shop_id": shop_id})