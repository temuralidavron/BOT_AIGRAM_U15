# 5-dars — FSM: ko'p qadamli buyurtma

| | |
|---|---|
| **Davomiyligi** | 90 daqiqa |
| **Oldindan kerak** | 4-dars tugagan bo'lsin |
| **Tayyor kod** | `darslar/5-dars/` |
| **Oldingi darsdan farqi** | Bot endi ketma-ket savol bera oladi va javoblarni eslab qoladi |

## Maqsad

Bot foydalanuvchidan **ketma-ket** ism, telefon, manzil va to'lov turini so'rasin,
har birini tekshirsin va oxirida buyurtmani jamlab ko'rsatsin.

## Vazifalar — dars oxirida o'quvchi buni qila oladi

- [ ] `StatesGroup` bilan bosqichlarni e'lon qiladi
- [ ] `state.set_state()` va `state.update_data()` ishlatadi
- [ ] Har bir qadamda validatsiya yozadi va noto'g'ri javobni qaytarib so'raydi
- [ ] Bitta holat uchun **bir nechta** handler yozadi (matn, kontakt, lokatsiya)
- [ ] `/bekor` chiqish yo'lini to'g'ri joyga qo'yadi
- [ ] Nima uchun bot restartdan keyin holatni unutishini tushuntiradi

## Yangi tushunchalar

`StatesGroup` · `State` · `FSMContext` · `set_state` · `update_data` · `get_data` ·
`clear` · `MemoryStorage` · `request_contact` · `request_location` · validatsiya

## Yaratiladigan fayllar

```
mening_botim/
├── states.py                 ← YANGI: bosqichlar
├── handlers/checkout.py      ← YANGI: buyurtma oqimi
├── handlers/__init__.py      ← o'zgaradi: checkout eng birinchi
├── callbacks.py              ← o'zgaradi: CheckoutCB qo'shiladi
└── ...qolganlari o'zgarmaydi
```

---

## 1-qism. Muammoni ko'rsating (10 daqiqa)

**Savol bering:**

> "Bot foydalanuvchidan ismini so'radi. Foydalanuvchi 'Ali' deb yozdi.
> Keyingi xabar kelganda bot qayerdan biladi — bu ismmi yoki telefon raqammi?"

O'quvchilar o'ylasin. Keyin ayting:

> "Bilmaydi. Har bir xabar — **alohida, mustaqil update**. Bot xotirasiz.
> Shuning uchun 'hozir qaysi savoldamiz' degan ma'lumotni biror joyda saqlashi kerak."

**Doskaga chizing:**

```
Foydalanuvchi:  "Ali"          →  bot: bu nima? ism? manzil?
                                    ↓
                        state = Checkout.ism  ← bot shuni biladi
                                    ↓
                              demak bu ISM
```

> "Bu — **FSM**, ya'ni holatlar mashinasi. Django'da bunga eng yaqin narsa —
> ko'p sahifali forma yoki `request.session`."

---

## 2-qism. Bosqichlarni e'lon qilamiz (10 daqiqa)

```bash
touch states.py
```

```python
from aiogram.fsm.state import State, StatesGroup


class Checkout(StatesGroup):
    ism = State()
    telefon = State()
    manzil = State()
    tolov = State()
```

**Tushuntiring:**

> "Bu shunchaki nomlar ro'yxati. `Checkout.ism` — bu satr `'Checkout:ism'`.
> Bot foydalanuvchi uchun shu satrni eslab qoladi."

**Muhim savol bering:**

> "Bot 100 ta foydalanuvchiga xizmat qilyapti. Holat qanday saqlanadi —
> hammasi uchun bittami?"

Javob: yo'q. Kalit — **`(bot_id, chat_id, user_id)`** uchligi. Har kimning
holati alohida.

### `main.py` da storage

```python
from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())
```

> "`MemoryStorage` — holat operativ xotirada. Bot restart bo'lsa — yo'qoladi.
> Production'da `RedisStorage` ishlatiladi, u restartdan keyin ham saqlanadi."

---

## 3-qism. Birinchi qadam (15 daqiqa)

`handlers/checkout.py`:

```python
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import storage
from callbacks import CartCB
from states import Checkout

router = Router(name="checkout")


@router.callback_query(CartCB.filter(F.action == "checkout"))
async def boshlash(call: CallbackQuery, state: FSMContext):
    if not storage.olish(call.from_user.id):
        return await call.answer("Savat bo'sh", show_alert=True)

    await state.set_state(Checkout.ism)
    await call.message.answer("👤 Ismingizni kiriting:", reply_markup=bekor_kb())
    await call.answer()
```

**`state: FSMContext` argumentini ko'rsating:**

> "4-darsda `callback_data` argumentini aiogram o'zi to'ldirgan edi. Bu ham
> xuddi shunday — `state` deb nomlasangiz, aiogram o'zi beradi."

### Ismni qabul qilish

```python
@router.message(Checkout.ism, F.text)
async def ism(message: Message, state: FSMContext):
    qiymat = (message.text or "").strip()
    if len(qiymat) < 3:
        return await message.answer("❌ Ism kamida 3 ta harf bo'lsin. Qayta kiriting:")

    await state.update_data(ism=qiymat)
    await state.set_state(Checkout.telefon)
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=telefon_kb())
```

**Ikkita filtrni ko'rsating:**

```python
@router.message(Checkout.ism, F.text)
#               └──────┬─────┘  └──┬──┘
#            "faqat shu holatda"  "va matn bo'lsa"
```

> "Ikkalasi ham bajarilishi kerak. Boshqa holatdagi foydalanuvchi bu handler'ga
> tushmaydi."

**Validatsiya naqshini alohida ta'kidlang:**

```python
if len(qiymat) < 3:
    return await message.answer("❌ ...")     # ← state O'ZGARMAYDI
```

> "Diqqat: xato bo'lsa `set_state` chaqirilmaydi. Foydalanuvchi **shu holatda
> qoladi** va qayta yozadi. Bu — FSM'ning asosiy naqshi."

---

## 4-qism. Bitta holat — bir nechta handler (20 daqiqa)

Telefon ikki xil kelishi mumkin: tugma orqali **kontakt** yoki qo'lda **matn**.

```python
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
    await message.answer("📍 Manzilni yuboring...", reply_markup=manzil_kb())
```

**`_` bilan boshlangan nom** — bu handler emas, yordamchi funksiya. Ikkalasi
bir xil ishni qiladi, takrorlamaslik uchun ajratdik.

### Telefonni tekshirish

```python
import re

def telefon_tekshir(matn: str) -> str | None:
    raqamlar = re.sub(r"\D", "", matn or "")     # faqat raqamlarni qoldiradi
    if len(raqamlar) == 9:
        raqamlar = "998" + raqamlar              # 901112233 -> 998901112233
    return "+" + raqamlar if len(raqamlar) == 12 and raqamlar.startswith("998") else None
```

Doskada sinab ko'ring:

| Kiritilgan | Natija |
|---|---|
| `+998901112233` | `+998901112233` |
| `901112233` | `+998901112233` |
| `90 111 22 33` | `+998901112233` |
| `12345` | `None` → xato |

---

## 5-qism. Lokatsiya va HAQIQIY TUZOQ (20 daqiqa)

> Bu qismni albatta o'ting — o'quvchilaringiz shunga duch keladi.

### Uchta handler kerak

```python
@router.message(Checkout.manzil, F.location)      # xaritadan pin
async def manzil_pin(message: Message, state: FSMContext):
    await state.update_data(
        manzil=f"📍 {message.location.latitude:.4f}, {message.location.longitude:.4f}")
    await _tolovga_otish(message, state)


@router.message(Checkout.manzil, F.text)          # matnli manzil
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


@router.message(Checkout.manzil)                  # rasm, stiker, ovoz...
async def manzil_notogri(message: Message):
    await message.answer("❌ Lokatsiya yuboring yoki manzilni matn bilan yozing.")
```

### Tuzoqni ko'rsating

Kompyuterdagi Telegram'dan `📍 Lokatsiya yuborish` tugmasini bosing.

**Natija:** hech nima bo'lmaydi.

**Ayting:**

> "Bu bot xatosi emas. `request_location` tugmasi **faqat telefondagi Telegramda**
> ishlaydi. Kompyuterda va brauzerda u umuman hech nima qilmaydi — bu Telegram
> platformasining cheklovi.
>
> Foydalanuvchi buni bilmaydi. U bosadi, hech nima bo'lmaydi, va 'bot buzuq'
> deb o'ylab ketib qoladi. Shuning uchun biz **oldindan aytamiz** va matnli
> muqobil beramiz."

### Ikkinchi tuzoq

Telefondan `📍 Lokatsiya yuborish` yozuvini **matn qilib** yuboring.

Agar `qiymat == "📍 Lokatsiya yuborish"` tekshiruvi bo'lmasa — bu satr
**manzil sifatida bazaga tushib ketadi**.

> "Umumiy qoida: FSM ichida **tugma yorlig'i matn sifatida kelib qolishi**ni
> doim hisobga oling."

### Uchinchi handler nima uchun kerak

Foydalanuvchi stiker yubordi. `F.location` ham, `F.text` ham mos kelmadi.
Filtrsiz uchinchi handler bo'lmasa — bot **jim qoladi**.

---

## 6-qism. Chiqish yo'li va yakun (15 daqiqa)

### `/bekor` — eng birinchi

```python
@router.message(Command("bekor"))
@router.message(F.text == BTN_BEKOR)
async def bekor(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("↩️ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Asosiy menyu:",
                         reply_markup=kb.bosh_menyu(storage.dona(message.from_user.id)))
```

### `handlers/__init__.py` — yangi tartib

```python
def register(dp: Dispatcher) -> None:
    dp.include_router(checkout.router)   # FSM + /bekor — ENG BIRINCHI
    dp.include_router(cart.router)
    dp.include_router(catalog.router)
    dp.include_router(common.router)     # /start + FALLBACK — eng oxirida
```

**Nima uchun checkout birinchi** — sinab ko'rsating: uni pastga tushiring,
FSM ichida `/bekor` yozing → ishlamaydi, foydalanuvchi qamalib qoladi.

### `common.py` da bitta o'zgarish

```python
@router.message(F.text, StateFilter(None))     # ← StateFilter qo'shildi
async def boshqa(message: Message):
    ...
```

> "Usiz fallback FSM ichidagi javoblarni ham ushlab oladi. `StateFilter(None)`
> — 'faqat hech qanday holatda bo'lmaganda ishla' degani."

### Tasdiq va yakun

```python
@router.callback_query(CheckoutCB.filter(F.action == "submit"))
async def tasdiq(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    jami = storage.jami(call.from_user.id)

    storage.tozalash(call.from_user.id)
    await state.clear()                        # ← MAJBURIY

    await call.message.edit_text(
        f"🎉 <b>Buyurtma qabul qilindi!</b>\n\n"
        f"👤 {data['ism']}\n📱 {data['telefon']}\n📍 {data['manzil']}\n"
        f"💳 <b>{narx(jami)}</b>"
    )
    await call.answer("✅")
```

> "`state.clear()` ni unutmang. Aks holda keyingi buyurtmada eski ma'lumot chiqadi."

---

## 7-qism. Restart sinovi (5 daqiqa)

1. Buyurtmani boshlang, ismni yozing
2. Botni `Ctrl+C` bilan to'xtating
3. Qayta ishga tushiring
4. Telefon raqam yozing

**Natija:** bot tushunmaydi, "Menyudan tanlang" deydi.

> "Chunki `MemoryStorage` — xotirada. Bot o'chganda holat yo'qoldi.
> Production'da `RedisStorage` ishlatiladi. Buni 14-darsda ko'ramiz."

---

## Dars natijasi

To'liq oqim ishlaydi:

```
🧺 Savat → ✅ Buyurtma berish → ism → telefon → manzil → to'lov → tasdiq
```

Har bir qadamda validatsiya bor, `/bekor` har joyda ishlaydi.

Tayyor kod: `darslar/5-dars/`

---

## Uy vazifasi

1. Oqimga **izoh** qadamini qo'shing (manzildan keyin), `⏭ O'tkazib yuborish` tugmasi bilan
2. Har bir qadamga **`⬅️ Orqaga`** tugmasini qo'shing — oldingi savolga qaytsin
3. Ism qadamida raqam yozib bo'lmasin (`Ali123` rad etilsin)
4. Tasdiq ekranida savat tarkibini ham chiqaring

---

## Tez-tez chiqadigan xatolar

| Xato | Sabab | Yechim |
|---|---|---|
| Bot FSM'da javob bermayapti | Shu holat uchun handler yo'q | Filtrsiz "qolgan hammasi" handler qo'shing |
| `/bekor` ishlamayapti | checkout router pastda | Uni eng birinchi ulang |
| Keyingi buyurtmada eski ma'lumot | `state.clear()` chaqirilmagan | Yakunda albatta chaqiring |
| Fallback FSM javoblarini yutyapti | `StateFilter(None)` yo'q | Fallback'ga qo'shing |
| `KeyError: 'ism'` | `update_data` chaqirilmagan | Har qadamda saqlanayotganini tekshiring |
| Restartdan keyin holat yo'qoldi | `MemoryStorage` | To'g'ri ishlayapti. Redis — 14-darsda |
