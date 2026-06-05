from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from logger import logger

# Import Custom Validators and Exceptions
from validators import validate_name, validate_email, validate_price, validate_stock, validate_quantity
from exceptions import EmailAlreadyExistsException

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cart API")


# 1. USERS

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    validate_name(user.name)
    validate_email(user.email)

    if db.query(models.User).filter(models.User.email == user.email).first():
        raise EmailAlreadyExistsException()
        
    new_user = models.User(email=user.email, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    validate_name(user_update.name)
    validate_email(user_update.email)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    
    user.email = user_update.email
    user.name = user_update.name
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
        
    [db.delete(cart) for cart in db.query(models.Cart).filter(models.Cart.user_id == user_id).all()]
    db.delete(user)
    db.commit()
    return None


# 2. PRODUCTS

@app.post("/products/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    validate_price(product.price)
    validate_stock(product.stock)

    new_product = models.Product(name=product.name, price=product.price, stock=product.stock)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products/", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product: 
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.patch("/products/{product_id}/stock", response_model=schemas.ProductResponse)
def update_stock(product_id: int, data: schemas.StockUpdate, db: Session = Depends(get_db)):
    validate_stock(data.stock)
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product: 
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.stock = data.stock
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product: 
        raise HTTPException(status_code=404, detail="Product not found")
        
    db.delete(product)
    db.commit()
    return None



# 3. CARTS & ITEMS

@app.post("/users/{user_id}/cart/", response_model=schemas.CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if db.query(models.Cart).filter(models.Cart.user_id == user_id, models.Cart.status == "active").first():
        raise HTTPException(status_code=400, detail="User already has an active cart.")
    
    new_cart = models.Cart(user_id=user_id, status="active")
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    return new_cart

@app.get("/cart/{cart_id}", response_model=schemas.CartResponse)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart: 
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@app.post("/cart/{cart_id}/items/", response_model=schemas.CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(cart_id: int, item: schemas.ItemAdd, db: Session = Depends(get_db)):
    validate_quantity(item.quantity)
    
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.status == "active").first()
    if not cart: 
        raise HTTPException(status_code=404, detail="Active cart not found")
        
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product: 
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < item.quantity: 
        raise HTTPException(status_code=400, detail="Insufficient stock")

    new_item = models.CartItem(cart_id=cart_id, product_id=item.product_id, quantity=item.quantity, price_at_addition=product.price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.post("/cart/{cart_id}/checkout")
def checkout_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.status == "active").first()
    
    if not cart: 
        raise HTTPException(status_code=404, detail="Active Cart not found")
    if not cart.items: 
        raise HTTPException(status_code=400, detail="Cannot checkout an empty cart.")
    
    for item in cart.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        
        if not product or product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Checkout failed: Product ID {item.product_id} only has {product.stock if product else 0} units left in stock."
            )
            
        product.stock -= item.quantity

    cart.status = "checked_out"
    db.commit()
    
    return {"message": "Checkout successful. Inventory has been deducted."}

@app.delete("/cart/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart: 
        raise HTTPException(status_code=404, detail="Cart not found")
        
    cart.status = "deleted"
    db.commit()
    return None