import logging

logging.basicConfig(
    filename="cart.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("cart-api")