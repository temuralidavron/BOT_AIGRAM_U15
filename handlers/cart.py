# ============================================================
#  7-DARS — Savat endi baza bilan "birlashtiriladi".
#
#  storage faqat {id: soni} biladi.
#  Nom va narx bazadan olinadi va shu yerda birlashtiriladi.
# ============================================================

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import services
import storage
from callbacks import CartCB, MenuCB
from services import narx

router = Router(name="cart")


async def savat_elementlari(user_id: int) -> list[dict]:
    """{id: soni} + bazadagi ma'lumot = to'liq savat."""
    xom = storage.xom(user_id)
    if not xom:
        return []
    mahsulotlar = await services.mahsulotlar_by_ids(list(xom))
    natija = []
    for mahsulot_id, soni in xom.items():
        m = mahsulotlar.get(mahsulot_id)
        if m:                                  # mahsulot o'chirilgan bo'lishi mumkin
            natija.append({**m, "soni": soni, "summa": m["narx"] * soni})
    return natija


def savat_matni(elementlar: list[dict]) -> str:
    qatorlar = [
        f"{i}. {e['nom']}\n    {e['soni']} x {narx(e['narx'])} = <b>{narx(e['summa'])}</b>"
        for i, e in enumerate(elementlar, 1)
    ]
    jami = sum(e["summa"] for e in elementlar)
    return ("🧺 <b>Savatingiz</b>\n\n" + "\n".join(qatorlar) +
            f"\n\n➖➖➖➖➖➖➖➖\n💳 Jami: <b>{narx(jami)}</b>")


async def korsatish(target: Message | CallbackQuery, user_id: int):
    elementlar = await savat_elementlari(user_id)
    if not elementlar:
        matn, markup = "🧺 Savatingiz bo'sh.\n\nMenyudan biror narsa tanlang!", None
    else:
        matn, markup = savat_matni(elementlar), kb.savat(elementlar)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(matn, reply_markup=markup)
    else:
        await target.answer(matn, reply_markup=markup)


@router.message(F.text.startswith(kb.BTN_SAVAT))
async def savat_matn(message: Message):
    await korsatish(message, message.from_user.id)


@router.callback_query(MenuCB.filter(F.action == "cart"))
async def savat_callback(call: CallbackQuery):
    await korsatish(call, call.from_user.id)
    await call.answer()


@router.callback_query(CartCB.filter(F.action.in_({"inc", "dec"})))
async def sonini_ozgartirish(call: CallbackQuery, callback_data: CartCB):
    farq = 1 if callback_data.action == "inc" else -1
    storage.ozgartirish(call.from_user.id, callback_data.product_id, farq)
    await korsatish(call, call.from_user.id)
    await call.answer()


@router.callback_query(CartCB.filter(F.action == "del"))
async def ochirish(call: CallbackQuery, callback_data: CartCB):
    storage.ochirish(call.from_user.id, callback_data.product_id)
    await korsatish(call, call.from_user.id)
    await call.answer("🗑 O'chirildi")


@router.callback_query(CartCB.filter(F.action == "clear"))
async def tozalash(call: CallbackQuery):
    storage.tozalash(call.from_user.id)
    await call.message.edit_text("🧺 Savat tozalandi.")
    await call.answer()
