from aiogram import F, Router
from aiogram.types import CallbackQuery

import keyboards as kb
import storage
from callbacks import CategoryCB, MenuCB, ProductCB
from data import CATEGORIES, mahsulot_top, narx

router = Router(name="catalog")

MAX_SONI = 20


@router.callback_query(MenuCB.filter(F.action == "categories"))
async def kategoriyalar(call: CallbackQuery):
    await call.message.edit_text("🍽 <b>Menyu</b>\n\nKategoriyani tanlang:",
                                 reply_markup=kb.kategoriyalar())
    await call.answer()


@router.callback_query(MenuCB.filter(F.action == "noop"))
async def noop(call: CallbackQuery):
    # "2 ta" yozuvi ham tugma — bosilganda hech nima bo'lmasligi kerak,
    # lekin answer() baribir chaqiriladi, aks holda soat aylanaveradi.
    await call.answer()


@router.callback_query(CategoryCB.filter())
async def kategoriya(call: CallbackQuery, callback_data: CategoryCB):
    k = CATEGORIES.get(callback_data.key)
    if not k:
        return await call.answer("Kategoriya topilmadi", show_alert=True)
    await call.message.edit_text(f"<b>{k['nom']}</b>\n\nMahsulotni tanlang:",
                                 reply_markup=kb.mahsulotlar(callback_data.key))
    await call.answer()


async def _kartani_chizish(call: CallbackQuery, product_id: int, qty: int):
    m = mahsulot_top(product_id)
    if not m:
        return await call.answer("Mahsulot topilmadi", show_alert=True)
    savatda = next((x["soni"] for x in storage.olish(call.from_user.id)
                    if x["id"] == product_id), 0)
    await call.message.edit_text(
        f"<b>{m['nom']}</b>\n\n{m['tavsif']}\n\n"
        f"💰 Narxi: <b>{narx(m['narx'])}</b>\n"
        f"🧺 Savatda: <b>{savatda} ta</b>",
        reply_markup=kb.mahsulot_kartasi(product_id, qty),
    )


@router.callback_query(ProductCB.filter(F.action == "open"))
async def mahsulot(call: CallbackQuery, callback_data: ProductCB):
    await _kartani_chizish(call, callback_data.product_id, 1)
    await call.answer()


@router.callback_query(ProductCB.filter(F.action.in_({"inc", "dec"})))
async def sonini_ozgartirish(call: CallbackQuery, callback_data: ProductCB):
    qadam = 1 if callback_data.action == "inc" else -1
    qty = max(1, min(MAX_SONI, callback_data.qty + qadam))
    if qty == callback_data.qty:
        return await call.answer(f"1 dan {MAX_SONI} gacha")
    await call.message.edit_reply_markup(
        reply_markup=kb.mahsulot_kartasi(callback_data.product_id, qty))
    await call.answer()


@router.callback_query(ProductCB.filter(F.action == "add"))
async def savatga(call: CallbackQuery, callback_data: ProductCB):
    yangi = storage.qoshish(call.from_user.id, callback_data.product_id, callback_data.qty)
    m = mahsulot_top(callback_data.product_id)
    await call.answer(f"✅ {m['nom']} — savatda {yangi} ta")
    await _kartani_chizish(call, callback_data.product_id, callback_data.qty)
