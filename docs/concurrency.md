# Concurrency 

## 1. Shops/create_listing

Create_listing poses potential concurrency concerns. In our database schema, shoe information is stored for each unique shoe. 
If a shoe does not yet exist, it is added to the database and a listing is made using the shoe_id. This creates an issue as two shops could
potentially create a listing for identical shoes at the same time, resulting in a shoe being in the database twice rather than once.
We protect against this issue by having our read and write in one SQL statement. So, when we check if something is already in the database
we are executing the write feature in that statment. We achieved this using ON CONFLICT to determine whether or not we will be writing. This is
an example of a phantom read.

![image](https://github.com/0felicia0/Shoetopia/assets/97004682/38bcd26a-0185-4a4c-aee7-3fb12c0b0f9c)

## 2. Flash Sale with Checkout

Checking out during a flash sale can cause a lost update concurrency issue. When a shop has a flash sale, only a limited number of customers can take adavntage of the sale.
For example, the first ten customers can get a discount.
T1 is the tenth customer to enter checkout and T2 is the next one after that.
If T1 is in checkout and is in the middle of checking the inventory, T2 can potnetially checkout in the meantime. This now makes the T1 ineligible for the discount.
But, the process still carries out as if it is a valid purchase with a discount.
To prevent this, we implemented a ledger to track how many eligible discounts are available. We also have this in place for tracking shoe inventory for additional protection.

<img width="450" alt="Screenshot 2023-11-28 at 4 16 54 PM" src="https://github.com/0felicia0/Shoetopia/assets/102556938/68cad6f2-f018-4746-83b2-c3bad7a3db05">


## 3. Users/Create_account

Another area of potential concurrency issues is create_account. In the rare case where two people are trying to create an account using the 
same email at the same exact time, there could be a case where T1 made an account first but T2 read that the email wasn't yet used and overrides
T1. This is an example of a phantom read and this problem is accounted for using ON CONFLICT. By using this we can read and write in one transaction 
rather than splitting this up into two sql queries. This is an example of the lost update phenomena. 

![image](https://github.com/0felicia0/Shoetopia/assets/97004682/0a7dd1d9-b596-440f-98cb-3747a710d452)
