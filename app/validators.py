import re
from exceptions import (
    NameTooLongException,
    InvalidNameException,
    InvalidEmailException,
    NegativePriceException,
    NegativeStockException,
    InvalidQuantityException
)

def validate_name(name: str):
    if len(name) > 100:
        raise NameTooLongException()
    if not re.fullmatch(r"[A-Za-z ]+", name):
        raise InvalidNameException()

def validate_email(email: str):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$"
    if not re.fullmatch(email_pattern, email):
        raise InvalidEmailException()

def validate_price(price: float):
    if price < 0:
        raise NegativePriceException()

def validate_stock(stock: int):
    if stock < 0:
        raise NegativeStockException()

def validate_quantity(quantity: int):
    if quantity <= 0:
        raise InvalidQuantityException()