# 7-dars — Botni bazaga ulaymiz: servis qatlami

| | |
|---|---|
| **Davomiyligi** | 90 daqiqa |
| **Oldindan kerak** | 6-dars tugagan bo'lsin |
| **Tayyor kod** | `darslar/7-dars/` |
| **Oldingi darsdan farqi** | Bot endi `data.py` dan emas, **bazadan** o'qiydi |

## Maqsad

Admin panelda narx o'zgartirilsa, bot **darhol** yangi narxni ko'rsatsin.
Kodga tegilmasin, bot qayta ishga tushirilmasin.

## Vazifalar — dars oxirida o'quvchi buni qila oladi

- [ ] `sync_to_async` nima uchun kerakligini tushuntirib beradi
- [ ] Servis qatlamini yozadi va handler'dan chaqiradi
- [ ] Nima uchun servis `dict` qaytarishini asoslaydi
- [ ] Botni `manage.py runbot` orqali ishga tushiradi
- [ ] Handler'da ORM ishlatmaslik qoidasini biladi va sababini aytadi

## Yangi tushunchalar

`sync_to_async` · `SynchronousOnlyOperation` · servis qatlami · `dict` qaytarish ·
management command · `settings.BOT_TOKEN` · `filter(faol=True)`

## Yaratiladigan / o'zgaradigan fayllar

```
mening_botim/
├── services.py                       ← YANGI: baza bilan yagona ko'prik
├── storage.py                        ← o'zgaradi: endi faqat {id: soni}
├── keyboards.py                      ← o'zgaradi: tayyor dict qabul qiladi
├── handlers/catalog.py               ← o'zgaradi: servisdan o'qiydi
├── handlers/cart.py                  ← o'zgaradi: baza bilan birlashtiradi
├── shop/management/commands/runbot.py ← YANGI
├── config/settings.py                ← o'zgaradi: BOT_TOKEN qo'shiladi
├── main.py                           ← O'CHIRILADI
└── data.py                           ← data_eski.py ga aylanadi (faqat seed uchun)
```

---

## 1-qism. Muammoni ko'rsating (10 daqiqa)

`handlers/catalog.py` ni oching va shu qatorni ko'rsating:

```python
from data import CATEGORIES
```

**Ayting:**

> "Kecha butun katalogni bazaga ko'chirdik. Admin panelda narxni o'zgartirdik.
> Lekin bot hali ham `data.py` dan o'qiyapti. Ya'ni bazadagi o'zgarish
> botga ta'sir qilmayapti."

Buni **ko'rsating**: admin panelda narxni 99 000 qiling, botni oching — hali 32 000.

### Birinchi urinish — va u ishlamaydi

`catalog.py` da `from data import CATEGORIES` o'rniga to'g'ridan-to'g'ri yozib ko'ring:

```python
from shop.models import Product

@router.callback_query(ProductCB.filter(F.action == "open"))
async def mahsulot(call: CallbackQuery, callback_data: ProductCB):
    m = Product.objects.get(pk=callback_data.product_id)      # ← shunday qilaylik
    ...
```

Ishga tushiring va tugmani bosing:

```
django.core.exceptions.SynchronousOnlyOperation:
You cannot call this from an async context - use a thread or sync_to_async.
```

### Nima uchun — doskaga chizing

```
Django ORM  →  SINXRON    (so'rov yuborib, javob kelguncha KUTADI)
aiogram     →  ASINXRON   (kutish paytida boshqa ish qiladi)
```

> "Agar asinxron kod ichida sinxron ORM chaqirsak, u butun botni **muzlatib
> qo'yadi** — 100 ta foydalanuvchi bittasini kutib turadi. Django buni oldindan
> sezib, xato beradi: 'bunday qilma'."

**Yechim:** `sync_to_async` — sinxron funksiyani alohida oqimda (thread) ishlatadi,
bot esa kutish paytida boshqa foydalanuvchilarga xizmat qiladi.

---

## 2-qism. Servis qatlami (25 daqiqa)

### Nima uchun alohida fayl

> "Har bir handler'da `sync_to_async` yozib o'tirmaymiz. Bazaga tegadigan
> hamma narsani **bitta faylga** yig'amiz. Bu — Django'dagi `models.py` ning
> manager qismiga o'xshaydi."

`services.py` yarating:

```python
from asgiref.sync import sync_to_async

from shop.models import Category, Product


def narx(son) -> str:
    return f"{int(son):,}".replace(",", " ") + " so'm"


def _mahsulot_dict(m: Product) -> dict:
    return {"id": m.pk, "nom": m.nom, "tavsif": m.tavsif,
            "narx": int(m.narx), "kategoriya_id": m.kategoriya_id}


@sync_to_async
def mahsulotlar(kategoriya_id: int) -> list[dict]:
    qs = Product.objects.filter(kategoriya_id=kategoriya_id, faol=True)
    return [_mahsulot_dict(m) for m in qs]


@sync_to_async
def mahsulot_top(mahsulot_id: int) -> dict | None:
    m = Product.objects.filter(pk=mahsulot_id, faol=True).first()
    return _mahsulot_dict(m) if m else None
```

### ENG MUHIM QOIDA — nima uchun `dict`

**To'xtang. Bu darsning eng muhim 5 daqiqasi.**

Shunday qilib ko'rsating — servis model qaytarsin:

```python
@sync_to_async
def mahsulot_top(mahsulot_id: int) -> Product | None:
    return Product.objects.filter(pk=mahsulot_id).first()      # model qaytardik
```

Handler'da:

```python
m = await services.mahsulot_top(1)
print(m.nom)                    # ishlaydi
print(m.kategoriya.nom)         # ← PORTLAYDI!
```

```
SynchronousOnlyOperation
```

**So'rang:**

> "Nega? `sync_to_async` ishlatdik-ku."

**Javob:**

> "`m.nom` — bu allaqachon o'qilgan ma'lumot, muammo yo'q. Lekin
> `m.kategoriya` — bu **yangi SQL so'rov**. Django uni faqat so'ralganda
> bajaradi, bunga **lazy loading** deyiladi. Va u asinxron kontekstda
> portlaydi."

**Doskaga yozing:**

```
QOIDA: servis handler'ga "jonli" model bermaydi.
       Servis DICT qaytaradi.
```

> "Shunda handler'da tasodifan lazy FK'ga tegib ketish **imkonsiz** bo'ladi.
> Bu qoida sizni o'nlab soatlik xatodan qutqaradi."

### `filter(faol=True)` — sezilmaydigan foyda

```python
Product.objects.filter(kategoriya_id=kategoriya_id, faol=True)
```

> "Admin panelda `faol` belgisini olib tashlash — mahsulotni **o'chirmasdan**
> yashirish. Buyurtmalar tarixi buzilmaydi, lekin botda ko'rinmaydi.
> Bu — mahsulot tugab qolganda kerak bo'ladi."

Amalda ko'rsating: admin panelda `Chizburger` ning `faol` belgisini oching,
botda menyuga qarang — yo'q. Qaytaring — paydo bo'ldi.

---

## 3-qism. Handler'larni ko'chiramiz (20 daqiqa)

### Oldin va keyin — yonma-yon ko'rsating

```python
# 6-dars
kategoriya = CATEGORIES.get(kalit)
royxat = kategoriya["mahsulotlar"]

# 7-dars
k = await services.kategoriya_top(callback_data.category_id)
royxat = await services.mahsulotlar(k["id"])
```

To'liq handler:

```python
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
```

**Ikkita `if` ni ta'kidlang:**

> "Bazadan kelgan narsa **yo'q bo'lishi mumkin**. Lug'atda kalit doim bor edi,
> bazada esa admin o'chirib yuborgan bo'lishi mumkin. Shuning uchun har safar
> tekshiramiz."

### `callbacks.py` da bitta o'zgarish

```python
class CategoryCB(CallbackData, prefix="cat"):
    category_id: int          # oldin: key: str
```

> "Endi kategoriya kaliti — bazadagi `id`, ya'ni son."

### `keyboards.py` — endi ma'lumot tashqaridan keladi

```python
def kategoriyalar(royxat: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for k in royxat:
        kb.button(text=k["toliq_nom"], callback_data=CategoryCB(category_id=k["id"]))
    kb.adjust(2)
    return kb.as_markup()
```

**Muhim qoidani ayting:**

> "Diqqat qiling — bu faylda bitta ham `await` va bitta ham `.objects.` yo'q.
> Klaviatura bazani **bilmaydi**. Unga tayyor ro'yxat beriladi. Bu qatlamlarni
> ajratish deyiladi va u kodni test qilinadigan qiladi."

---

## 4-qism. Savat va baza (15 daqiqa)

### `storage.py` yengillashadi

Oldin savat mahsulot nomini ham bilardi. Endi **faqat id va soni**:

```python
_SAVATLAR: dict[int, dict[int, int]] = {}     # {user_id: {mahsulot_id: soni}}


def xom(user_id: int) -> dict[int, int]:
    return dict(_SAVATLAR.get(user_id, {}))
```

### Birlashtirish `handlers/cart.py` da

```python
async def savat_elementlari(user_id: int) -> list[dict]:
    """{id: soni} + bazadagi ma'lumot = to'liq savat."""
    xom = storage.xom(user_id)
    if not xom:
        return []
    mahsulotlar = await services.mahsulotlar_by_ids(list(xom))
    natija = []
    for mahsulot_id, soni in xom.items():
        m = mahsulotlar.get(mahsulot_id)
        if m:                          # mahsulot o'chirilgan bo'lishi mumkin
            natija.append({**m, "soni": soni, "summa": m["narx"] * soni})
    return natija
```

**Ikkita narsani ta'kidlang:**

1. **Bitta so'rov** — har bir mahsulot uchun alohida emas:
   ```python
   Product.objects.filter(pk__in=idlar)      # 1 ta so'rov
   ```
   > "Agar sikl ichida `mahsulot_top()` chaqirsak, 10 ta mahsulot uchun 10 ta
   > SQL so'rov ketardi. Bunga **N+1 muammosi** deyiladi."

2. **`if m:`** — savatdagi mahsulot bazadan o'chirilgan bo'lishi mumkin

### Eng chiroyli natija

> "Endi narx **har safar bazadan** olinadi. Ya'ni admin panelda narxni
> o'zgartirsangiz, savatdagi summa ham darhol yangilanadi."

Buni sinab ko'rsating — bu darsning eng kuchli lahzasi.

---

## 5-qism. `manage.py runbot` (15 daqiqa)

### Nima uchun `python main.py` endi ishlamaydi

Sinab ko'ring:

```bash
python main.py
```

```
django.core.exceptions.ImproperlyConfigured:
Requested setting INSTALLED_APPS, but settings are not configured.
```

> "Bot endi Django modellaridan foydalanadi. Django esa ishlashidan oldin
> **sozlanishi** kerak: qaysi baza, qaysi app'lar, qaysi til. `manage.py`
> buni o'zi qiladi. Shuning uchun botni ham `manage.py` orqali ishga
> tushiramiz."

### `settings.py` ga token

```python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ...fayl oxirida:
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
```

### `shop/management/commands/runbot.py`

```python
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


async def run():
    from handlers import register

    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    register(dp)
    try:
        me = await bot.get_me()
        logger.info("Bot ishga tushdi: @%s", me.username)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


class Command(BaseCommand):
    help = "Telegram botni ishga tushiradi"

    def handle(self, *args, **options):
        if not settings.BOT_TOKEN:
            raise CommandError("BOT_TOKEN .env faylida ko'rsatilmagan.")
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s | %(levelname)s | %(message)s")
        try:
            asyncio.run(run())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nBot to'xtatildi."))
```

`main.py` ni **o'chiring**. Endi:

```bash
python manage.py runbot          # 1-terminal
python manage.py runserver       # 2-terminal
```

---

## 6-qism. Yakuniy namoyish (5 daqiqa)

Ikkala terminalni ham ishga tushiring va shu ketma-ketlikni bajaring:

1. Botda `🍽 Menyu` → `🍔 Burgerlar` → `Klassik burger` → narx **32 000**
2. Admin panelda narxni **99 000** qiling, Save bosing
3. Botda `🔙 Orqaga` → yana `Klassik burger`

**Narx 99 000.** Bot qayta ishga tushirilmadi, kodga tegilmadi.

> "Mana shu — butun kursning eng muhim lahzasi. Endi do'kon egasi
> dasturchisiz ishlay oladi."

---

## Dars natijasi

| Amal | Natija |
|---|---|
| Admin panelda narx o'zgartirish | Bot darhol yangi narxni ko'rsatadi |
| Admin panelda `faol` ni olib tashlash | Mahsulot botda yo'qoladi |
| Yangi mahsulot qo'shish | Botda darhol paydo bo'ladi |
| `python manage.py runbot` | Bot ishga tushadi |

Tayyor kod: `darslar/7-dars/` (admin: `admin` / `admin12345`)

---

## Uy vazifasi

1. `services.py` ga **`qidiruv(matn)`** funksiyasini qo'shing —
   nom bo'yicha mahsulot qidirsin (`nom__icontains`)
2. Kategoriya tugmasida **mahsulotlar sonini** chiqaring: `🍔 Burgerlar (3)`
3. Mahsulot kartasiga **`⬅️ Oldingi`** / **`Keyingi ➡️`** tugmalarini qo'shing
4. Servisga `eng_arzon(n)` funksiyasini yozing — eng arzon N ta mahsulot

---

## Tez-tez chiqadigan xatolar

| Xato | Sabab | Yechim |
|---|---|---|
| `SynchronousOnlyOperation` | ORM to'g'ridan-to'g'ri chaqirildi | `@sync_to_async` bilan o'rang |
| Xuddi shu xato, lekin servisda emas | Lazy FK: `m.kategoriya.nom` | Servis `dict` qaytarsin |
| `ImproperlyConfigured: settings are not configured` | `python main.py` ishlatildi | `python manage.py runbot` |
| `ModuleNotFoundError: No module named 'shop'` | Loyiha ildizidan ishga tushirilmagan | `manage.py` yonidan ishlating |
| Bot eski narxni ko'rsatyapti | Kesh emas — servis chaqirilmagan | Handler `await services...` qilyaptimi |
| `Model class ... isn't in an application in INSTALLED_APPS` | Noto'g'ri `settings` yuklandi | `DJANGO_SETTINGS_MODULE` va `sys.path` ni tekshiring |
| N+1: bot sekin | Sikl ichida servis chaqirilyapti | `filter(pk__in=[...])` bilan bitta so'rov |
