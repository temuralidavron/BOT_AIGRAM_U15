# ============================================================
#  5-DARS — FSM: buyurtma rasmiylashtirish
#
#  OQIM:  ism -> telefon -> manzil -> to'lov -> tasdiq
#
#  E'TIBOR BERING:
#   1. Har bir qadamda VALIDATSIYA bor (noto'g'ri bo'lsa qaytarib so'raydi)
#   2. Manzil qadamida UCHTA handler: lokatsiya, matn, "qolgan hammasi"
#   3. /bekor buyrug'i ENG BIRINCHI — foydalanuvchi qamalib qolmasin
# ============================================================

import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import keyboards as kb
import storage
from callbacks import CartCB, CheckoutCB
from services import narx
from states import Checkout

router = Router(name="checkout")

BTN_BEKOR = "❌ Bekor qilish"


def bekor_kb():
    k = ReplyKeyboardBuilder()
    k.row(KeyboardButton(text=BTN_BEKOR))
    return k.as_markup(resize_keyboard=True)


def telefon_kb():
    k = ReplyKeyboardBuilder()
    k.row(KeyboardButton(text="📱 Raqamni yuborish", request_contact=True))
    k.row(KeyboardButton(text=BTN_BEKOR))
    return k.as_markup(resize_keyboard=True)


def manzil_kb():
    k = ReplyKeyboardBuilder()
    k.row(KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True))
    k.row(KeyboardButton(text=BTN_BEKOR))
    return k.as_markup(resize_keyboard=True)


def tolov_kb():
    k = InlineKeyboardBuilder()
    k.button(text="💵 Naqd", callback_data=CheckoutCB(action="payment", value="naqd"))
    k.button(text="💳 Karta", callback_data=CheckoutCB(action="payment", value="karta"))
    k.adjust(2)
    return k.as_markup()


def tasdiq_kb():
    k = InlineKeyboardBuilder()
    k.button(text="✅ Tasdiqlash", callback_data=CheckoutCB(action="submit"))
    k.button(text="❌ Bekor qilish", callback_data=CheckoutCB(action="abort"))
    k.adjust(1)
    return k.as_markup()


def telefon_tekshir(matn: str) -> str | None:
    raqamlar = re.sub(r"\D", "", matn or "")
    if len(raqamlar) == 9:
        raqamlar = "998" + raqamlar
    return "+" + raqamlar if len(raqamlar) == 12 and raqamlar.startswith("998") else None


# ---------- BEKOR QILISH — eng birinchi, har qanday holatda ----------
@router.message(Command("bekor"))
@router.message(F.text == BTN_BEKOR)
async def bekor(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("↩️ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Asosiy menyu:",
                         reply_markup=kb.bosh_menyu(storage.dona(message.from_user.id)))


# ---------- 1-qadam: boshlash ----------
@router.callback_query(CartCB.filter(F.action == "checkout"))
async def boshlash(call: CallbackQuery, state: FSMContext):
    if not storage.xom(call.from_user.id):
        return await call.answer("Savat bo'sh", show_alert=True)

    await state.set_state(Checkout.ism)
    await call.message.answer("👤 Ismingizni kiriting:", reply_markup=bekor_kb())
    await call.answer()


# ---------- 2-qadam: ism ----------
@router.message(Checkout.ism, F.text)
async def ism(message: Message, state: FSMContext):
    qiymat = (message.text or "").strip()
    if len(qiymat) < 3:
        return await message.answer("❌ Ism kamida 3 ta harf bo'lsin. Qayta kiriting:")

    await state.update_data(ism=qiymat)
    await state.set_state(Checkout.telefon)
    await message.answer("📱 Telefon raqamingizni yuboring:\n\n"
                         "Tugmani bosing yoki <code>+998901234567</code> ko'rinishida yozing.",
                         reply_markup=telefon_kb())


# ---------- 3-qadam: telefon (kontakt YOKI matn) ----------
@router.message(Checkout.telefon, F.contact)
async def telefon_kontakt(message: Message, state: FSMContext):
    await _telefon_saqlash(message, state, message.contact.phone_number)


@router.message(Checkout.telefon, F.text)
async def telefon_matn(message: Message, state: FSMContext):
    await _telefon_saqlash(message, state, message.text)


async def _telefon_saqlash(message: Message, state: FSMContext, xom: str):
    raqam = telefon_tekshir(xom)
    if not raqam:
        return await message.answer("❌ Raqam noto'g'ri.\nNamuna: <code>+998901234567</code>")

    await state.update_data(telefon=raqam)
    await state.set_state(Checkout.manzil)
    await message.answer(
        "📍 <b>Manzilni yuboring</b>\n\n"
        "<b>1-usul.</b> «📍 Lokatsiya yuborish» tugmasi — <i>faqat telefondagi "
        "Telegramda ishlaydi, kompyuterda emas.</i>\n\n"
        "<b>2-usul.</b> Manzilni matn bilan yozing:\n"
        "<code>Chilonzor 9-kvartal, 42-uy</code>",
        reply_markup=manzil_kb(),
    )


# ---------- 4-qadam: manzil (UCHTA handler!) ----------
@router.message(Checkout.manzil, F.location)
async def manzil_pin(message: Message, state: FSMContext):
    await state.update_data(
        manzil=f"📍 {message.location.latitude:.4f}, {message.location.longitude:.4f}")
    await _tolovga_otish(message, state)


@router.message(Checkout.manzil, F.text)
async def manzil_matn(message: Message, state: FSMContext):
    qiymat = (message.text or "").strip()
    if qiymat == "📍 Lokatsiya yuborish":
        return await message.answer(
            "🖥 Kompyuterdagi Telegram lokatsiya yubora olmaydi.\n\n"
            "Manzilni matn bilan yozing: <code>Chilonzor 9-kvartal, 42-uy</code>")
    if len(qiymat) < 5:
        return await message.answer("❌ Manzil kamida 5 ta belgi bo'lsin.")

    await state.update_data(manzil=qiymat)
    await _tolovga_otish(message, state)


@router.message(Checkout.manzil)
async def manzil_notogri(message: Message):
    await message.answer("❌ Lokatsiya yuboring yoki manzilni matn bilan yozing.")


async def _tolovga_otish(message: Message, state: FSMContext):
    await state.set_state(Checkout.tolov)
    await message.answer("Qabul qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer("💳 To'lov turini tanlang:", reply_markup=tolov_kb())


# ---------- 5-qadam: to'lov ----------
@router.callback_query(Checkout.tolov, CheckoutCB.filter(F.action == "payment"))
async def tolov(call: CallbackQuery, callback_data: CheckoutCB, state: FSMContext):
    await state.update_data(tolov=callback_data.value)
    data = await state.get_data()

    from handlers.cart import savat_elementlari
    elementlar = await savat_elementlari(call.from_user.id)
    qatorlar = "\n".join(f"{i}. {e['nom']} — {e['soni']} x {narx(e['narx'])}"
                         for i, e in enumerate(elementlar, 1))
    jami = sum(e["summa"] for e in elementlar)

    await call.message.edit_text(
        f"🧾 <b>Buyurtmani tasdiqlang</b>\n\n{qatorlar}\n\n"
        f"➖➖➖➖➖➖➖➖\n"
        f"💳 Jami: <b>{narx(jami)}</b>\n\n"
        f"👤 {data['ism']}\n📱 {data['telefon']}\n📍 {data['manzil']}\n"
        f"💵 {data['tolov'].capitalize()}",
        reply_markup=tasdiq_kb(),
    )
    await call.answer()


# ---------- 6-qadam: tasdiq ----------
@router.callback_query(CheckoutCB.filter(F.action == "submit"))
async def tasdiq(call: CallbackQuery, state: FSMContext):
    from handlers.cart import savat_elementlari
    data = await state.get_data()
    jami = sum(e["summa"] for e in await savat_elementlari(call.from_user.id))

    storage.tozalash(call.from_user.id)
    await state.clear()

    await call.message.edit_text(
        f"🎉 <b>Buyurtma qabul qilindi!</b>\n\n"
        f"👤 {data['ism']}\n📱 {data['telefon']}\n📍 {data['manzil']}\n"
        f"💳 <b>{narx(jami)}</b>\n\n"
        f"<i>Hozircha buyurtma hech qayerga saqlanmadi — "
        f"bazani 6-darsda qo'shamiz.</i>"
    )
    await call.message.answer("Asosiy menyu:", reply_markup=kb.bosh_menyu(0))
    await call.answer("✅")


@router.callback_query(CheckoutCB.filter(F.action == "abort"))
async def abort(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("↩️ Buyurtma bekor qilindi.")
    await call.answer()
