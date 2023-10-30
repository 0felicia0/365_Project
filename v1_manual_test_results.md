# Example workflow
POST shop/create_account to create a unique username and provide necessary account information
POST shop/create_shop is called so the seller can decide their store name.
POST listing/create_listing now that the store name is created they can upload their listing for their shoes by providing necessary information such as the name, size, brand, and meaningful tags that will be used for searching

# Testing results

1. curl -X 'POST' \
  'http://127.0.0.1:8000/shop/create_account' \
  -H 'accept: application/json' \
  -H 'access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvd3Fzdm5tZWd4bm9hbGJjdnFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjgzMjUsImV4cCI6MjAxMzk0NDMyNX0.pb9Dq_POqNgChJNjtDCGUiIC0xlYxhcAP70vT5C_xuA' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "emma",
  "email": "emma@gmail.com",
  "password": "hello",
  "date_of_birth": "4-18-2023"
}'

2. "OK"

1. curl -X 'POST' \
  'http://127.0.0.1:8000/shop/create_shop?account_id=2' \
  -H 'accept: application/json' \
  -H 'access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvd3Fzdm5tZWd4bm9hbGJjdnFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjgzMjUsImV4cCI6MjAxMzk0NDMyNX0.pb9Dq_POqNgChJNjtDCGUiIC0xlYxhcAP70vT5C_xuA' \
  -H 'Content-Type: application/json' \
  -d '{
  "store_name": "emmas store"
}'

2. "OK"

1. curl -X 'POST' \
  'http://127.0.0.1:8000/shop/create_listing' \
  -H 'accept: application/json' \
  -H 'access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvd3Fzdm5tZWd4bm9hbGJjdnFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTgzNjgzMjUsImV4cCI6MjAxMzk0NDMyNX0.pb9Dq_POqNgChJNjtDCGUiIC0xlYxhcAP70vT5C_xuA' \
  -H 'Content-Type: application/json' \
  -d '{
  "shoe": {
    "brand": "Nike",
    "color": "green",
    "size": 7,
    "style": "amazing"
  },
  "listing": {
    "shop_id": 6,
    "quantity": 1,
    "price": 50
  }
}'

2. "OK"