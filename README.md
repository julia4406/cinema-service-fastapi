# Cinema Service

**Cinema Service** is a forward-thinking, full-featured platform where users can register, log in, browse an extensive catalog of movies, and even purchase their favorites—all from the comfort of their own home. The project leverages modern web technologies, ensuring a smooth, secure, and highly personalized experience.

---

## Table of Contents
- [Key Features](#key-features)
  - [User Management](#user-management)
  - [Movies](#movies)
  - [Shopping Cart](#shopping-cart)
  - [Orders](#orders)
  - [Payments](#payments)


- [Endpoints](#endpoints)


- [Architecture & Tech Stack](#architecture--tech-stack)


- [Database Schema](#database-schema)
  - [Accounts](#accounts)
  - [Movies Schema](#movies-schema)
  - [Shopping Cart & Orders](#shopping-cart--orders)
  - [Payments Schema](#payments-schema)


- [Getting Started](#getting-started)
  - [Installation & Setup](#installation--setup)

---

## Key Features

### User Management

- **Registration & Activation:**
  - Register using your email.
  - Receive an activation link valid for 24 hours. If you miss it, no worries – you can request a new one!
  - Expired activation tokens are automatically cleaned up using celery-beat.


- **Login & Logout:**
  - Secure login with JWT tokens (both access and refresh tokens).
  - Logout clears the JWT token, ensuring your session stays secure.


- **Password Management:**
  - Change your password by verifying the old one.
  - Forgot your password? Request a reset link and get back on track without hassle.
  - Password complexity checks to keep your account safe.


- **User Groups:**
  - **User:** Basic access.
  - **Moderator:** Additional rights to manage movie content and view sales.
  - **Admin:** Full control including user management and manual account activations.

### Movies

- **Catalog Browsing:**
  - Enjoy an organized movie catalog with pagination.
  - Detailed movie descriptions and ratings.
  

- **Social Features:**
  - Like, dislike, and favorite movies.
  - Rate movies on a 10-point scale.


- **Favorites & Search:**
  - Easily add movies to your favorites.
  - Advanced search, filter, and sort options to find the perfect movie for your mood.

### Shopping Cart

- **Cart Management:**
  - Add movies to your cart if you haven’t purchased them already.
  - Remove or clear items with ease.
  - View movie details like title, price, genre, and release year in your cart.


- **Purchase Validation:**
  - Ensure movies are available for purchase.
  - Prevent duplicate purchases – once bought, it’s yours for life (or at least as long as your account stays active).

### Orders

- **Order Lifecycle:**
  - Place orders for movies in your cart.
  - Track your orders with clear statuses: pending, paid, or canceled.
  - Detailed order history with date, list of movies, total amount, and status.
  - Cancel orders before payment, and for paid orders, initiate a refund request.


- **Seamless Checkout:**
  - Redirect to a payment gateway for secure payment processing.
  - Email confirmations for all successful orders.

### Payments

- **Stripe Integration:**
  - Make payments through Stripe with ease.
  - Receive confirmation both on the website and via email.
  

- **Transaction Records:**
  - View detailed payment history including date, amount, and status.
  - Track external transaction IDs for easy cross-referencing.
  

- **Validation & Security:**
  - Ensure accurate total amounts and transaction integrity.
  - Recommendations provided if a payment method fails—because even the best of us have off days!

---

## Endpoints

For detailed API documentation and available endpoints, please refer to [API Endpoints Documentation](./endpoints.md).

---

## Architecture & Tech Stack

- **Backend:** FastAPI for lightning-fast API responses.
- **Containerization:** Docker & Docker Compose to run FastAPI, Redis and Celery.
- **Dependency Management:** Poetry keeps our dependencies in check with the `pyproject.toml`.
- **CI/CD:** GitHub Actions automates tests and code quality checks.

---

## Database Schema

### Accounts

- **User & Profile:**
  - `users` table for user credentials and activity tracking.
  - `user_profiles` for optional additional information like first name, last name, and avatar.
  

- **Tokens:**
  - `activation_tokens` for account activation.
  - `password_reset_tokens` for recovering forgotten passwords.
  - `refresh_tokens` for managing JWT access renewal.
  

- **User Groups:**
  - `user_groups` table defines roles: USER, MODERATOR, ADMIN.

### Movies Schema

- **Movie Details:**
  - `movies` table holds movie details like title, release year, duration, IMDb rating, and price.
  

- **Associated Entities:**
  - `genres`, `stars`, `directors`, and `certifications` tables.
  - Association tables like `movie_genres`, `movie_directors`, and `movie_stars` to maintain many-to-many relationships.

### Shopping Cart & Orders

- **Shopping Cart:**
  - `carts` for each user (one-to-one relationship).
  - `cart_items` for individual movies added to the cart.
  

- **Orders:**
  - `orders` table tracks each order along with its status (pending, paid, canceled).
  - `order_items` records which movies are in an order and at what price they were purchased.

### Payments Schema

- **Payment Records:**
  - `payments` table for recording payment transactions linked to orders.
  - `payment_items` for itemized details of each payment.
  

- **Integration & Auditing:**
  - External payment IDs for cross-referencing with Stripe.
  - Detailed status tracking to support refunds and audits.

---

## Getting Started

### Installation & Setup

Follow the steps below to set up the project on your local machine:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/julia4406/cinema-service-fastapi.git
   cd cinema-service-fastapi
   
2. **Install Dependencies: Use Poetry to install all required dependencies:**
   ```bash
   poetry install

3. **Launch the Application: Spin up all services with Docker Compose:**
   ```bash
   docker-compose up --build

4. **Configuration:**
  - Configure environment variables as needed.
  - Review the pyproject.toml for dependency configurations.
