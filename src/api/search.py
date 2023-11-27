from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum
from urllib.error import HTTPError
# hi
router = APIRouter(
    prefix="/search",
    tags=["search"],
    dependencies=[Depends(auth.get_api_key)],
)

class filter_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

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

class genders(str, Enum):
    Youth = "Youth"
    Women = "Women"
    Men = "Men"
    Unisex = "Unisex"

class condition(str, Enum):
    new = "new"
    used = "used"

@router.get("/filter")
def filter(
    search_page: str = "",
    brand: str = "",
    gender: genders = "",
    size: int = "",
    color: colors = "",
    style: str = "",
    condition: condition = "",
    min_price: int = 1,
    max_price: int = "",
    sort_order: filter_sort_order = filter_sort_order.desc,
):
    order_by = db.listings.c.price
    if sort_order== filter_sort_order.desc:
        order_by = order_by.desc()
    else:
        order_by = order_by.asc()

    # quantity = (
    #     sqlalchemy.select(
    #         db.shoe_inventory_ledger.c.listing_id,
    #         sqlalchemy.sum(db.shoe_inventory_ledger.c.quantity)
    #     )
    #     .select_from(db.shoe_inventory_ledger)
    #     .group_by(db.shoe_inventory_ledger.c.listing_id)
    # )  

    

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
                db.listings.c.condition,
                sqlalchemy.literal_column("quantities.total_quantity").label("total_quantity"),  # Include total_quantity

        )
       .select_from(
        db.shoes
        .join(db.listings, db.shoes.c.shoe_id == db.listings.c.shoe_id)
        .join(
            (
                sqlalchemy.select(
                    db.shoe_inventory_ledger.c.listing_id,
                    sqlalchemy.func.sum(db.shoe_inventory_ledger.c.quantity).label("total_quantity")
                )
                .select_from(db.shoe_inventory_ledger)
                .group_by(db.shoe_inventory_ledger.c.listing_id)
                .having(sqlalchemy.func.sum(db.shoe_inventory_ledger.c.quantity) > 0)  # Filter for total_quantity > 0

            ).alias("quantities"),
            db.listings.c.listing_id == sqlalchemy.literal_column("quantities.listing_id")
        )
    )
    .where(db.listings.c.price >= min_price
   )
    .order_by(order_by)
    )
    
    if max_price != "":
        res = res.where(db.listings.c.price<=max_price)
    if brand != "":
        res = res.where(db.shoes.c.brand.ilike(f"%{brand}%"))
    if size != "":
        res = res.where(db.listings.c.size == size)
    if color != "":
        res = res.where(db.shoes.c.color == color)
    if style != "":
        res = res.where(db.shoes.c.style.ilike(f"%{style}%"))
    if gender != "":
        res = res.where(db.listings.c.gender == gender)
    if condition != "":
        res = res.where(db.listings.c.condition == condition)
     
    if search_page == "":
        search_page = 1
    else:
        search_page = int(search_page)
    
    page_range_upper = (search_page*5)+ 1
    page_range_lower = page_range_upper-5
    
    ans = []
    with db.engine.connect() as conn:
        results = conn.execute(res)
        
        i = 1

        for row in results:
            if i>=page_range_lower and i<page_range_upper:
                result_item = {
                    "listing_id": row.listing_id,
                    "quantity": row.total_quantity,
                    "price": row.price

                }
                ans.append(result_item)
            i = i+1
    return ans

# @router.get("/filters")
# def filter(
#     brand: str = "",
#     size: int = "",
#     color: str = "",
#     style: str = "",
#     min_price: int = 1,
#     max_price: int = "",
#     gender: str = "",
#     condition: str = "",
#     sort_order: filter_sort_order = filter_sort_order.desc,
# ):
#     print('helpppp')
    
#     # quantities = (
#     #     sqlalchemy.select([
#     #         db.shoe_inventory_ledger.c.id
#     #     ])
#     #     .select_from(
#     #         db.shoe_inventory_ledger
#     #     )
#     #     .group_by(db.shoe_inventory_ledger.c.listing_id)
#     # )

#     order_by = db.listings.c.price
#     if sort_order == filter_sort_order.desc:
#         order_by = order_by.desc()
#     else:
#         order_by = order_by.asc()

#     res = (
#         sqlalchemy.select([
#             db.shoes.c.shoe_id,
#             db.shoes.c.brand,
#             db.shoes.c.color,
#             db.shoes.c.style,
#             db.shoes.c.transaction_id,
#             db.listings.c.listing_id,
#             db.listings.c.price,
#             db.listings.c.size,
#             #$quantities.c.quantity,
#             db.listings.c.condition,
#             db.listings.c.gender
#         ])
#         .select_from(
#             db.shoes
#             .join(db.listings, db.shoes.c.shoe_id == db.listings.c.shoe_id)
#             #.join(quantities, quantities.c.listing_id == db.listings.c.listing_id)
#         )
#         .where(db.listings.c.price >= min_price)
#         .order_by(order_by)
#     )
    
#     if max_price != "":
#         res = res.where(db.listings.c.price <= max_price)
#     if brand != "":
#         res = res.where(db.shoes.c.brand.ilike(f"%{brand}%"))
#     if size != "":
#         res = res.where(db.listings.c.size == size)
#     if color != "":
#         res = res.where(db.shoes.c.color.ilike(f"%{color}%"))
#     if style != "":
#         res = res.where(db.shoes.c.style.ilike(f"%{style}%"))
#     if gender != "":
#         res = res.where(db.listings.c.gender.ilike(f"%{gender}%"))
#     if condition != "":
#         res = res.where(db.listings.c.condition.ilike(f"%{condition}%"))

#     ans = []
#     with db.engine.connect() as conn:
#         results = conn.execute(res)
#         for row in results:
#             result_item = {
#                 "listing_id": row.listing_id,
#                 "quantity": row.quantity,
#                 "price": row.price
#             }
#             ans.append(result_item)
#         return ans