from pydantic import BaseModel, EmailStr, Field
from typing import List

# --- Users ---
class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    email: EmailStr
    name: str

# --- Products ---
class ProductCreate(BaseModel):
    name: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    stock: int = Field(ge=0, description="Stock cannot be negative")

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    model_config = {"from_attributes": True}

class StockUpdate(BaseModel):
    stock: int = Field(ge=0, description="New stock quantity")

# --- Cart Items ---
class ItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

class ItemUpdate(BaseModel):
    quantity: int = Field(gt=0, description="New quantity must be greater than 0")

class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_addition: float
    model_config = {"from_attributes": True}

# --- Carts ---
class CartResponse(BaseModel):
    id: int
    user_id: int
    status: str
    items: List[CartItemResponse] = []
    model_config = {"from_attributes": True}
