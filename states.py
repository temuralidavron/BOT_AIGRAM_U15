# ============================================================
#  FSM bosqichlari — Django'dagi Form ning ekvivalenti.
#
#  Bot foydalanuvchidan ketma-ket 4 ta narsa so'raydi.
#  Lekin har bir xabar — ALOHIDA update. Bot "hozir qaysi
#  savoldamiz" ni eslab qolishi kerak. Mana shu — state.
# ============================================================

from aiogram.fsm.state import State, StatesGroup


class Checkout(StatesGroup):
    ism = State()
    telefon = State()
    manzil = State()
    tolov = State()
