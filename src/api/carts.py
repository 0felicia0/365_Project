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

@router.post("/")
def create_cart(new_cart: NewCart):

    """ """
    with db.engine.begin() as connection:
            
            result = connection.execute(sqlalchemy.text("""INSERT INTO carts (user_id)
                                                            VALUES (:user_id)
                                                            RETURNING id"""), {"name": new_cart.user_id})
            
            cart_id = result.scalar()

    print(" cart_id: ", cart_id)
    return {"cart_id": cart_id}


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, listing_id: int, quantity: int):
    """Update DB to reflect adding a shoe to a specific cart"""
    with db.engine.begin() as connection:
            
            result = connection.execute(sqlalchemy.text("""INSERT INTO cart_items (listing_id, cart_id, quantity)
                                                            VALUES (:listing_id, :cart_id, :quantity)
                                                            """), {"listing_id": listing_id, "cart_id": cart_id, "quantity": quantity}) 
    return "OK"

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    # have to update ledgers, create transaction,

  
        
        
    pass