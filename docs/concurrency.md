# Concurrency 

## 1. Shops/create_listing

Create_listing poses potential concurrency concerns. In our database schema, shoe information is stored for each unique shoe. 
If a shoe does not yet exist, it is added to the database and a listing is made using the shoe_id. This creates an issue as two shops could
potentially create a listing for identical shoes at the same time, resulting in a shoe being in the database twice rather than once.
We protect against this issue by having our read and write in one SQL statement. So, when we check if something is already in the database
we are executing the write feature in that statment. We achieved this using ON CONFLICT to determine whether or not we will be writing. 

![image](https://github.com/0felicia0/Shoetopia/assets/97004682/38bcd26a-0185-4a4c-aee7-3fb12c0b0f9c)

## 2. Checkout

Explain the process of checking out, any relevant details, and steps involved.

## 3. Users/Create_account

Another area of potential concurrency issues is create_account. In the rare case where two people are trying to create an account using the 
same email at the same exact time, there could be a case where T1 made an account first but T2 read that the email wasn't yet used and overrides
T1. This problem is accounted for using ON CONFLICT. By using this we can read and write in one transaction rather than splitting this up into
two sql queries. This is an example of the lost update phenomena. 

![image](https://github.com/0felicia0/Shoetopia/assets/97004682/0a7dd1d9-b596-440f-98cb-3747a710d452)
