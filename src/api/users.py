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
    #       potential upgrade -> restrict password in a certain way
    #       ENCRYPT PASSWORD!!!!! 

    try:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT user_id, email
                                                        FROM users
                                                        WHERE email = :email
                                                        """)
                                                        , {"email": new_account.email}).first()

            # if the account exists, return message indicating so, otherwise make an account
            if result is None:
                # create new account because email not already in the DB
                # encrypt password
                user_id = connection.execute(sqlalchemy.text("""
                                                    INSERT INTO users (name, email, password)
                                                    VALUES(:name, :email, :password)
                                                    RETURNING user_id
                                                    """
                                                ),
                                                [{"name": new_account.name, "email": new_account.email, "password": new_account.password}]).scalar()
                return {"user_id": user_id}

            else:
                raise HTTPError(url=None, code=400, msg="Account already exists with given email. Try a different email, or login with existing account.", hdrs={}, fp=None)
        
    except Exception as e:
        return e.msg 


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

    except Exception as e:
        return e.msg


@router.put("/change_password")
def change_password(email: str, password: str, new_password: str):
    # plan: take in email and password to ensure it is the right user
    #       replace the password
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

    except Exception as e:
        return e.msg


@router.put("/change_email")
def change_email(email: str, password: str, new_email: str):
    # plan: take in email and password to ensure it is the right user
    #       replace the password
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

    except Exception as e:
        return e.msg


# @router.put("/change_account_details")
# def change_account_details(email: str, password: str, new_password: str = "", new_email: str = "", new_name: str = ""):
#     # plan: take in email and password to ensure it is the right user
#     #       replace the information with the new stuff
#     #       ask how the change account details is typically done -> individual endpoints, or all in one go
#     try:
#         with db.engine.begin() as connection:
#             result = connection.execute(sqlalchemy.text("""
#                                                         SELECT users.name, users.email, users.password
#                                                         FROM users
#                                                         WHERE users.email = :email AND users.password = :password
#                                                         """)
#                                                         , {"email": email, "password": password}).first()
#             if result is None:
#                 raise HTTPError(url=None, code=400, msg="Wrong email and/or password. Try again with proper credentials.", hdrs={}, fp=None)
            
#             if result.password == new_password:
#                 raise HTTPError(url=None, code=400, msg="New password cannot be existing password. Try again.", hdrs={}, fp=None)
#             if result.email == new_email:
#                 raise HTTPError(url=None, code=400, msg="New email cannot be existing email. Try again.", hdrs={}, fp=None)
#             if result.name == name:
#                 raise HTTPError(url=None, code=400, msg="New name cannot be existing name. Try again.", hdrs={}, fp=None)

#             # update password
#             connection.execute(sqlalchemy.text("""
#                                                 UPDATE users
#                                                 SET password = :new_password
#                                                 WHERE users.email = :email AND users.password = :password
#                                                 """)
#                                                 , {"email": email, "password": password, "new_password": new_password})
            
#             return{"Password successfully changed!"}

#     except Exception as e:
#         return e.msg