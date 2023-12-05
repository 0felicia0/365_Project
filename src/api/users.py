from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from urllib.error import HTTPError

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewAccount(BaseModel):
    name: str
    email: str
    password: str
   
@router.post("/create_account")
def create_account(new_account: NewAccount):
    # plan: check if account already exists with the email bc emails are generally unique
    #       if so, raise error that account already exists
    #       else, create the account
    #       potential upgrade -> restrict password in a certain way (maybe)
    #       try on conflict to minimize code
    new_account.email = new_account.email.lower()
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                INSERT INTO users (name, email, password)
                VALUES (:name, :email, :password)
                ON CONFLICT (email) DO NOTHING
                RETURNING user_id
            """),
            {"name": new_account.name, "email": new_account.email, "password": new_account.password}).first()

            if result is not None:
                return {"user_id": result.user_id}
            else:
                raise HTTPError(
                    url=None,
                    code=400,
                    msg="Account already exists with given email. Try a different email, or login with an existing account.",
                    hdrs={},
                    fp=None
                )
    except HTTPError as h:
        return h.msg

    except Exception as e:
         print("Error in the process of creating account: ", e)


@router.get("/{user_id}/get_account")
def get_account(user_id: int):
    # plan: take in user id and check to see if it exists
    #       if exists, return email and name
    #       beneficial for something like forgot email/username
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT users.name, users.email
                                                        FROM users
                                                        WHERE users.user_id = :user_id
                                                        """)
                                                        , {"user_id": user_id}).first()
            if result is None:
                raise HTTPError(url=None, code=400, msg="Account does not exist with given user_id. Try again with a different user_id.", hdrs={}, fp=None)
            
            return{"Name": result.name, "Email": result.email}

    except HTTPError as h:
        return h.msg

    except Exception as e:
         print("Error in the process of getting account: ", e)


@router.put("/change_password")
def change_password(email: str, password: str, new_password: str):
    # plan: take in email and password to ensure it is the right user
    #       replace the password
    email = email.lower()
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT users.name, users.email, users.password
                                                        FROM users
                                                        WHERE users.email = :email AND users.password = :password
                                                        """)
                                                        , {"email": email, "password": password}).first()
            if result is None:
                raise HTTPError(url=None, code=400, msg="Wrong email and/or password. Try again with proper credentials.", hdrs={}, fp=None)
            
            if result.password == new_password:
                raise HTTPError(url=None, code=400, msg="New password cannot be existing password. Try again.", hdrs={}, fp=None)

            # update password
            connection.execute(sqlalchemy.text("""
                                                UPDATE users
                                                SET password = :new_password
                                                WHERE users.email = :email AND users.password = :password
                                                """)
                                                , {"email": email, "password": password, "new_password": new_password})
            
            return{"Password successfully changed!"}

    except HTTPError as h:
        return h.msg

    except Exception as e:
        print("Error in the process of changing password: ", e)


@router.put("/change_email")
def change_email(email: str, password: str, new_email: str):
    # plan: take in email and password to ensure it is the right user
    #       replace the password
    email = email.lower()
    new_email = email.lower()
    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT users.name, users.email, users.password
                                                        FROM users
                                                        WHERE users.email = :email AND users.password = :password
                                                        """)
                                                        , {"email": email, "password": password}).first()
            if result is None:
                raise HTTPError(url=None, code=400, msg="Wrong email and/or password. Try again with proper credentials.", hdrs={}, fp=None)
            
            if result.email == new_email:
                raise HTTPError(url=None, code=400, msg="New email cannot be existing email. Try again.", hdrs={}, fp=None)

            # update password
            connection.execute(sqlalchemy.text("""
                                                UPDATE users
                                                SET email = :new_email
                                                WHERE users.email = :email AND users.password = :password
                                                """)
                                                , {"email": email, "password": password, "new_email": new_email})
            
            return{"Email successfully changed!"}

    except HTTPError as h:
        return h.msg

    except Exception as e:
         print("Error in the process of changing password: ", e)
         
@router.post("/submit_review")
def submit_review(user_id: int, shop_id: int, rating: int):
    try:
        with db.engine.begin() as connection:
        # check valid user
            result = connection.execute(sqlalchemy.text("""
                                                    SELECT user_id
                                                    FROM users
                                                    WHERE user_id = :user_id
                                                    """)
                                                    , {"user_id": user_id}).first()
            if result is None:
                raise Exception("User does not exist. Try with a valid user to post a review.")
        # check valid shop
            result = connection.execute(sqlalchemy.text("""
                                                    SELECT shop_id
                                                    FROM shops
                                                    WHERE shop_id = :shop_id
                                                    """)
                                                    , {"shop_id": shop_id}).first()
            if result is None:
                raise Exception("Shop does not exist to post a rating. Try again with a valid shop.")
        # check valid rating
            if rating < 1 or rating > 5:
                raise Exception("Invalid rating value. Must be an integer 1 through 5")
            
        # # check that user bought from the certain shop
        #     records = connection.execute(sqlalchemy.text("""
        #                                             SELECT carts.user_id, shop_inventory_ledger.shop_id
        #                                             FROM cart_items
        #                                             LEFT JOIN carts on carts.cart_id = cart_items.id
        #                                             LEFT JOIN listings on listings.listing_id = cart_items.listing_id
        #                                             LEFT JOIN shop_inventory_ledger on shop_inventory_ledger.shop_id = listings.shop_id
        #                                             WHERE carts.user_id = :user_id AND shop_inventory_ledger.shop_id = :shop_id
        #                                             """),
        #                                  [{
        #                                      "user_id": user_id,
        #                                      "shop_id": shop_id
        #                                  }])
        #     if records is None:
                
        # post review
            connection.execute(sqlalchemy.text("""
                            INSERT INTO shop_rating_ledger (shop_id, user_id, rating)
                            VALUES (:shop_id, :user_id, :rating)
                               """), [{
                                   "shop_id": shop_id,
                                   "user_id": user_id,
                                   "rating": rating
                               }])
            
            return ("Submitted rating of %d for shop id %d." % (rating, shop_id))
        
    except Exception as e:
        return {f"Error in posting a review: {e}"}