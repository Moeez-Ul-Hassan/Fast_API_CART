from fastapi import HTTPException

class NameTooLongException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Name cannot exceed 100 characters.")

class InvalidNameException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Name must contain only alphabetic characters.")

class InvalidEmailException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid email format.")

class EmailAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Email already registered.")

class NegativePriceException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Price cannot be negative.")

class NegativeStockException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Stock cannot be negative.")

class InvalidQuantityException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Quantity must be greater than zero.")
