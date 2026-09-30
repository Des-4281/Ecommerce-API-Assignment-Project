# E-Commerce API

A RESTful API for an online store, built with **Flask**, **Flask-SQLAlchemy**, **Flask-Marshmallow**, and **MySQL**. It manages users, products, and orders.

## Features

- Full CRUD for **users** and **products**
- Create **orders** and add or remove products on them
- **One-to-Many:** a user can place many orders
- **Many-to-Many:** an order can hold many products, and a product can appear in many orders (via the `order_product` table)
- Duplicate products on the same order are blocked
- User emails must be unique
- Deleting a user also deletes their orders
- Marshmallow schemas serialize all responses to JSON

## Setup

**1. Create the database**

In MySQL Workbench, run:

```sql
CREATE DATABASE ecommerce_api;
```

**2. Create a virtual environment and install dependencies**

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Add your MySQL password**

Copy `.env.example` to a new file named `.env` and fill in your password:

```
DB_PASSWORD="your_mysql_password_here"
```

**4. Run the app**

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`. The tables are created automatically on first run.

## Endpoints

### Users
| Method | Endpoint | Description |
|---|---|---|
| GET | `/users` | Get all users |
| GET | `/users/<id>` | Get a user by ID |
| POST | `/users` | Create a user |
| PUT | `/users/<id>` | Update a user |
| DELETE | `/users/<id>` | Delete a user |

### Products
| Method | Endpoint | Description |
|---|---|---|
| GET | `/products` | Get all products |
| GET | `/products/<id>` | Get a product by ID |
| POST | `/products` | Create a product |
| PUT | `/products/<id>` | Update a product |
| DELETE | `/products/<id>` | Delete a product |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| POST | `/orders` | Create an order |
| PUT | `/orders/<order_id>/add_product/<product_id>` | Add a product to an order |
| DELETE | `/orders/<order_id>/remove_product/<product_id>` | Remove a product from an order |
| GET | `/orders/user/<user_id>` | Get all orders for a user |
| GET | `/orders/<order_id>/products` | Get all products in an order |

### Example request bodies

**Create user**
```json
{"name": "Dave", "address": "123 Main St", "email": "dave@example.com"}
```

**Create product**
```json
{"product_name": "Keyboard", "price": 49.99}
```

**Create order**
```json
{"user_id": 1, "order_date": "2026-09-29T10:00:00"}
```

## Testing with Postman

A Postman collection with every endpoint is included: `ecommerce_api.postman_collection.json`.

In Postman, click **Import**, select the file, and send the requests in order (Users → Products → Orders, with deletes last).

## Database

| Table | Columns |
|---|---|
| `users` | id, name, address, email (unique) |
| `products` | id, product_name, price |
| `orders` | id, order_date, user_id → users |
| `order_product` | order_id → orders, product_id → products (composite primary key, which prevents duplicates) |
