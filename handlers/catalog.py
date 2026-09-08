# ============================================================
#  7-DARS — Handler endi SERVIS orqali ishlaydi.
#
#  Taqqoslang:
#    6-dars:  CATEGORIES[kalit]["mahsulotlar"]      ← lug'atdan
#    7-dars:  await services.mahsulotlar(kat_id)    ← bazadan
#
#  Handler'da bitta ham `.objects.` yo'q — bu qoida.
# ============================================================

from aiogram import F, Router
from aiogram.types import CallbackQuery

import keyboards as kb
import services
import storage
from callbacks import CategoryCB, MenuCB, ProductCB
from services import narx

router = Router(name="catalog")

MAX_SONI = 20


@router.callback_query(MenuCB.filter(F.action == "categories"))
async def kategoriyalar(call: CallbackQuery):
    royxat = await services.kategoriyalar()
    if not royxat:
        return await call.answer("Katalog bo'sh", show_alert=True)
    await call.message.edit_text("🍽 <b>Menyu</b>\n\nKategoriyani tanlang:",
                                 reply_markup=kb.kategoriyalar(royxat))
    await call.answer()


@router.callback_query(MenuCB.filter(F.action == "noop"))
async def noop(call: CallbackQuery):
    await call.answer()


@router.callback_query(CategoryCB.filter())
async def kategoriya(call: CallbackQuery, callback_data: CategoryCB):
    k = await services.kategoriya_top(callback_data.category_id)
    if not k:
        return await call.answer("Kategoriya topilmadi", show_alert=True)

    royxat = await services.mahsulotlar(k["id"])
    if not royxat:
        return await call.answer("Bu kategoriyada mahsulot yo'q", show_alert=True)

    await call.message.edit_text(f"<b>{k['toliq_nom']}</b>\n\nMahsulotni tanlang:",
                                 reply_markup=kb.mahsulotlar(royxat))
    await call.answer()


async def _kartani_chizish(call: CallbackQuery, mahsulot_id: int, qty: int):
    m = await services.mahsulot_top(mahsulot_id)
    if not m:
        return await call.answer("Mahsulot topilmadi", show_alert=True)
    savatda = storage.soni(call.from_user.id, mahsulot_id)
    await call.message.edit_text(
        f"<b>{m['nom']}</b>\n\n{m['tavsif'] or '—'}\n\n"
        f"💰 Narxi: <b>{narx(m['narx'])}</b>\n"
        f"🧺 Savatda: <b>{savatda} ta</b>",
        reply_markup=kb.mahsulot_kartasi(mahsulot_id, qty),
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
    m = await services.mahsulot_top(callback_data.product_id)
    if not m:
        return await call.answer("Mahsulot topilmadi", show_alert=True)
    yangi = storage.qoshish(call.from_user.id, callback_data.product_id, callback_data.qty)
    await call.answer(f"✅ {m['nom']} — savatda {yangi} ta")
    await _kartani_chizish(call, callback_data.product_id, callback_data.qty)
