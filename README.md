# Cart API (FastAPI Architecture)

A production-grade, fully observable E-Commerce Cart API built with **FastAPI**, **SQLAlchemy**, and **MySQL**. This project was designed to demonstrate complete backend data lifecycles, relational database integrity, and real-time request tracing.

## Key Features

* **Complete CRUD Lifecycle:** Manage Users, Products, Carts, and Cart Items with full HTTP method support (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
* **Relational Data Integrity:** Enforces database-level Foreign Key constraints (e.g., preventing the deletion of a product currently sitting in an active cart).
* **Strict Data Validation:** Utilizes `Pydantic` schemas to intercept bad data before it ever hits the database.
* **Custom Middleware Observability:** Features a global HTTP middleware and `logger.py` integration to track, timestamp, and log every API request and response status.
* **Live Flow Visualizer:** Includes a vanilla HTML/JS frontend that acts as a real-time terminal, breaking down the exact sequence of FastAPI routing, database querying, and JSON serialization.

## Tech Stack

* **Framework:** FastAPI (Python)
* **Database:** MySQL (via XAMPP)
* **ORM:** SQLAlchemy
* **Validation:** Pydantic
* **Server:** Uvicorn
* **Frontend:** Vanilla HTML, CSS, JavaScript

## Project Structure

```text
Cart_C/
├── app/
│   ├── database.py       # SQLAlchemy engine and session management
│   ├── models.py         # MySQL Table definitions (User, Product, Cart, CartItem)
│   ├── schemas.py        # Pydantic models for request/response validation
│   ├── logger.py         # Secure server-side logging configuration
│   ├── main.py           # API Router, endpoints, and Middleware
│   └── frontend/
│       └── index.html    # Interactive API testing UI and Flow Visualizer
├── .gitignore
└── README.md
