# Example Flows

## 1. Shoetopia customer browsing/purchasing flow

A potential customer comes to our shop because the new shoe that just dropped from Nike is already sold out. First, they use the appropriate filters to get the availability across multiple shops. Then, after reviewing the potential sellers, they add the shoe to their cart and checkout. They can now track the status of the order.

- **POST/catalog/filter with filters like “brand” = Nike**
- **POST/cart/**
- **POST/cart/id/items/product_id where product id is unique**
- **POST /carts/id/checkout**
- **GET /buyer/track_order**

The seller will receive their percentage of the sale, and Shoetopia will receive a percentage of the sale. Now, the customer will wait for their new shoes.

## 2. Shoetopia client creating a shop/creating a listing flow

A shoe seller has collected various rare shoes over the years and is looking to list their shoes for sale on Shoetopia. They first need to make an account. From there they will create their shop before finally making their listing. 

- **POST shop/create_account to create a unique username and provide necessary account information**
- **POST shop/create_shop is called so the seller can decide their store name.**
- **POST listing/create_listing now that the store name is created they can upload their listing for their shoes by providing necessary information such as the name, size, brand, and meaningful tags that will be used for searching**

## 3. Shoetopia seller applying for verification

Sellers may apply for verification on Shoetopia to demonstrate to potential buyers that a particular seller is trustworthy and an established reputation. After providing their shop id to create an application request, administrators will run a background check on the profile. The seller will be able to check the status of the application, and if the application is successful, their status will be update accordingly.

- **POST /seller/post-application to create an application request**
- **GET /admin/background-check to check the seller's transactions, dispute history, and ratings**
- **POST /seller/verification-status to check the verified status of the seller and the outcome of the application**
- **POST /admin/update-verification to set the seller's status to Verified or Unverified**


