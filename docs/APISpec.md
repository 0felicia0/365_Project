# API Specification

## 1. Customer Endpoints

The API calls are made in this sequence when making a purchase:
1. `Get Catalog of shoes with appropriate filters (can be optional`
2. `New Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`
5. `Track order` (can happen whenever after a purchase)

### 1.1. Browse catalog - `/catalog/filters` (POST)

Creates a new cart for a specific customer.

**Request**:

```json
{
    "brand”: string,
		“size”: int,
		“colors”: [ ],
		“style”: string (this would be constrained to options like: high tops, low, mid, etc)
		“min_price”: int,
		“max_price”: int
}
```

**Returns**:

```json
{
    “Sku”: string
    “product _id”: int
}
```

### 1.2. New Cart - `/carts/` (POST)

Creates a new cart for a specific customer.

**Request**:

```json
{
  “Name”: string,
}
```

**Returns**:

```json
{
    "cart_id": "string" /* This id will be used for future calls to add items and checkout */
}
```

### 1.3. Add Item to Cart - `/carts/{cart_id}/items/{product_id}` (PUT)

Updates the quantity of a specific item in a cart. 

**Request**:

```json
{
  "quantity": "integer"
}
```

**Returns**:

```json
{
    "success": "boolean"
}
```

### 1.4. Checkout Cart - `/carts/{cart_id}/checkout` (POST)

Handles the checkout process for a specific cart.

**Request**:

```json
{
  "payment": "string",
  "gold_paid": "integer"
}
```

**Returns**:

```json
{
    "order_id: "integer"
    "Tracking Number": "integer" 
    "success": "boolean"
}
```

### 1.5. Track Order - `/track/{order_id}` (POST)

Handles the checkout process for a specific cart.

**Returns**:

```json
{
    "Status": string, // Status of the order ("Processing," "Shipped," "Out for Delivery," "Delivered")
    "Estimated Delivery Date": string
}
```

## 2. Seller Purchasing

The API calls are made in this sequence when setting up a shop:
1. 

## 2. Admin
TBD
