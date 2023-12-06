# Performance Writeup

## 1. Fake Data Modeling
Link to the file used to construct the rows of fake data: https://github.com/0felicia0/Shoetopia/blob/main/src/populate.py 
Rows per table:
- cart_items: 4575
- carts: 5007
- listings: 200003
- shoe_inventory_ledger: 204588
- shoes: 16465
- shop_balance_ledger: 100003
- shops: 100001
- transactions: 204577
- users: 200001

- total rows: 1,009,994

- In creating this distribution we decided that a bulk of our data would be in our transactions table because numerous endpoints require an operation to be logged in the transactions ledger.
- Our users are also a bulk of our rows (about 20%), and half of our users have a shop correlated with their account.
- The main builk of our data was in shoes and listings as we expect each shop will have many listings, and the bulk of time will be spent browsing the vast catalog of shoes.
- We then had a smaller percentage of checkouts because we estimated that out of the pool of users only a small group from that pool would make it through the full checkout process.  Having completed this analysis we agree it would be worth investigating the runtimes when carts were doubled as there could be many active carts at any given time.
  

## 2. Performance results of hitting endpoints
Endpoint Performance (in ms):
- create_shop - 15, 11, 8
- purchase_promotion_tier - 13, 14, 13
- create_listing - 23, 15, 11
- **post_application - 47, 38, 41 (slowest)**
- update_verification - 13, 10, 8
- verification_status - 9, 10, 7
- start_flash_sale - 35, 39, 33
- new_cart - 16, 13, 15
- get_cart - 8, 10, 7
- set_item_quantity - 25
- **checkout - 43, 49, 32 (slowest)**
- create_account - 9, 13, 10
- get_account - 10, 7, 6
- change_password - 12, 11, 14
- change_email - 15, 12, 14
- submit_review - 12, 13, 11
- **filter - 330 (slowest)**
- view_ratings - 9, 8, 8 
- compare - 9, 16, 10

**From this, we concluded that our slowest endpoints were:**
- post_application
- checkout
- filter

## 3. Performance tuning

### 1. Post Application

**Query #1:**
<img width="1203" alt="Screenshot 2023-12-05 at 11 31 32 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/1aae7e16-e278-4670-9b63-88993d5684f1">

- Explanation of Query Plan: 
	- The query aggregates the shop_rating_ledger by shop_id, then scans through the grouped rows to find the appropriate shop_id. An index on the shop_id in the shop_rating_ledger used in the where and group by statements should improve the performance.

- Index to Add
	- CREATE INDEX ON shop_rating_ledger(shop_id)

- Indexed Query Plan
<img width="1205" alt="Screenshot 2023-12-05 at 11 37 58 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/d25e3261-7f94-42cc-810b-97d22240b33b">


- Explanation of Indexed Query Plan
	- The query aggregates the shop_rating_ledger by shop_id, then scans through the bitmap of indexes to find the appropriate shop_id.

- Expected Performance Boost:
	- YES

**Query #2:**
<img width="1200" alt="Screenshot 2023-12-05 at 11 32 40 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/eb5dc67a-5e92-4ce7-9931-314428ac9644">

- Explanation of Query Plan
	- The query aggregates the shoe_inventory_ledger by shop_id, then scans through the shoe_inventory_ledger to find the rows with the given shop_id that involve reducing the quantity of shoes. Adding a composite index on the quantity and shop_id for rows in the shoe_inventory_ledger should boost performance.
 
- Index to Add
	- CREATE INDEX ON shoe_inventory_ledger(quantity, shop_id);

- Indexed Query Plan
<img width="1201" alt="Screenshot 2023-12-05 at 11 34 37 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/f48b1533-a773-4cb9-aa5d-440868cef3d8">

- Explanation of Indexed Query Plan
	- The query aggregates the shoe_inventory_ledger by shop_id, then performs an index-only scan on the shoe_inventory_ledger to filter through the composite indexes by quantity and shop_id.

- Expected Performance Boost
	- Yes
 
### 2. Checkout

**Query #1:**
<img width="1200" alt="Screenshot 2023-12-05 at 12 06 08 PM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/f3613df2-2294-4cb3-a19a-abb0ae697b77">

- Explanation of Query Plan
	- The query is sequentially scanning cart_items to find the rows with the given cart_id, then scanning listings for the listing_id using the index on listing_id’s. Adding an index on the cart_id in cart_items should improve performance.
   
- Index to Add
	- CREATE INDEX ON cart_items(cart_id)
   
- Indexed Query Plan
<img width="1200" alt="Screenshot 2023-12-05 at 12 35 10 PM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/1fb512db-ba23-408e-b222-95f9e843a511">

- Explanation of Indexed Query Plan
	- The query scans through cart_items for the given cart_id using the index on cart_id’s, and then scans through listings for the appropriate listing_id’s using the index on listing_id’s.
   
- Expected Performance Boost
	- Yes

### 3. Filter

**Query #1:**

<img width="600" alt="Screenshot 2023-12-05 at 11 44 56 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/6a567a29-7da7-445e-b1ef-4536fc95d8ca">
<img width="1199" alt="Screenshot 2023-12-05 at 11 45 06 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/58db1f70-9fb5-4107-9772-93d8a7f379b4">
<img width="1201" alt="Screenshot 2023-12-05 at 11 45 14 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/df010fa5-3546-4f3c-b4cb-6ce8fea0c318">

- Explanation of Query Plan
	- When the query is sorting and hash joining the tables together, it is performing sequential scans on the shoe_inventory_ledger, shoes, shops, quantities, and listings before filtering according to the inputted filters. Adding an index on the listing_id in shoe_inventory_ledger should help with the performance.

- Index to Add
	- CREATE INDEX ON shoe_inventory_ledger(listing_id)

- Indexed Query Plan
<img width="1198" alt="Screenshot 2023-12-05 at 11 52 14 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/d8c2cafe-d443-4b54-bd71-6f7557244de9">
<img width="1198" alt="Screenshot 2023-12-05 at 11 52 17 AM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/7c3afd12-6261-4383-8bec-4bac16507839">

- Explanation of Indexed Query Plan
	- The query sorts and hash joins the tables together as before, but the new index allows an index scan for the listing_id in the shoe_inventory_ledger instead of a sequential scan.

- Expected Performance Boost
	- Yes
