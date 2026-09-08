from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    action: str


class CategoryCB(CallbackData, prefix="cat"):
    category_id: int          # 7-dars: satr kalit o'rniga baza ID si


class ProductCB(CallbackData, prefix="prod"):
    action: str
    product_id: int = 0
    qty: int = 1


class CartCB(CallbackData, prefix="cart"):
    action: str
    product_id: int = 0


class CheckoutCB(CallbackData, prefix="chk"):
    action: str
    value: str = ""
