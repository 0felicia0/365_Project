# API Specification

## 1. Customer Endpoints

The API calls are made in this sequence when making a purchase:
1. `Get Catalog of shoes with appropriate filters (can be optional`
2. `New Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`
5. `Track order` (can happen whenever after a purchase)

### 1.1. Browse catalog - `/search/filters` (POST)

Filters shoe catalog.

**Request**:

```json
{
    "search_page": string,
    "brand”: string,
    "gender": gender,
    “size”: int,
    “color”: colors,
    “style”: string,
    "condition": condition,
    “min_price”: int,
    “max_price”: int,
    "sort_order": sort_order = desc
}
```

**Returns**:

```json
[
 {
    “listing_id": "integer",
    "quantity": "integer",
    "price": "integer"
 }
]
```

### 1.2. New Cart - `/carts/` (POST)

Creates a new cart for a specific customer.

**Request**:

```json
{
  “user_id”: "integer",
}
```

**Returns**:

```json
{
    "cart_id": "integer" /* This id will be used for future calls to add items and checkout */
}
```

### 1.3. Add Item to Cart - `/carts/{cart_id}/items/{product_id}` (PUT)

Updates the quantity of a specific item in a cart. 

**Request**:

```json
{
	"listing_id": "integer",
	"cart_id": "integer",
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
	"cart_id": "integer"
}
```

**Returns**:

```json
{
    "success_msg": "text"
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

## 2. Admin

### 2.1 Background Check - `/admin/background-check/` (GET)

Returns the various statistics of a seller.

**Request**:
```json
    "shop_id": int,
```

**Response**:
```json
    "sales": int
```

### 2.2 Update Verification - `/admin/update-verification` (POST)

Updates the Verified status of a particular seller.

**Request**:
```json
{
  "shop_id": int,
  "status": bool
}
```

**Response**:
```json
{
  "Success": boolean
}
```

## 3. Seller

### 3.1 Apply for Verification - `/seller/post-application` (POST)

Creates an application request for administrators to view.

**Request**:
```json
{
    "shopr_id": int
}
```
**Response**:
```json
{
    "success": boolean
}
```

### 3.2 Check Verification Status - `/seller/verification-status` (GET)

Checks if a seller is verified or not, and if an application is currently being processed.

**Request**:
```json
{
    "shop_id": int
}
```

**Response**:
```json
{
  "Verified": boolean,
  "Message": string
}
```

### 3.3 Create Listing - `/shops/upload` (POST)
This endpoint allows buyers or sellers to upload their shoes to the item database if they are not already listed.

**Request**:
```json
{
    “Brand”: string,
    “Size”: int,
    “Color”: string,
    “Style”: string,
    “Quantity”: int,
    "Shop_id": int,
    "Price": int

}
```
**Response** 
```json
{
	“Success”: boolean
}
```


### 3.4 Create Shop - `/shop/create_shop` (POST)
This endpoint allows first time sellers to create their shop before they may begin listings. This is once they have already created an account as that is a separate endpoint. 

**Request**:
```json
{
    “Store_name”: string
    “Store_owner” : string
}
```
**Response**:
```json
{
    “Success”: boolean
}
```

### 3.5 Create Account - `/shop/create_account` (POST):
This endpoint allows first time users (regardless of if they are a seller/buyer) to create an account to access the website. 

**Request**:
```json
{
    “Name”: string,
    “Email”: string,
    “Password”: string
}
```
**Response**:
```json
{
    “Success”: boolean
}
```

### 3.6. Retrieve Account - `/{user_id}/get_account` (GET)

Retrieves name and emial associated with user_id
**Request**:

```json
{
	"user_id": "integer"
}
```

**Returns**:

```json
{
    "name": "text", 
    "email": "text"
}
```

### 3.7. Change Password - `/change_password` (PUT)

Changes password with valid inputs

**Request**:

```json
{
	"email": "text",
    "password": "text",
    "new_password": "text"
}
```

**Returns**:

```json
{
    "success_msg": "text"
}
```

### 3.7. Change Email - `/change_email` (PUT)

Changes email with valid inputs

**Request**:

```json
{
	"email": "text",
    "password": "text",
    "new_email": "text"
}
```

**Returns**:

```json
{
    "success_msg": "text"
}
```

### 3.8 Start Flash Sale - `/start_flash_sale` (POST)

Starts a flash sale for a particular shop
```json
{
    "shop_id": "int",
    "disCounter": "int",
    "priceModifier": "int"
}
```

**Returns**:
```json
{
    "success_msg": "text"
}
```