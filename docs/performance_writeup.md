# Performance Writeup

## 1. Fake Data Modeling
Link to file used to construct the rows of data: https://github.com/0felicia0/Shoetopia/blob/main/src/populate.py 

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
- compare - 9, 16, 10

**From this, we concluded that our slowest endpoints were:**
- post_application
- checkout
- filter

## 3. Performance tuning

**1. Post Application**
**Query #1:**
(screenshot)

- Explanation of Query Plan 
    - The query aggregates the shop_rating_ledger by shop_id, then scans through the grouped rows to find the appropriate shop_id. An index on the shop_id in the shop_rating_ledger used in the where and group by statements should improve performance (by).

- Index to Add
    - CREATE INDEX ON shop_rating_ledger(shop_id)

**Indexed Query Plan**
(screenshot)

**Explanation of Indexed Query Plan**
The query aggregates the shop_rating_ledger by shop_id, then scans through the bitmap of indexes to find the appropriate shop_id.

**Expected Performance Boost:** YES

**Query #2:**
- QUERY PLAN SCREENSHOT
- EXPLANATION OF QUERY PLAN
	- The query aggregates the shoe_inventory_ledger by shop_id, then scans through the shoe_inventory_ledger to find the rows with the given shop_id that involve reducing the quantity of shoes. Adding an composite index on the quantity and shop_id for rows in the shoe_inventory_ledger should boost performance. 
- INDEX TO ADD
	- CREATE INDEX ON shoe_inventory_ledger(quantity, shop_id);
- INDEXED QUERY PLAN SCREENSHOT
- EXPLANATION OF QUERY PLAN
	- The query aggregates the shoe_inventory_ledger by shop_id, then performs an index-only scan on the shoe_inventory_ledger to filter through the composite indexes by quantity and shop_id.
- EXPECTED PERFORMANCE BOOST: YES



