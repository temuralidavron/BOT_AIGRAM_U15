from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message

import keyboards as kb
import storage

router = Router(name="common")


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Salom, <b>{message.from_user.full_name}</b>!\n\nMenyudan tanlang 👇",
        reply_markup=kb.bosh_menyu(storage.dona(message.from_user.id)),
    )


@router.message(Command("menyu"))
@router.message(F.text == kb.BTN_MENYU)
async def menyu(message: Message):
    await message.answer("🍽 <b>Menyu</b>\n\nKategoriyani tanlang:",
                         reply_markup=kb.kategoriyalar())


@router.message(F.text == kb.BTN_PROFIL)
async def profil(message: Message):
    u = message.from_user
    await message.answer(
        f"👤 <b>Profil</b>\n\nIsm: <b>{u.full_name}</b>\nID: <code>{u.id}</code>\n"
        f"Savatda: <b>{storage.dona(u.id)}</b> dona"
    )


# ENG OXIRGI handler — tanilmagan hamma narsa shu yerga tushadi
@router.message(F.text, StateFilter(None))
async def boshqa(message: Message):
    await message.answer("Menyudan tanlang 👇",
                         reply_markup=kb.bosh_menyu(storage.dona(message.from_user.id)))
