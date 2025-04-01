# API Endpoints Documentation

This document outlines all the available API endpoints for the Cinema Service project. Each section details the endpoints grouped by functionality (Admin, Auth, Profile, Movies, Genres, Stars, Orders) along with descriptions, methods, and any special notes regarding authentication or request/response formats.

---

## Admin Endpoints

These endpoints are prefixed with `/admin` and require **Admin** privileges (i.e. the current user must be an Admin).

- **Get User by Email**  
  - **Endpoint:** `GET /admin/users/{user_email}`  
  - **Description:** Retrieves detailed user information (including profile and group data) based on the user's email address.  
  - **Response:** Returns a `UserAdminResponse` containing the user's id, email, activation status, group, and profile information.  
  - **Errors:** Returns 400 for invalid data, 404 if the user is not found, and 500 for any other errors.


- **Register a New User (by Admin)**  
  - **Endpoint:** `POST /admin/users`  
  - **Description:** Allows an Admin to register a new user by providing necessary user data.  
  - **Response:** Returns the created user's information in the form of a `UserAdminResponse`.  
  - **Errors:** Returns 400 for invalid data and 500 for other errors.


- **Update User Data**  
  - **Endpoint:** `PATCH /admin/users/{user_id}`  
  - **Description:** Updates the specified user's data using provided update fields.  
  - **Response:** Returns an updated `UserAdminResponse` with the latest information.  
  - **Errors:** Returns 400 for invalid data, 500 for other errors.


- **Update User Profile**  
  - **Endpoint:** `PATCH /admin/profile/{user_id}`  
  - **Description:** Updates the profile of a user identified by `user_id` using the provided profile data.  
  - **Response:** Returns a `UserAdminResponse` containing updated profile information.  
  - **Errors:** Returns 400 if data is invalid, 404 if the user is not found, or 500 for any other errors.


- **Delete a User**  
  - **Endpoint:** `DELETE /admin/users/{user_id}`  
  - **Description:** Deletes the specified user. The endpoint returns a 204 status code on successful deletion.  
  - **Errors:** Returns 400 for invalid data or 500 for any unexpected errors.

---

## Auth Endpoints

These endpoints are under the `/auth` prefix and handle registration, login, activation, and token management. No Admin role is needed for most of these, but proper authentication is required for logout and password changes.

- **User Registration**  
  - **Endpoint:** `POST /auth/register/`  
  - **Description:** Registers a new user using the provided email and other user data.  
  - **Response:** Returns a `UserCreateResponse` containing registration details.  
  - **Errors:** Returns 400 for invalid data and 500 for server errors.


- **Account Activation**  
  - **Endpoint:** `GET /auth/activate/{token}/`  
  - **Description:** Activates a user account using a unique activation token received by email.  
  - **Errors:** Returns 400 for invalid data and 500 for server errors.


- **Resend Activation Token**  
  - **Endpoint:** `POST /auth/resend-activation/`  
  - **Description:** Resends the activation token to the user’s email if the previous token expired or was lost.  
  - **Errors:** Returns 400 for invalid data and 500 for any other issues.


- **User Login**  
  - **Endpoint:** `POST /auth/login/`  
  - **Description:** Logs in a user by verifying credentials and issuing JWT access and refresh tokens.  
  - **Errors:** Returns 400 for invalid data and 500 for errors during login.


- **User Logout**  
  - **Endpoint:** `POST /auth/logout/`  
  - **Description:** Logs out the current user by revoking the refresh token.  
  - **Errors:** Returns 400 for invalid data and 500 if something goes wrong.


- **Refresh Token**  
  - **Endpoint:** `POST /auth/refresh/`  
  - **Description:** Provides a new access token using a valid refresh token.  
  - **Errors:** Returns 400 for invalid data and 500 for other issues.


- **Change Password**  
  - **Endpoint:** `POST /auth/change-password/`  
  - **Description:** Allows an authenticated user to change their password by verifying the current password.  
  - **Errors:** Returns 400 for invalid data and 500 for server errors.


- **Forgot Password**  
  - **Endpoint:** `POST /auth/forgot-password/`  
  - **Description:** Initiates a password reset process by sending a reset link to the user's email.  
  - **Errors:** Returns 400 for invalid data and 500 for other errors.


- **Reset Password**  
  - **Endpoint:** `POST /auth/reset-password/{token}`  
  - **Description:** Resets the user’s password using a valid reset token and the new password provided.  
  - **Errors:** Returns 400 for invalid data and 500 for unexpected errors.

---

## Profile Endpoints

These endpoints deal with user profile data and require the user to be authenticated.

- **Get Profile**  
  - **Endpoint:** `GET /profile/`  
  - **Description:** Retrieves the current authenticated user's profile data.  
  - **Response:** Returns a `ProfileResponse` with user profile details.  
  - **Errors:** Returns 400 for invalid data and 500 for general errors.


- **Update Profile**  
  - **Endpoint:** `PATCH /profile/`  
  - **Description:** Updates the current user’s profile using provided profile data.  
  - **Response:** Returns an updated `ProfileResponse`.  
  - **Errors:** Returns 400 for invalid data and 500 for any other errors.


- **Upload Avatar**  
  - **Endpoint:** `POST /profile/avatar/`  
  - **Description:** Uploads a new avatar image for the current user.  
  - **Response:** Returns a `ProfileResponse` reflecting the updated avatar.  
  - **Errors:** Returns 400 for invalid data and 500 for unexpected issues.

---

## Genres Endpoints

Endpoints for managing movie genres. Depending on the operation, a user might need **Moderator** or **Admin** privileges.

- **Get List of Genres**  
  - **Endpoint:** `GET /genres/`  
  - **Description:** Retrieves a paginated list of genres.  
  - **Parameters:** `page`, `per_page` (pagination controls).  
  - **Response:** Returns a `GenresResponseSchema` containing genres data.


- **Get Genre Details**  
  - **Endpoint:** `GET /genres/{genre_id}/`  
  - **Description:** Retrieves details of a specific genre by its ID.  
  - **Response:** Returns a `GenreSchema`.


- **Create a New Genre**  
  - **Endpoint:** `POST /genres/`  
  - **Description:** Allows a **Moderator** to create a new genre.  
  - **Response:** Returns the created genre in a `GenreSchema` with a 201 status code.


- **Update Genre**  
  - **Endpoint:** `PUT /genres/{genre_id}/`  
  - **Description:** Updates the specified genre using new genre data.  
  - **Response:** Returns the updated genre.
  

- **Delete Genre**  
  - **Endpoint:** `DELETE /genres/{genre_id}/`  
  - **Description:** Deletes the specified genre. Requires **Admin** privileges.  
  - **Response:** Returns a 204 status code on success.

---

## Movies Endpoints

Endpoints for accessing and managing movie data. These endpoints support filtering, sorting, and user interactions such as likes and favorites.

- **Get List of Movies**  
  - **Endpoint:** `GET /` (under movies router)  
  - **Description:** Retrieves a paginated list of movies with support for filtering (title, year, IMDb rating, price) and sorting.  
  - **Response:** Returns a `MovieListResponseSchema`.


- **Get Movie Details**  
  - **Endpoint:** `GET /{id}`  
  - **Description:** Retrieves detailed information for a specific movie.  
  - **Response:** Returns a `MovieDetailSchema`.


- **Create a New Movie**  
  - **Endpoint:** `POST /`  
  - **Description:** Allows a **Moderator** to create a new movie entry.  
  - **Response:** Returns a `MovieDetailSchema` with a 201 status code.


- **Update Movie**  
  - **Endpoint:** `PATCH /{id}`  
  - **Description:** Updates an existing movie’s data.  
  - **Response:** Returns a message indicating success in the form of a `DetailMessageSchema`.
  

- **Delete Movie**  
  - **Endpoint:** `DELETE /{movie_id}/`  
  - **Description:** Deletes the specified movie. Requires **Admin** privileges.  
  - **Response:** Returns a 204 status code on success.


- **Like or Dislike a Movie**  
  - **Endpoint:** `POST /{movie_id}/like/`  
  - **Description:** Allows a user to like or dislike a movie.  
  - **Response:** Returns a `MovieLikeResponseSchema`.


- **Favorite/Unfavorite a Movie**  
  - **Endpoint:** `POST /{movie_id}/favorite/`  
  - **Description:** Adds or removes a movie from the user’s favorites.  
  - **Response:** Returns a `MovieFavoriteResponseSchema`.


- **Get Favorite Movies**  
  - **Endpoint:** `GET /favorites/`  
  - **Description:** Retrieves a paginated list of the user's favorite movies with optional filtering and sorting.  
  - **Response:** Returns a `FavoriteMoviesSchema`.

---

## Stars Endpoints

Endpoints for managing stars (actors/actresses) in movies.

- **Get List of Stars**  
  - **Endpoint:** `GET /stars/`  
  - **Description:** Retrieves a paginated list of movie stars.  
  - **Response:** Returns a `StarsResponseSchema`.


- **Get Star Details**  
  - **Endpoint:** `GET /stars/{star_id}/`  
  - **Description:** Retrieves details for a specific star by their ID.  
  - **Response:** Returns a `StarSchema`.


- **Create a New Star**  
  - **Endpoint:** `POST /stars/`  
  - **Description:** Allows a **Moderator** to create a new star entry.  
  - **Response:** Returns the created star in a `StarSchema` with a 201 status code.


- **Update Star**  
  - **Endpoint:** `PUT /stars/{star_id}/`  
  - **Description:** Updates the specified star with new data.  
  - **Response:** Returns the updated star information.


- **Delete Star**  
  - **Endpoint:** `DELETE /stars/{star_id}/` 
  - **Description:** Deletes the star specified by `star_id`. This endpoint requires the current user to have **Admin** privileges.
  - **Response:** Returns a 204 No Content status code upon successful deletion.
---

## Orders Endpoints

Orders endpoints manage the order lifecycle from creation through confirmation and cancellation. They are divided into two sets: one for general user order actions and one for administrative order management.

### User Orders

- **Create an Order**  
  - **Endpoint:** `POST /orders/`  
  - **Description:** Creates a new order from the items in the user's shopping cart.  
  - **Response:** Returns the created order details with a 201 status code.


- **Get User Orders**  
  - **Endpoint:** `GET /orders/`  
  - **Description:** Retrieves a list of orders for the authenticated user.  
  - **Response:** Returns a list of orders with basic order details.


- **Get Order Details**  
  - **Endpoint:** `GET /orders/{order_id}`  
  - **Description:** Retrieves detailed information for a specific order.  
  - **Response:** Returns full order details including movies, amounts, and status.


- **Cancel a Pending Order**  
  - **Endpoint:** `PATCH /orders/{order_id}/cancel`  
  - **Description:** Cancels a pending order (only possible if payment has not been completed).  
  - **Response:** Returns updated order status.


- **Confirm an Order**  
  - **Endpoint:** `POST /orders/{order_id}/confirm`  
  - **Description:** Confirms an order and initiates the payment process.  
  - **Response:** Returns order confirmation details.

### Admin Orders

- **Get All Orders (Admin)**  
  - **Endpoint:** `GET /orders`  
  - **Description:** Allows an Admin to retrieve a list of all orders across users.  
  - **Response:** Returns a comprehensive list of orders for monitoring and analysis.


- **Update Order Status (Admin)**  
  - **Endpoint:** `PATCH /orders/{order_id}/status`  
  - **Description:** Allows an Admin to update the status of an order (e.g., from pending to paid or canceled).  
  - **Response:** Returns updated order status details.

---

## Payment Endpoints

### Stripe Webhook
- **Endpoint:** `POST /webhook`
- **Description:**  
  Processes incoming Stripe webhook events. The endpoint:
  - Validates the Stripe signature.
  - Constructs the event and processes it based on its type.
  - For a successful checkout session (`checkout.session.completed`):
    - Creates a new payment record with a status of **SUCCESSFUL**.
    - Updates the associated order status to **PAID**.
    - Creates payment item records for each order item.
    - Sends a payment confirmation email in the background.
  - For failed payment events (`checkout.session.async_payment_failed` or `checkout.session.payment_failed`):
    - Creates a payment record with a status of **CANCELED**.
    - Sends a payment cancellation email in the background.
- **Response:**  
  Returns a JSON response with a status message (e.g., "Payment created" or "Payment cancelled").
- **Errors:**  
  - 400 if the Stripe signature is missing or invalid.
  - 400 for invalid payload or other errors during processing.

---

### Create Payment Session
- **Endpoint:** `POST /{order_id}`
- **Description:**  
  Creates a Stripe Checkout session for a given order. It:
  - Validates that the order exists and is in a pending state.
  - Ensures the total amount is valid and matches the sum of order items.
  - Retrieves the user’s email.
  - Creates a Stripe Checkout Session with line items for each movie in the order.
- **Response:**  
  Returns a JSON object containing the `payment_url` where the user can complete the payment.
- **Errors:**  
  - 400 if the order is not found, the status is not pending, the amount is invalid, or user email is missing.

---

### Payment Success
- **Endpoint:** `GET /success/`
- **Description:**  
  Confirms a successful payment.
- **Response:**  
  Returns a JSON message: "The payment has been successfully completed."

---

### Payment Cancel
- **Endpoint:** `GET /cancel/`
- **Description:**  
  Confirms that the payment was canceled.
- **Response:**  
  Returns a JSON message: "The payment has been canceled."

---

### Payment History
- **Endpoint:** `GET /history/`
- **Description:**  
  Retrieves the payment history for the authenticated user.
- **Response:**  
  Returns an array of payment records. Each record includes:
  - Creation date (`created_at`)
  - Payment amount (`amount`)
  - Payment status (`status`)
- **Errors:**  
  Returns 400 for any issues with retrieving the payment history.

---

## Shopping Cart Endpoints

### Admin Endpoints

These endpoints allow an admin to manage user carts.

#### Get User Cart
- **Endpoint:** `GET /{user_id}/cart`
- **Description:**  
  Retrieves the shopping cart details for a specific user.
- **Response:**  
  Returns the user's cart data.


#### Add Movie to Cart
- **Endpoint:** `POST /{user_id}/cart/items`
- **Description:**  
  Allows an admin to add a movie to a user's cart.
- **Response:**  
  Returns the updated cart information.


#### Remove Movie from Cart
- **Endpoint:** `DELETE /{user_id}/cart/items/{movie_id}`
- **Description:**  
  Removes a specific movie from a user's cart.
- **Response:**  
  Returns updated cart data.


#### Clear User Cart
- **Endpoint:** `DELETE /{user_id}/cart`
- **Description:**  
  Clears all items from a user's cart.
- **Response:**  
  Returns confirmation of the cart being cleared.

---

### User Endpoints

These endpoints are for regular users to manage their own shopping carts.

#### Get Cart
- **Endpoint:** `GET /`
- **Description:**  
  Retrieves the current authenticated user's shopping cart.
- **Response:**  
  Returns the cart details.


#### Create Cart
- **Endpoint:** `POST /`
- **Description:**  
  Creates a new shopping cart for the user (if one does not already exist).
- **Response:**  
  Returns the newly created cart information.


#### Add Item to Cart
- **Endpoint:** `POST /items/`
- **Description:**  
  Adds a movie to the current user's cart.
- **Response:**  
  Returns updated cart details.


#### Remove Item from Cart
- **Endpoint:** `DELETE /items/{item_id}`
- **Description:**  
  Removes a specific item from the user's cart.
- **Response:**  
  Returns updated cart details.


#### Clear Cart
- **Endpoint:** `DELETE /clear/`
- **Description:**  
  Clears all items from the current user's cart.
- **Response:**  
  Returns a confirmation message indicating that the cart has been cleared.
