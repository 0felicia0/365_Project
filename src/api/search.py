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
    black = "black"
    grey = "grey"
    white = "white"
    ivory = "ivory"
    beige = "beige"
    brown = "brown"
    metallic = "metallic"
    purple = "purple"
    blue = "blue"
    green = "green"
    yellow = "yellow"
    orange = "orange"
    pink = "pink"
    red = "red"
    burgundy = "burgundy"
    other = "other"

class genders(str, Enum):
    youth = "youth"
    women = "women"
    men = "men"
    unisex = "unisex"


class condition(str, Enum):
    new = "new"
    used = "used"
class verification_filter(str, Enum):
    verified = "verified"

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
    price_order: filter_sort_order = "",
    verification: verification_filter = "",
    #price_order: filter_sort_order = filter_sort_order.desc,

    shop_id: str = ""
):
    brand = brand.lower()
    style = style.lower()
    #promoted shoes should always be at the beg of the search
    #if by price, promoted still first within its price range

    if price_order == "":
        order_by1 = db.shops.c.promotion_tier.desc()
        order_by2 = db.listings.c.price.desc()
    else:
        if price_order== filter_sort_order.desc:
            order_by1 = db.listings.c.price.desc()

        else:
            order_by1 = db.listings.c.price.asc()
        order_by2 = db.shops.c.promotion_tier.desc()
   
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
                db.listings.c.gender,
                db.listings.c.shop_id,
                db.shops.c.promotion_tier,
                db.shops.c.verified,
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
        .join(db.shops, db.shops.c.shop_id == db.listings.c.shop_id)
    )
    .where(db.listings.c.price >= min_price
   )
    .order_by(order_by1, order_by2)
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
    if shop_id != "":
        res = res.where(db.listings.c.shop_id == shop_id)
    if verification != "":
        res = res.where(db.shops.c.verified == 'TRUE' )
   
   
    if search_page == "":
        search_page = 1
    else:
        search_page = int(search_page)
   
    page_range_upper = (search_page*5)+ 1
    page_range_lower = page_range_upper-5
   
    ans = []
    try:
        with db.engine.connect() as conn:
            results = conn.execute(res)
           
            i = 1

            for row in results:
                if i>=page_range_lower and i<page_range_upper:
                    result_item = {
                        "listing_id": row.listing_id,
                        "price": row.price / 100,
                        "brand": row.brand,
                        "gender": row.gender,
                        "size": row.size,
                        "color": row.color,
                        "style": row.style,
                        "condition": row.condition,
                        "shop id": row.shop_id,
                        "is verified": row.verified                      

                    }
                    ans.append(result_item)
                i = i+1
    except HTTPError as h:
        return h.msg

    except Exception as e:
        print("Error in search: ", e)

    if ans == [] and search_page==1:
        return "no results, please modify your search"
    elif ans == []:
        return "no results on this page"
    return ans

@router.get("/compare")
def compare(listing1: int, listing2:int):
    try:
       
        #add checking that both listings exist
        with db.engine.begin() as connection:
            listing1_info = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT price, size, condition, gender, listings.shop_id as shop_id, brand, color, style, verified, listings.listing_id as listing_id
                    FROM listings
                    JOIN shoes on listings.shoe_id = shoes.shoe_id
                    JOIN shops on shops.shop_id = listings.shop_id
                    WHERE listings.listing_id = :listing1
                    """
                ),
                [{"listing1": listing1}]
            ).fetchone()
           
            if listing1_info is None:
                raise ValueError("No results for listing1. Try Again.")

            listing2_info = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT price, size, condition, gender, listings.shop_id as shop_id, brand, color, style, verified, listings.listing_id as listing_id
                    FROM listings
                    JOIN shoes on listings.shoe_id = shoes.shoe_id
                    JOIN shops on shops.shop_id = listings.shop_id
                    WHERE listings.listing_id = :listing2
                    """
                ),
                [{"listing2": listing2}]
            ).fetchone()
            if listing2_info is None:
                raise ValueError("No results for listing2. Try Again.")

        #then need to make a message
            ans = []
            ans.append({
                            "listing_id": listing1_info.listing_id,
                            "price": listing1_info.price / 100,
                            "brand": listing1_info.brand,
                            "gender": listing1_info.gender,
                            "size": listing1_info.size,
                            "color": listing1_info.color,
                            "style": listing1_info.style,
                            "condition": listing1_info.condition,
                            "shop id": listing1_info.shop_id,
                            "is verified": listing1_info.verified                      

                        })
            ans.append({
                            "listing_id": listing2_info.listing_id,
                            "price": listing2_info.price / 100,
                            "brand": listing2_info.brand,
                            "gender": listing2_info.gender,
                            "size": listing2_info.size,
                            "color": listing2_info.color,
                            "style": listing2_info.style,
                            "condition": listing2_info.condition,
                            "shop id": listing2_info.shop_id,
                            "is verified": listing2_info.verified                      

                        })
        return ans
    except HTTPError as h:
        return h.msg

    except Exception as e:
        print("Error creating listing: ", e)