# 🏪 Store Management System (IEP Project 2025)

This project implements a **multi-user store management system** using **Python**, **Flask**, **SQLAlchemy**, **Docker**, and **Ethereum smart contracts** (via **Ganache**).  
It was developed as part of the **IEP 2025 project** and demonstrates containerized microservices for user management, store operations, and blockchain-based payment handling.

---

## 📘 Overview

The system simulates a full e-commerce workflow:
- **Customers** can register, browse products, create orders, pay using blockchain, and confirm deliveries.  
- **Couriers** can pick up and deliver orders.  
- **Store owners** can upload products, view sales statistics, and receive payments.  

Each part of the system runs inside its own **Docker container**, and all services communicate securely through internal Docker networks.

---

## 🧩 System Architecture

The project consists of **two main parts**:

### 1. User Management Service
Handles:
- Customer and courier registration (`/register_customer`, `/register_courier`)
- Login and JWT authentication (`/login`)
- Account deletion (`/delete`)

This service maintains a **dedicated database** containing only user data and issues **JWT tokens** for authentication.

### 2. Store Management System
Contains multiple containers:
- **Owner Service** – manages products and statistics  
- **Customer Service** – handles browsing, ordering, payment, and delivery confirmation  
- **Courier Service** – manages order pickup and delivery  

Each service communicates with its own **SQLAlchemy-based backend** connected to a shared store database.

---

## ⚙️ Technologies Used

| Component | Technology |
|------------|-------------|
| Backend | Python 3, Flask, SQLAlchemy |
| Containerization | Docker, Docker Compose |
| Blockchain Simulation | Ganache CLI (Ethereum) |
| Authentication | JSON Web Tokens (JWT) |
| Database | MySQL (or SQLite for testing) |
| Orchestration | Docker Compose |

---

## 🔐 User Roles

| Role | Capabilities |
|------|---------------|
| **Customer** | Register, search products, place orders, pay via blockchain, confirm deliveries |
| **Courier** | Register, view undelivered orders, pick up and deliver orders |
| **Owner** | Manage product catalog (CSV upload), view product/category statistics, receive payments |

---

## 💾 Database Entities

- **User** – email, password, forename, surname, role (customer / courier / owner)
- **Category** – category name
- **Product** – unique name, price, and associated categories
- **Order** – list of ordered products, total price, timestamp, and status (`CREATED`, `PENDING`, `COMPLETE`)

---

## 💰 Blockchain Payment Integration

Payments are simulated using the **Ethereum blockchain (Ganache)**:
- Each order generates a **smart contract**.
- Customers must pay (`order_price * 100 wei`) before delivery.
- Couriers are linked to contracts upon pickup.
- After delivery confirmation:
  - 80% of funds are transferred to the owner.
  - 20% go to the courier.
- Once completed, contracts become immutable.

Ganache is automatically initialized with accounts and sufficient balances.

---

## 🐳 Docker Setup

The system is fully containerized using **Docker Compose**.

### Services

| Container | Description |
|------------|-------------|
| `user_api` | Flask API for user registration and authentication |
| `store_owner_api` | Flask API for owner functions |
| `store_customer_api` | Flask API for customer functions |
| `store_courier_api` | Flask API for courier functions |
| `user_db` | Database for user data |
| `store_db` | Database for store operations |
| `ganache` | Local Ethereum blockchain simulator |

### Environment Rules
- Databases are **not exposed** to the outside network.  
- Data persists between restarts via **Docker volumes**.  
- Each service communicates only with its permitted peers.  
- On first launch, an owner account is pre-created:
  ```json
  {
    "forename": "Scrooge",
    "surname": "McDuck",
    "email": "onlymoney@gmail.com",
    "password": "evenmoremoney"
  }
  ```

---

## 🚀 How to Run

1. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

2. **Access the APIs**
   - User Service → `http://localhost:<user_port>`
   - Store APIs → `http://localhost:<store_port>`
   - Ganache → `http://localhost:8545`

3. **Initialize the system**
   - Tables and default owner account are created automatically.

---

## 🔍 Example Endpoints

### User Service
```
POST /register_customer
POST /register_courier
POST /login
POST /delete
```

### Owner Service
```
POST /update                  # Upload products (CSV)
GET  /product_statistics
GET  /category_statistics
```

### Customer Service
```
GET  /search
POST /order
POST /generate_invoice
POST /delivered
GET  /status
```

### Courier Service
```
GET  /orders_to_deliver
POST /pick_up_order
```

---

## 🧠 Key Features

- JWT-based authentication & authorization  
- SQLAlchemy ORM integration  
- Modular, containerized microservices  
- Secure internal network isolation  
- Automatic database initialization  
- Smart contract integration with Ganache  
- Transaction splitting between owner and courier  

---

## 🧪 Testing

Each API can be tested using **Postman** or **curl**.  
All JSON responses follow consistent schema and error handling (e.g., `"message": "Invalid email."`).
