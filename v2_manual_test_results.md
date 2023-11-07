
# Example Workflow 1 - Customer Browsing/Purchasing Flow
A potential customer comes to our shop because the new shoe that just dropped from Nike is already sold out. First, they use the appropriate filters to get the availability across multiple shops. Then, after reviewing the potential sellers, they add the shoe to their cart and checkout. They can now track the status of the order.

POST/catalog/filter with filters like “brand” = Nike
POST/cart/
POST/cart/id/items/product_id where product id is unique
POST /carts/id/checkout
GET /buyer/track_order
The seller will receive their percentage of the sale, and Shoetopia will receive a percentage of the sale. Now, the customer will wait for their new shoes.

## Testing results for create_cart

Curl: curl -X 'POST' \
  'http://127.0.0.1:8000/carts/creat_cart' \
  -H 'accept: application/json' \
  -H 'access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvd3Fzdm5tZWd4bm9hbGJjdnFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjgzMjUsImV4cCI6MjAxMzk0NDMyNX0.pb9Dq_POqNgChJNjtDCGUiIC0xlYxhcAP70vT5C_xuA' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 1
}'

Response: {
  "cart_id": 2
}

## Testing results for set_item_quantity

Curl: curl -X 'POST' \
  'http://127.0.0.1:8000/carts/add_to_cart?cart_id=2&listing_id=5&quantity=1' \
  -H 'accept: application/json' \
  -H 'access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvd3Fzdm5tZWd4bm9hbGJjdnFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjgzMjUsImV4cCI6MjAxMzk0NDMyNX0.pb9Dq_POqNgChJNjtDCGUiIC0xlYxhcAP70vT5C_xuA' \
  -d ''

   Request URL: http://127.0.0.1:8000/carts/add_to_cart?cart_id=2&listing_id=5&quantity=1

Response: "OK"

# Example Workflow 2 - Client Creating a Shop/Creating a Listing
A shoe seller has collected various rare shoes over the years and is looking to list their shoes for sale on Shoetopia. They first need to make an account. From there they will create their shop before finally making their listing.

# Example Workflow 3 - Seller Applying for Verification
Sellers may apply for verification on Shoetopia to demonstrate to potential buyers that a particular seller is trustworthy and an established reputation. After providing their shop id to create an application request, administrators will run a background check on the profile. The seller will be able to check the status of the application, and if the application is successful, their status will be update accordingly.
