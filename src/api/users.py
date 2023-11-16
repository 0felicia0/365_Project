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


@router.post("/{user_id}/get_account")
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
    