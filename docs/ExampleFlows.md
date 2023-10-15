# Example Flows

## 1. Shoetopia customer browsing/purchasing flow

A potential customer comes to our shop because the new shoe that just dropped from Nike is already sold out. First, they use the appropriate filters to get the availability across multiple shops. Then, after reviewing the potential sellers, they add the shoe to their cart and checkout. They can now track the status of the order.

- **POST/catalog/filter with filters like “brand” = Nike**
- **POST/cart/**
- **POST/cart/id/items/product_id where product id is unique**
- **POST /carts/id/checkout**
- **GET /buyer/track_order**

The seller will receive their percentage of the sale, and Shoetopia will receive a percentage of the sale. Now, the customer will wait for their new shoes.

