# ============================================================
#  TARTIB QOIDASI (4-darsdan):  tordan kengga.
#
#  5-darsda yangi qoida qo'shildi:
#    FSM router'i — ENG BIRINCHI.
#    Sabab: /bekor buyrug'i har qanday holatda ishlashi kerak.
#    Agar u pastda tursa, foydalanuvchi FSM ichida qamalib qoladi.
# ============================================================

from aiogram import Dispatcher

from handlers import cart, catalog, checkout, common


def register(dp: Dispatcher) -> None:
    dp.include_router(checkout.router)   # FSM + /bekor — ENG BIRINCHI
    dp.include_router(cart.router)
    dp.include_router(catalog.router)
    dp.include_router(common.router)     # /start + FALLBACK — eng oxirida
