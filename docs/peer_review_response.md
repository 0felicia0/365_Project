##Ella Hagen

###Code Review
1. For both create_account and create_shop, I think just for the sake of clarity when testing, it might be better to return the account id that was created instead of just "ok." This way if you don't have access to the database you can still follow the flow of that specific account/shop id. 
	- We implemented this feedback
For create_shop, I would first check to make sure that the shop name isn't already in the database, so that way two sellers won't have the same shop name.
We implemented this feedback
Similarly to the one above, for create_account, I would add a check to make sure that the email that's passed in isn't already in the users table, so that way it's not possible to have multiple accounts under the same email.
We implemented this feedback
With the search function, it might be better to have it output a string representing the shoe instead of just the listing_id, otherwise it's kind of hard to see what shoe is actually for sale.
We implemented this feedback and now return additional information in search.
In addition to making search clearer, we added a compare endpoint so we can isolate the two listings we are looking at.
This is kind of trivial since it's not an actual shop, but right now carts_checkout doesn't have a way for customers to pay. With the potion shop there was a payment string, so maybe you could add that as well.
We implemented this feedback
In create_listing, there isn't any error handling, so even if a transaction fails, it still returns "ok." This can be pretty easily fixed though with a try, except clause.
We implemented this feedback.
Similarly, create shop and create account return "ok" no matter what, so maybe consider adding more error handling in case something fails.
We implemented this feedback
I saw this when testing, but it doesn't look like the search list is updated when a shoe is bought. I bought a pair of shoes, but then when I ran the search function again, the shoe was still there. I think it's because the search function is looking at the original quantity that was entered when the seller put in the shoe, but then the quantity is continuously changed through the ledger (everything works during checkout).
We implemented this feedback
Also, since the quantity of a certain shoe is maintained in a ledger based system, there should be a check in the search function that sums the quantity and if the quantity is zero then it shouldn't be added to the return list.
We implemented this feedback.
For checkout, this also isn't super necessary, but instead of returning false if the inventory isn't enough, it might be better to return "insufficient inventory," or something like that, so that way it's more clear for the customer why their transaction didn't go through.
We implemented this feedback.
In create_cart, if you put in an account_id that doesn't exist, it will return an Internal Server Error, so it might be good to check first to see if it exists, or use a try/except statement.
We implemented this feedback
Similarly to the one above, in set_item_quantity, if you put a non-existent listing id, it'll cause an Internal Server Error. So it might be good to add more extensive error handling so instead of just saying Internal Server Error, it'll explain what went wrong.
We implemented this feedback
I'm not quite sure how to test this since the search function doesn't update, but I think that if someone has multiple items in their cart it will only checkout the first item since .first() is called, instead of doing something like for row in res:
We implemented this feedback

###Schema/API
For style in your api spec, you say it should be constrained to options such as "high tops, low, mid, etc," but right now a user could type in anything, so it might help to add an enum to the database so they'll be forced to choose.
We did not do this because there are many possible styles of shoes. Our database takes in any types of shoes so there are many possibilities for what could be implemented, therefore we determined an Enum would not be reasonable for this portion.
Similarly, I think some other fields like color could be changed to an enum, just so it's more restrictive.
We implemented this feedback. 
It could be good to implement a function that gets all listings for a specific store or add a store field to the search function so if a customer has a specific store that they know and trust, they can look to see what the store offers.
We implemented this feedback as part of a search rather than its own function.
For simplicity's sake, this might be unnecessary, but to fit your design, there are a couple fields whose data types could change. The main one being size could be a float instead, so that way people can sell shoes that are, for example, size eight and a half.
We implemented this feedback
For store verification, it might be good to implement the ratings/review system, so that way only stores that have good reviews and ratings can be verified, regardless of how many shoes they have sold.
We implemented this feedback
Maybe you could add a "condition" parameter to the listing so customers could know whether the shoe is used, new, lightly worn, or etc.
We implemented this feedback.
I think this is just a matter of preference, but the endpoint paths could contain more information about the transaction taking place. For example, in the set quantity function, instead of "set_item_quantity", it could be "/{cart_id}/listing/{listing_id}."
We implemented this feedback.
I would consider maybe automating the verification of stores, so maybe after a customer has purchased a shoe/left a rating, it would check to see if it meets the qualifications for verification. That way the administrators wouldn't have to do it by hand.
We did not implement this feedback, as it would waste resources and time as our shop scales to check if a shop meets a verification. We approached this from the perspective of Instagram verification, where users can apply for the status rather than being automatically awarded. 
In the search function, in the array of listings, it might be nice to add whether or not the store that is selling it is verified or not.
We implemented this feedback
This is just a suggestion, but the functions could be broken up into different files, perhaps the search function could go into it's own file, since I'm not sure if it really matches the purpose of the other functions in carts.py.
We implemented this feedback
Similarly to the one above, I think the filter endpoint should probably be something like "/filter" instead of "/carts/filter" since it doesn't really have anything to do with carts.
We implemented this feedback
Perhaps consider having it so the filter endpoint doesn't need the API key since it's a function that doesn't really need proper authorization and should be available for all customers to access.



###Suggestions
Suggestion 1: Store Discounts
It would be cool if sellers could decide to offer a store wide discount, where all of the listings that they offer are marked down by however much they decide and for however long they want the sale to go on for. This wouldn't require any database additions, just a new endpoint that would update the listings table. This could also work well with the filter endpoint, if there was an option so that users could only see shoes that are currently on sale.
	We implemented this feedback with a flash sale feature
Suggestion 2: Promoted Shoes
If sellers want to promote their shoes, they could pay a small fee, and then when a customer uses the search function, that shoe will be displayed first, as long as it matches the criteria. This would require a small database change, which would probably just be a boolean in the listing table that says whether or not it has been promoted. Additionally this would require a new endpoint that would take in payment and the listing_id of the promoted shoe.
	We implemented this feedback with a promotional tier a shop can purchase


Jin Wu

Code Review
in carts.py, filter(min_price, max_price) should be floats not integers to allow for prices that are not whole numbers. 
No, was told to use ints and change currency to cents
in carts.py, max_price is declared as an integer but is constantly being referenced to as a string.
We implemented this feedback
/create_cart does not check if the user already has an active cart, so in that case a user may create two unique carts in the carts table which may cause issues in checkout such as doubling their order when it is not intended.
We implemented this feedback
in /checkout, it may be useful to have more data in the description such as quantity, listing_id, and money paid.
We implemented this feedback
/create_account does not account for if the user already exists in the table. This may create duplicate users and may interfere with checkouts and other functions which expect only a single unique account.
We implemented this feedback
I think the Listing(BaseModel) should have price as a float to allow for decimal values of dollars.
We were told to use int and convert dollars to cents
in /create_listing, it may be helpful to also contain the price of the shoe in the description
We implemented this feedback
a shop may bypass the post_application due to create_shop not checking if a shop already exists in the table so there may be duplicate shops in the shops table and it will count each shoe sold per shop extra and will get them verified when you don't want them to.
We implemented this feedback
/verification_status will error out on shops with multiple entries in the table, and that is possible because create_shop does not check if a shop already exists in the table before inserting a new shop into the shops table.
We implemented this feedback
I would return more descriptive results when a user sets item quantity or checkout, maybe returning OK with the description of the item i added to my cart.
We implemented this feedback
I would re-route filtering and getting the catalog of items away from the carts endpoint.
We implemented this feedback
Maybe add an endpoint where no filters are passed and all the items in every store are returned just so users can see items without having to hunt for them.
We implemented this feedback with the search endpoint, not a separate one.

Schema/API
cart_items should always point to a specific cart so I think cart_id should never be null, that would mean there is an item in an unknown cart.
We implemented this feedback
cart_items should not exist if there is no quantity associated with it, so the quantity should be not null and always be 1 or greater, as a cart_item with quantity zero should just not exist.
We implemented this feedback
I would consider more descriptors to put under shoes. With how specialized this product is, the majority of users probably really care about exactly what shoe they are buying. Maybe add date_released, condition, and if it has all original accessories.
We implemented this feedback with the condition. 
I think adding a rating column to shops would be good for users to easily see how trustworthy a shop is at a quick glance.
We implemented this feedback
I would add a reviews table with foreign key references to shops and the user who left the review as well as a rating(int) and a description(text) so users can leave ratings for particular shops and other users can judge a shop off of more descriptive ratings.
We implemented this feedback but without description
Maybe add a way for users to display themselves without using either their email or real name as that can help with privacy.
Not sure what this really meant. We do not display any information besides name and email now when one uses the get_account endpoint.
It seems that there is no way to take a listing off of the site after it has been sold other than to delete the listing all together. Maybe add a boolean column to it (active) to only display listings that are not sold, and keep all sold listings in the database.
We have a filter to check the quantity. If it’s zero, we don’t show in the search results.
I think shop_balance_ledger (balance) should not be an integer as people can pay with cents as well, so a float would fit it better, same with all other variables representing dollar amounts.
No, we used ints for converting to cents
I assume that dollar amounts are in USD but it might help to keep track of that in case you need to do conversions with other countries.
No, we just wanted to focus on USD
Maybe add an endpoint in /catalog/ to display all listings without needing any filters to apply.
Search endpoint handles the cases.
the endpoint /shop/create_shop takes in a store name and store owner both as strings. This may cause problems when there are two users on the platform with the same name. I think that creating a shop based off of a unique identifier (user id) would be much better.
We implemented this feedback
the endpoint /carts/{cart_id}/checkout passes in gold_paid, which seems a bit odd for a real life shop.
We implemented this feedback

Suggestions

Ratings
It would be nice if there was an endpoint like /shop/rating which took in an account_id and a rating (integer from 1-5) as well as a description (text). This endpoint would update a ratings table (which has a foreign key reference to a shop) and we could get a shops rating with the endpoint /shop/rating/{shop_id}
We implemented this feedback
Threads / Discussion Board
For a particular shoe it would be cool if users could talk about the shoe and add comments/reply to others about it. There could be a /shoes/discussion/{shoe_id} endpoint which takes in an optional comment_id if this was a reply to another persons comment or would just take in text about the particular shoe.
We did not implement this, but liked the idea. We wanted to focus on ratings.

Nick Patrick

Code Review
For create_account, you may want to check if a user is already in the database so there are no duplicate rows with the exact same information
We implemented this feedback
Similarly, you may not want people to have the same shop name as another shop that already exists. I recommend checking that the shop name is unique in the create shop endpoint.
We implemented this feedback
For your set_item_quantity function, I recommend adding the cart id, as well as the listing id into the post/curl statement. You can check the schema for the potion lab and basically copy gthe post statement there. "@router.post("/{cart_id}/items/{item_sku}")" replacing item_sku with listing_id
We implemented this feedback
You can also do something similar in checkout. the curl statement should include the cart_id
We implemented this feedback
Also, I recommend looking over shop.py and checking each of the curls. You could add "shop_id" or "account_id" where need be.
We implemented this feedback
For checkout, you may want to return something other than True/false. for example, a message saying "Cart successfully checked out"/ "Checkout failed"
We implemented this feedback
As of now, your post_application function just counts the sum of the quantity, meaning the total amount of shoes they have in their inventory at the moment. Instead, you should do something like count* where quantity <0 from the ledger. This would at least count how many times customers have purchased shoes from them, rather than their current stock of shoes.
We implemented this feedback
I would recommend combining the post_application function and the uodate_verification. i do not see the purpose of having them in two separate functions.
No because helps establish idempotency and thus concurrency control by preventing unnecessary posts if the planning logic fails, and also the intention is that an administrator would check the results of the application and manually update the shop’s verification status instead of it being an automatic process. that way customers know that a verified shop has been reviewed by staff instead of a shop managing to game some algorithm
Pretty minor issue but you should change the server.py code to include members of your group as the contact
We implemented this feedback
In filter, max and min price should be floats, not integers.
We are using ints to convert dollars to cents
Also, size should be a float so that people can search for half shoe sizes.
We implemented this feedback
You should also have a condition "if min_price != 1" so that you can filter by the minimum price
We implemented this feedback

Schema/API
You should take a look at what columns in your tables can be null. For example I think something like "quantity" in your cart_items table should not be nullable and maybe have a default value of 0 or 1.
We implemented this feedback
Your "shoes" table could have a few more columns to be more specific on the actual shoe. For example there are multiple Nike Dunk Lows that are blue. I recommend adding something like 'factory color' column to differentiate between say "University Blue" and "Blue Raspberry" dunks. You may want both to come up when someone searches for blue dunks, but you would want to differentiate between the blue color-ways.
We implemented part of the feedback. Color is constrained now by an enum and we are only containing basic colors at this time, based on what we saw on Nordstrom.com
Additionally, You may want a column for 'release year' to differentiate between shoes of the same color-way which were released in different years. If someone was trying to sell their 2009 Jordan Flu Game 12's, they would be under the same shoe id as if someone were to sell their 2016 Flu Games. While the shoes have the same color-way and style, they have minor differences in details and a significant difference in price.
We decided not to implement this feature as it would further muddle results for users rather than providing concise feedback about each listing. In addition some sellers may not have this info.
I think you may want to differentiate between 'users' and 'customers'. Some users might only want to host a shop, and others may only want to purchase shoes. A customer would need info such as 'Shipping Address' and 'payment info' so that they can purchase the shoes they want and they will be delivered to them.
We discussed this as a group when we were initially planning and decided there were too many similarities to separate the two
You will want to make user_id a foreign key to the users table in your shops table.
We implemented this feedback
You may want users to have a 'username' column, unless you plan on using emails as the username.
Emails are used as the username
You may want to change the 'size' column in your listings table to a float to include half sizes. Perhaps you could also add a constraint so it must be either a full size or a half size.
We implemented this feedback
You may also want to add a 'sold' boolean column to the listings table to differentiate between listings that are active and listings that have been sold already.
We do not display any listings with 0 quantity
You will want the 'balance' column in the shop balance ledger to be a float in case people list shoes for an amount that is not an integer value
We convert dollars to cents
Similarly, You might want the 'price' column in your listings to be a float in case someone wants to list a shoe for a price such as $199.99
We convert dollars to cents
You probably should not store user's passwords as plain text in the users table. Like we went over in class, you should find a way to use a hashmap so their info cannot be accessed
Not implemented, but we do know that this is vital in a real application.
You might want some type of constraint on the email column in the users table. For example it should end in '@gmail.com' or something similar
There are too many emails for us to constrain as valid inputs. I do agree with proper verification of valid emails.

Suggestions
Suggestion 1
For my first endpoint suggestion, I think it would be very cool if users were able to trade their shoes. It might be difficult to implement but you could have a separate catalog for shoes listed for trade. Then, you could maybe have some things that that user is looking for in return. For example, what size they wear, what brands they are looking for, etc. It would also be cool to have something like a size-swap, where users could list their shoes up while looking for the same shoe in a different size.
	We don’t want to have a trading feature as this can happen through third party ways. And hard for us as the developers to guarantee safe trading with real shoes.
Suggestion 2
I think a great endpoint you could implement would be customer ratings on the shops. You could include the rating (1-5) and even perhaps allow customers to leave comments/reviews on their experience. I think this could also work well with your shop verification. Perhaps the shop would need a minimum rating (i.e. 3 stars) and/or a certain amount of reviews to become verified.


We implemented this feedback
