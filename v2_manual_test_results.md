
# Example workflow
A potential customer comes to our shop because the new shoe that just dropped from Nike is already sold out. First, they use the appropriate filters to get the availability across multiple shops. Then, after reviewing the potential sellers, they add the shoe to their cart and checkout. They can now track the status of the order.

POST/catalog/filter with filters like “brand” = Nike
POST/cart/
POST/cart/id/items/product_id where product id is unique
POST /carts/id/checkout
GET /buyer/track_order
The seller will receive their percentage of the sale, and Shoetopia will receive a percentage of the sale. Now, the customer will wait for their new shoes.

# Testing results for create_cart

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

# Testing results for set_item_quantity

Curl: curl -X 'POST' \
  'http://127.0.0.1:8000/carts/add_to_cart?cart_id=2&listing_id=5&quantity=1' \
  -H 'accept: application/json' \
  -H 'access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvd3Fzdm5tZWd4bm9hbGJjdnFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjgzMjUsImV4cCI6MjAxMzk0NDMyNX0.pb9Dq_POqNgChJNjtDCGUiIC0xlYxhcAP70vT5C_xuA' \
  -d ''

   Request URL: http://127.0.0.1:8000/carts/add_to_cart?cart_id=2&listing_id=5&quantity=1

Response: "OK"
