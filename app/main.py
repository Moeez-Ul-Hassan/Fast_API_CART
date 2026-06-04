from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from logger import logger

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ultimate Learning Cart API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- FLOW TRACKING ---
FLOW_LOGS = []

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response Status {response.status_code}")
    return response

@app.get("/flow")
def get_flow():
    return FLOW_LOGS

@app.delete("/flow")
def clear_flow():
    FLOW_LOGS.clear()
    return {"message": "Flow cleared"}

def log_step(message: str):
    FLOW_LOGS.append(message)

# ==========================================
# 1. USERS
# ==========================================
@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    log_step("Validating User Data")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(email=user.email, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_step("User inserted into MySQL database")
    return new_user

@app.get("/users/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    log_step("Fetching all users from database")
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    log_step(f"Searching for User ID: {user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    log_step(f"Updating User ID: {user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.email = user_update.email
    user.name = user_update.name
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    log_step(f"Deleting User ID: {user_id} and cascading carts")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    [db.delete(cart) for cart in db.query(models.Cart).filter(models.Cart.user_id == user_id).all()]
    db.delete(user)
    db.commit()
    return None

# ==========================================
# 2. PRODUCTS
# ==========================================
@app.post("/products/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    log_step("Adding new product to inventory")
    new_product = models.Product(name=product.name, price=product.price, stock=product.stock)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products/", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    log_step("Fetching all products")
    return db.query(models.Product).all()

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    log_step(f"Fetching Product ID: {product_id}")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.patch("/products/{product_id}/stock", response_model=schemas.ProductResponse)
def update_stock(product_id: int, data: schemas.StockUpdate, db: Session = Depends(get_db)):
    log_step(f"Patching stock for Product ID: {product_id}")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    product.stock = data.stock
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    log_step(f"Deleting Product ID: {product_id}")
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None

# ==========================================
# 3. CARTS & ITEMS
# ==========================================
@app.post("/users/{user_id}/cart/", response_model=schemas.CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(user_id: int, db: Session = Depends(get_db)):
    log_step(f"Checking if User {user_id} has active cart")
    if db.query(models.Cart).filter(models.Cart.user_id == user_id, models.Cart.status == "active").first():
        raise HTTPException(status_code=400, detail="User already has active cart.")
    new_cart = models.Cart(user_id=user_id, status="active")
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    log_step("New cart generated")
    return new_cart

@app.get("/cart/{cart_id}", response_model=schemas.CartResponse)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    log_step(f"Fetching Cart ID: {cart_id}")
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart: raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@app.post("/cart/{cart_id}/items/", response_model=schemas.CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(cart_id: int, item: schemas.ItemAdd, db: Session = Depends(get_db)):
    log_step(f"Validating Cart {cart_id} is active")
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.status == "active").first()
    if not cart: raise HTTPException(status_code=404, detail="Active cart not found")
        
    log_step(f"Checking inventory for Product {item.product_id}")
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < item.quantity: raise HTTPException(status_code=400, detail="Insufficient stock")

    new_item = models.CartItem(cart_id=cart_id, product_id=item.product_id, quantity=item.quantity, price_at_addition=product.price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    log_step("Item added successfully")
    return new_item

@app.post("/cart/{cart_id}/checkout")
def checkout_cart(cart_id: int, db: Session = Depends(get_db)):
    log_step(f"Processing checkout for Cart {cart_id}")
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.status == "active").first()
    if not cart or not cart.items: raise HTTPException(status_code=400, detail="Invalid/Empty cart")
    cart.status = "checked_out"
    db.commit()
    return {"message": "Checkout successful."}

@app.delete("/cart/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    log_step(f"Soft-deleting Cart {cart_id}")
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart: raise HTTPException(status_code=404, detail="Cart not found")
    cart.status = "deleted"
    db.commit()
    return None