import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np
from urllib.error import HTTPError
from sqlalchemy.exc import IntegrityError

def database_connection_url():
    dotenv.load_dotenv()
    return os.environ.get("POSTGRES_URI")

def create_users(num_users):
    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

    fake = Faker()
    with engine.begin() as conn:
        print("creating fake users...")
        for i in range(num_users):
        
            name = fake.first_name()
            email = fake.unique.email()
            password = fake.unique.password(length=5)
            

            poster_id = conn.execute(sqlalchemy.text(
                """
                INSERT INTO users (name, email, password) 
                VALUES (:name, :email, :password) RETURNING user_id;
                """
            ), {"name": name, "email": email, "password": password }).scalar_one();

def create_shops(num_shops):

    # Create a new DB engine based on our connection string
    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

    with engine.begin() as conn:   
        
        fake = Faker()

        print("creating fake shops...")
        for i in range(1,num_shops+1):    
            #print(i)
            
            account = conn.execute(sqlalchemy.text("""
                SELECT users.name
                FROM users
                WHERE users.user_id = :user_id
                """), {"user_id": i}).first()
            if account is None:
                raise ValueError("Account does not exist. Cannot create a shop.") 
                
                # check if user already has a shop
            result = conn.execute(sqlalchemy.text("""
                    SELECT shops.user_id
                    FROM shops
                    WHERE shops.user_id = :user_id
                    """), {"user_id": i}).first()

            # if account already has a shop, they cannot have another one
            if result is not None:
                raise ValueError("A shop already exists with the account. Cannot have more than one shop active.")
            #store_name = fake.company()
            
            is_unique = True
            while is_unique:
                store_name = fake.company()
                # Check if the store_name already exists in the database
                result = conn.execute(
                    sqlalchemy.text(
                        """
                        SELECT 1
                        FROM shops
                        WHERE store_name = :store_name
                        """
                    ),
                    {"store_name": store_name}
                ).first()

                if result is None:
                    is_unique = False

            shop_id = conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO shops (user_id, store_name)
                    VALUES(:user_id, :store_name)
                    RETURNING shop_id
                    """
                ),
                [{"user_id": i, "store_name": store_name}]
            ).scalar_one_or_none()
def create_listings(num_shops, num_listings):
    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)
    with engine.begin() as conn:   
        
        fake = Faker()
        print("creating fake shoes/listings...")
        for i in range(num_listings):
            shop_id = fake.random_int(1, num_shops)
            quantity = fake.random_int(1, 25)
            price = fake.random_int(5,60)*10
            size = fake.random_element(elements = [4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11])
            color = fake.random_element(elements = (
                "Black",
                "Grey",
                "White",
                "Ivory",
                "Beige",
                "Brown",
                "Metallic",
                "Purple",
                "Blue",
                "Green",
                "Yellow",
                "Orange",
                "Pink",
                "Red",
                "Burgundy",
                "Other"))
            
            brand = fake.random_element(elements = (
                'Nike', 'Adidas', 'Puma', 'Reebok', 'New Balance',
                'Under Armour', 'Converse', 'Vans', 'ASICS', 'Skechers',
                'Salomon', 'Brooks', 'Merrell', 'Mizuno', 'Fila',
                'Lacoste', 'Ecco', 'Clarks', 'Timberland', 'Doc Martens',
                'Saucony', 'Hoka One One', 'Columbia', 'On Running', 'Keen',
                'Birkenstock', 'Bally', 'Balenciaga', 'Gucci', 'Prada',
                'Versace', 'Fendi', 'Yeezy', 'Jordan', 'Balmain',
                'Vetements', 'Off-White', 'Common Projects', 'Vivobarefoot', 'Hush Puppies',
                'Sperry', 'Dr. Scholl\'s', 'UGG', 'Crocs', 'Steve Madden',
                'Merrell', 'Sorel', 'Cole Haan', 'Diadora', 'K-Swiss', 'Crocs'
            ))

            style = fake.random_element(elements =  (
                'Low Top Runner', 'High Top Basketball', 'Casual Slip-On', 'Sporty Sandal', 'Fashion Sneaker',
                'Athletic Trainer', 'Classic Loafer', 'Hiking Boot', 'Canvas Skate Shoe', 'Formal Oxford',
                'Slip-Resistant Work Boot', 'Urban Streetwear', 'Leather Chelsea Boot', 'Trail Hiker', 'Minimalist Sneaker',
                'Retro Jogger', 'High Fashion Heel', 'Platform Sandal', 'Running Shoe with Arch Support', 'Dressy Mule', 'Velcro'
            ))

            gender = fake.random_element(elements = ("Youth", "Women", "Men", "Unisex"))

            condition = fake.random_element(elements = ('new', 'used'))
            #print(shop_id, quantity, price, size, color, brand, style, gender, condition )
            #with db.engine.connect().execution_options(isolation_level="Serializable") as connection:
                #create a new transaction
                
            description = "shoe uploaded: " + color + ",  " + brand + ", " + style
            transaction_id = conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO transactions (description, tag)
                    VALUES(:description, 'LISTING')
                    RETURNING id
                    """
                ),
                [{"description": description}])
            transaction_id = transaction_id.first()[0]
                    
            shoe_id = conn.execute(
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
                [{"brand": brand, "color": color, "style": style, "transaction_id": transaction_id}]
            ).fetchone()[0]
                
            #insert listing into table
            listing_id = conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO listings (shop_id, shoe_id, price, size, transaction_id, gender, condition)
                    VALUES (:shop_id, :shoe_id, :price, :size, :transaction_id, :gender, :condition)
                    RETURNING listing_id
                    """    
                ),
                [{"shop_id": shop_id, "shoe_id": shoe_id, "price": price, "size": size, "transaction_id": transaction_id, "gender": gender, "condition" : condition}]
            )
            listing_id = listing_id.fetchone()[0]
            
            #update shoe_inventory ledger
            conn.execute(
                sqlalchemy.text(
                    """
                    INSERT into shoe_inventory_ledger(shop_id, listing_id, transaction_id, quantity)
                    VALUES (:shop_id, :listing_id, :transaction_id, :quantity )
                    """
                ),
                [{"shop_id": shop_id, "listing_id": listing_id, "transaction_id": transaction_id, "quantity": quantity}]
            )


def create_cart(user_id):
    
    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

    """ """            
    try:
        # plan: see if any active carts available
        #       if none, create cart, else return the active one
        # see if other exceptions have a message field, can cause issues if not -> update the exception block

        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT cart_id, user_id, active
                                                        FROM carts
                                                        WHERE active = TRUE AND user_id = :user_id
                                                        """), 
                                                        {"user_id": user_id}).first()

            if result is None:
                #print("No active cart with user_id:", user_id, "| Creating new cart.")
                cart_id = connection.execute(sqlalchemy.text("""
                                                            INSERT INTO carts (user_id, active)
                                                            VALUES (:user_id, TRUE)
                                                            RETURNING cart_id;"""), 
                                                            {"user_id": user_id}).scalar()
                return {"cart_id": cart_id}
            
            raise HTTPError(url=None, code=400, msg="Cart already active with given user_id. Checkout before activating another cart.", hdrs={}, fp=None)

    except HTTPError as e:
        return e.msg

    except Exception as e:
        print("Error in the process of creating a new cart: ", e)
def get_cart(user_id: int):

    """ """            
    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

    try:
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT cart_id
                                                        FROM carts
                                                        WHERE active = TRUE AND user_id = :user_id
                                                        """), 
                                                        {"user_id": user_id}).first()

            if result is not None:
                return result.cart_id
            
            raise HTTPError(url=None, code=400, msg="No active cart found with given user_id.", hdrs={}, fp=None)

    except HTTPError as e:
        return e.msg
    
    except Exception as e:
        print("Error in the process of getting an active/existing cart: ", e)
def set_item_quantity(cart_id: int, listing_id: int, quantity: int):
    """Update DB to reflect adding a shoe to a specific cart"""

    # make sure cart is active, listing exists, and enough quantity available
    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

    try:
        with engine.begin() as connection:
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
def checkout(cart_id: int):
    print("creating fake checkouts...")
 # have to update ledgers, create transaction,
    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

    with engine.begin() as connection:

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
                
                # retrieve sale_start
                saleInfo = connection.execute(sqlalchemy.text(
                    """
                        SELECT 
                            discount_counter,
                            price_percentage,
                            EXTRACT(epoch FROM sale_start)::int startTime
                        FROM shops
                        WHERE shop_id = :shop_id
                    """
                ),
                                   [{
                                       "shop_id": shop_id
                                   }]
                ).first()
                # identify if any listings in cart are from shops with active sales
                    # count shoes sold since sale's start date, compare to disCounter
                amtDiscounted = connection.execute(sqlalchemy.text(
                    """
                        SELECT
                            SUM(quantity) as amtDiscounted
                        FROM shoe_inventory_ledger
                        WHERE shop_id = :shop_id AND quantity < 0
                        AND (EXTRACT(epoch FROM created_at)::int - :startTime) > 0
                    """
                ),
                                   [{
                                       "shop_id": shop_id,
                                       "startTime": saleInfo[2]
                                   }]
                                   ).scalar()
                if amtDiscounted is None:
                    amtDiscounted = 0
                amtDiscounted = abs(amtDiscounted)
                if amtDiscounted < saleInfo.discount_counter:
                # if sale, check remaining discounted sales and compare to shoes
                    discPrice = price * saleInfo.price_percentage / 100
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

def create_checkouts(num_checkouts, num_listings):

    engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)
    with engine.begin() as conn:   
        for i in range(num_checkouts):   
            fake = Faker()
            user_id = fake.random_int(min=1, max = 5)
            listing_id = fake.random_int(min=1, max = num_listings)
            quantity = fake.random_int(min = 1, max = 5)
            create_cart(user_id)
            cart_id = get_cart(user_id)
            #print(cart_id)
            set_item_quantity(cart_id, listing_id, quantity)
            checkout(cart_id)
#modify the values according to how many rows you want to create:
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
   
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS carts CASCADE;
    DROP TABLE IF EXISTS cart_items CASCADE;
    DROP TABLE IF EXISTS shoes CASCADE;                             
    DROP TABLE IF EXISTS listings CASCADE; 
    DROP TABLE IF EXISTS shoe_inventory_ledger CASCADE;
    DROP TABLE IF EXISTS shops CASCADE;
    DROP TABLE IF EXISTS shop_balance_ledger CASCADE;
    DROP TABLE IF EXISTS transactions CASCADE;

    create table
    public.users (
        user_id bigint generated by default as identity,
        name text not null,
        email text not null,
        password text not null,
        created_at timestamp with time zone not null default now(),
        constraint users_pkey primary key (user_id),
        constraint users_email_key unique (email),
        constraint users_password_key unique (password)
    ) tablespace pg_default;

    create table
    public.shops (
        shop_id bigint generated by default as identity,
        user_id bigint not null,
        store_name text not null,
        created_at timestamp with time zone not null default now(),
        verified boolean not null default false,
        discount_counter integer not null default 0,
        sale_start timestamp with time zone not null default now(),
        price_percentage integer not null default 100,
        promotion_tier integer not null default 0,
        constraint shops_pkey primary key (shop_id),
        constraint shops_seller_id_key unique (user_id),
        constraint shops_shop_id_key unique (shop_id),
        constraint shops_store_name_key unique (store_name),
        constraint shops_price_percentage_check check ((price_percentage <= 100))
    ) tablespace pg_default; 

    create table
    public.transactions (
        id bigint generated by default as identity,
        created_at timestamp with time zone not null default now(),
        description text null,
        tag text not null,
        constraint transactions_pkey primary key (id)
    ) tablespace pg_default;
                                 
    create table
    public.shoes (
        shoe_id bigint generated by default as identity,
        brand text not null,
        color text not null,
        style text not null,
        created_at timestamp with time zone not null default now(),
        transaction_id bigint not null,
        primary key (shoe_id),
        constraint unique_brand_color_style unique (brand, color, style),
        constraint shoes_transaction_id_fkey foreign key (transaction_id) references transactions (id)
    ) tablespace pg_default;
                                 
    create table
    public.listings (
        listing_id bigint generated by default as identity,
        shop_id bigint not null,
        shoe_id bigint not null,
        price bigint not null,
        created_at timestamp with time zone not null default now(),
        size integer not null,
        transaction_id bigint not null,
        condition text not null,
        gender text not null,
        constraint listings_pkey primary key (listing_id),
        constraint listings_shoe_id_fkey foreign key (shoe_id) references shoes (shoe_id),
        constraint listings_shop_id_fkey foreign key (shop_id) references shops (shop_id),
        constraint listings_transaction_id_fkey foreign key (transaction_id) references transactions (id)
    ) tablespace pg_default;

    create table
    public.shoe_inventory_ledger (
        id bigint generated by default as identity,
        created_at timestamp with time zone not null default now(),
        quantity integer not null,
        shop_id bigint not null,
        listing_id bigint not null,
        transaction_id bigint not null,
        constraint shoe_inventory_ledger_pkey primary key (id),
        constraint shoe_inventory_ledger_listing_id_fkey foreign key (listing_id) references listings (listing_id),
        constraint shoe_inventory_ledger_shop_id_fkey foreign key (shop_id) references shops (shop_id),
        constraint shoe_inventory_ledger_transaction_id_fkey foreign key (transaction_id) references transactions (id)
    ) tablespace pg_default;

    create table
    public.shop_balance_ledger (
        id bigint generated by default as identity,
        created_at timestamp with time zone not null default now(),
        balance bigint not null,
        shop_id bigint not null,
        constraint shop_balance_ledger_pkey primary key (id),
        constraint shop_balance_ledger_shop_id_fkey foreign key (shop_id) references shops (shop_id)
    ) tablespace pg_default;                                                                                      

    create table
    public.carts (
        cart_id bigint generated by default as identity,
        created_at timestamp with time zone not null default now(),
        user_id bigint not null,
        active boolean not null,
        constraint carts_pkey primary key (cart_id),
        constraint carts_user_id_fkey foreign key (user_id) references users (user_id)
    ) tablespace pg_default;
                                 
    create table
    public.cart_items (
        id bigint generated by default as identity,
        created_at timestamp with time zone not null default now(),
        listing_id bigint not null,
        cart_id bigint not null,
        quantity integer not null,
        constraint cart_items_pkey primary key (id)
    ) tablespace pg_default;
  """))                            
num_users = 200000
num_shops = 100000
num_listings = 200000
num_checkouts = 5000

create_users(num_users)
create_shops(num_shops)
create_listings(num_shops, num_listings)
create_checkouts(num_checkouts, num_listings)