# ============================================================
#  CallbackData factory — satr o'rniga TIPLI obyekt
#
#  Oldin (3-dars):  callback_data=f"mah:{m['id']}"      -> qo'lda parslash
#  Endi:            ProductCB(action="open", product_id=1).pack()
#
#  Foydasi: tip xatosi bo'lmaydi, 64 bayt limiti nazorat qilinadi,
#           handler'ga tayyor obyekt kelib tushadi.
# ============================================================

from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    action: str                    # categories | cart | noop


class CategoryCB(CallbackData, prefix="cat"):
    key: str


class ProductCB(CallbackData, prefix="prod"):
    action: str                    # open | add | inc | dec
    product_id: int = 0
    qty: int = 1


class CartCB(CallbackData, prefix="cart"):
    action: str                    # inc | dec | del | clear | checkout
    product_id: int = 0


class CheckoutCB(CallbackData, prefix="chk"):
    action: str                    # payment | submit | abort
    value: str = ""
