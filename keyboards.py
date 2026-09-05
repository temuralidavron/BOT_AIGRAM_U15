# ============================================================
#  Barcha klaviaturalar SHU YERDA.
#  Handler'da tugma yasalmaydi — faqat chaqiriladi.
#  Sabab: dizaynni bir joydan o'zgartirasiz.
# ============================================================

from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from callbacks import CartCB, CategoryCB, MenuCB, ProductCB
from data import CATEGORIES, narx

BTN_MENYU = "🍽 Menyu"
BTN_SAVAT = "🧺 Savat"
BTN_PROFIL = "👤 Profil"


def bosh_menyu(savatda: int = 0) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    savat_matni = f"{BTN_SAVAT} ({savatda})" if savatda else BTN_SAVAT
    kb.row(KeyboardButton(text=BTN_MENYU), KeyboardButton(text=savat_matni))
    kb.row(KeyboardButton(text=BTN_PROFIL))
    return kb.as_markup(resize_keyboard=True)


def kategoriyalar() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for kalit, k in CATEGORIES.items():
        kb.button(text=k["nom"], callback_data=CategoryCB(key=kalit))
    kb.adjust(2)
    kb.row()
    kb.button(text="🧺 Savat", callback_data=MenuCB(action="cart"))
    return kb.as_markup()


def mahsulotlar(kalit: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for m in CATEGORIES[kalit]["mahsulotlar"]:
        kb.button(text=f"{m['nom']} — {narx(m['narx'])}",
                  callback_data=ProductCB(action="open", product_id=m["id"]))
    kb.adjust(1)
    kb.row()
    kb.button(text="🔙 Kategoriyalar", callback_data=MenuCB(action="categories"))
    kb.button(text="🧺 Savat", callback_data=MenuCB(action="cart"))
    return kb.as_markup()


def mahsulot_kartasi(product_id: int, qty: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➖", callback_data=ProductCB(action="dec", product_id=product_id, qty=qty))
    kb.button(text=f"{qty} ta", callback_data=MenuCB(action="noop"))
    kb.button(text="➕", callback_data=ProductCB(action="inc", product_id=product_id, qty=qty))
    kb.adjust(3)
    pastki = InlineKeyboardBuilder()
    pastki.button(text=f"🛒 Savatga qo'shish ({qty})",
                  callback_data=ProductCB(action="add", product_id=product_id, qty=qty))
    pastki.button(text="🔙 Orqaga", callback_data=MenuCB(action="categories"))
    pastki.adjust(1)
    kb.attach(pastki)
    return kb.as_markup()


def savat(elementlar: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for e in elementlar:
        kb.button(text="➖", callback_data=CartCB(action="dec", product_id=e["id"]))
        kb.button(text=f"{e['nom'][:14]} · {e['soni']}", callback_data=MenuCB(action="noop"))
        kb.button(text="➕", callback_data=CartCB(action="inc", product_id=e["id"]))
        kb.button(text="🗑", callback_data=CartCB(action="del", product_id=e["id"]))
    kb.adjust(4)
    pastki = InlineKeyboardBuilder()
    pastki.button(text="✅ Buyurtma berish", callback_data=CartCB(action="checkout"))
    pastki.button(text="🍽 Menyu", callback_data=MenuCB(action="categories"))
    pastki.button(text="🗑 Tozalash", callback_data=CartCB(action="clear"))
    pastki.adjust(1, 2)
    kb.attach(pastki)
    return kb.as_markup()
