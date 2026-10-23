import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import database as db

# ----------------- SOZLAMALAR -----------------
BOT_TOKEN = "8963367815:AAE9eQjWAcFM6NnD0ZyyeOeKt29EmmEpDkA"  # Botingiz tokeni
ADMIN_ID = 6669594073  # Telegram ID raqamingiz
CARD_NUMBER = "9860350149599481"  # To'lov qabul qilinadigan karta raqami

# Majburiy obuna kanallari (Bot kanalda admin bo'lishi shart!)
CHANNELS = [
    {
        "name": "Kurganov life | Rasmiy Kanal",
        "id": "@kurganov_life05",  # Username orqali tekshirish eng aniq ishlaydi
        "url": "https://t.me/kurganov_life05"
    }
]

# Tariflar ro'yxati
TARIFFS = {
    "tariff_1": {"name": "Ming som bonus", "price": 1000, "days": 3},
    "tariff_2": {"name": "Super Aksiya 60", "price": 1999, "days": 60},
    "tariff_3": {"name": "Bomba Aksiya 365 kun", "price": 5999, "days": 365},
    "tariff_4": {"name": "15 kun", "price": 15000, "days": 15},
    "tariff_5": {"name": "1 oy", "price": 30000, "days": 30},
    "tariff_6": {"name": "3 oy", "price": 90000, "days": 90},
}
# ---------------------------------------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
orders = {}


class MovieStates(StatesGroup):
    waiting_for_code = State()


class AdminStates(StatesGroup):
    waiting_for_video = State()
    waiting_for_info = State()


async def check_user_subscription(user_id: int) -> bool:
    channel_username = "@kurganov_life05"
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        print(f"\n====================================")
        print(f"TEKSHIRUV: Foydalanuvchi ID: {user_id}")
        print(f"Kanal: {channel_username}")
        print(f"Foydalanuvchi statusi: '{member.status}'")
        print(f"====================================\n")
        
        # Faqat kanalga a'zo, admin yoki kanal egasi bo'lsa True qaytadi
        if member.status in ["creator", "administrator", "member"]:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"\n[XATOLIK YUZ BERDI]: {e}\n")
        # Xatolik bo'lsa (masalan, bot kanalda admin bo'lmasa), obuna bo'lmagan deb hisoblaymiz:
        return False


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    db.add_user(user_id)

    # Obunani tekshirish
    is_sub = await check_user_subscription(user_id)
    
    if not is_sub:
        await message.answer(
            "⚠️ <b>Botdan toʻliq foydalanish uchun kanalimizga aʼzo boʻling!</b>\n\n"
            "Kanalga aʼzo boʻlgach, <b>«✅ Obunani tekshirish»</b> tugmasini bosing:",
            parse_mode="HTML",
            reply_markup=subscription_keyboard()
        )
        return

    # A'zo bo'lgandagina asosiy menyu chiqadi
    await message.answer(
        "🎬 <b>Kurganov life • KINO</b> botiga xush kelibsiz!\n\nKerakli boʻlimni tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


def subscription_keyboard():
    keyboard = []
    for ch in CHANNELS:
        keyboard.append(
            [InlineKeyboardButton(text=f"➕ {ch['name']}", url=ch["url"])]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ Obunani tekshirish",
                callback_data="verify_subscription",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 Film qidirish", callback_data="search"
                ),
                InlineKeyboardButton(text="🔥 Top filmlar", callback_data="top"),
            ],
            [
                InlineKeyboardButton(
                    text="📁 Saqlanganlar", callback_data="saved"
                ),
                InlineKeyboardButton(
                    text="💎 VIP tariflar", callback_data="vip_tariffs"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎬 Film buyurtma", callback_data="order"
                ),
                InlineKeyboardButton(
                    text="👤 Kabinet", callback_data="cabinet"
                ),
            ],
            [
                InlineKeyboardButton(text="ℹ️ Yordam", callback_data="help"),
                InlineKeyboardButton(
                    text="📢 Rasmiy kanal", url=CHANNELS[0]["url"]
                ),
            ],
        ]
    )


def vip_tariffs_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💎 Ming som bonus — 1 000 soʻm",
                    callback_data="buy_tariff_1",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 Super Aksiya 60 | 1.999 soʻm — 1 999 soʻm",
                    callback_data="buy_tariff_2",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 Bomba Aksiya 365 kun | 5.999 — 5 999 soʻm",
                    callback_data="buy_tariff_3",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 15 kun — 15 000 soʻm", callback_data="buy_tariff_4"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 1 oy — 30 000 soʻm", callback_data="buy_tariff_5"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 3 oy — 90 000 soʻm", callback_data="buy_tariff_6"
                )
            ],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_main")],
        ]
    )


# O'z ID raqamingizni aniqlash
@dp.message(Command("id"))
async def cmd_get_id(message: types.Message):
    await message.answer(
        f"Sizning Telegram ID raqamingiz: <code>{message.from_user.id}</code>",
        parse_mode="HTML",
    )


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    db.add_user(user_id)

    if not await check_user_subscription(user_id):
        await message.answer(
            "⚠️ <b>Botdan toʻliq foydalanish uchun kanalimizga aʼzo boʻling:</b>",
            parse_mode="HTML",
            reply_markup=subscription_keyboard(),
        )
        return

    await message.answer(
        "🎬 <b>MARKOFILIX • KINO</b> botiga xush kelibsiz!\n\nKerakli boʻlimni tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "verify_subscription")
async def verify_sub(callback: types.CallbackQuery):
    if await check_user_subscription(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer(
            "🎉 <b>Obuna tasdiqlandi!</b> Kerakli boʻlimni tanlang:",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
    else:
        await callback.answer(
            "❌ Siz hali kanalga aʼzo boʻlmadingiz!", show_alert=True
        )


@dp.callback_query(F.data == "cabinet")
async def show_cabinet(callback: types.CallbackQuery):
    expiry = db.get_vip_expiry(callback.from_user.id)
    status = (
        f"✅ Faol (Muddat: {expiry} gacha)"
        if expiry
        else "❌ Faol emas (Oddiy aʼzo)"
    )
    await callback.message.edit_text(
        f"👤 <b>Shaxsiy Kabinet</b>\n\n🆔 ID: <code>{callback.from_user.id}</code>\n💎 VIP holati: {status}",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "search")
async def start_search(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🔢 Film kodini yuboring (Masalan: <code>105</code>):", parse_mode="HTML")
    await state.set_state(MovieStates.waiting_for_code)
    await callback.answer()


@dp.message(MovieStates.waiting_for_code)
async def process_movie_code(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqamli kod kiriting!")
        return

    code = int(message.text)
    movie = db.get_movie_by_code(code)
    if not movie:
        await message.answer("❌ Bunday kodli film topilmadi.")
        await state.clear()
        return

    title, file_id = movie
    await message.answer_video(
        video=file_id,
        caption=f"🎬 <b>{title}</b>\n🔢 Kod: <code>{code}</code>",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )
    await state.clear()


@dp.message(F.text.isdigit())
async def direct_movie_search(message: types.Message):
    if not await check_user_subscription(message.from_user.id):
        await message.answer(
            "⚠️ Film koʻrish uchun avval kanalga aʼzo boʻling:",
            reply_markup=subscription_keyboard(),
        )
        return

    code = int(message.text)
    movie = db.get_movie_by_code(code)
    if not movie:
        await message.answer("❌ Film topilmadi.")
        return

    title, file_id = movie
    await message.answer_video(
        video=file_id,
        caption=f"🎬 <b>{title}</b>\n🔢 Kod: <code>{code}</code>",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.message(Command("addmovie"))
async def admin_add_movie(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu buyruq faqat bot admini uchun!")
        return
    await message.answer("Film videosini yuboring:")
    await state.set_state(AdminStates.waiting_for_video)


@dp.message(AdminStates.waiting_for_video, F.video)
async def process_admin_video(message: types.Message, state: FSMContext):
    await state.update_data(file_id=message.video.file_id)
    await message.answer(
        "Kino kodi va nomini yuboring:\n<code>kod|nomi</code> (Masalan: <code>105|Qasoskorlar</code>)",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_for_info)


@dp.message(AdminStates.waiting_for_info)
async def process_admin_info(message: types.Message, state: FSMContext):
    try:
        code_str, title = message.text.split("|", 1)
        data = await state.get_data()
        db.add_movie(
            code=int(code_str.strip()),
            title=title.strip(),
            file_id=data["file_id"],
        )
        await message.answer("✅ Film bazaga saqlandi!")
    except Exception:
        await message.answer("Xatolik. Qaytadan urinib koʻring (Format: <code>kod|nomi</code>).", parse_mode="HTML")
    finally:
        await state.clear()


@dp.callback_query(F.data == "vip_tariffs")
async def show_vip(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💎 <b>VIP tariflar</b>\n\nTarifni tanlang:",
        parse_mode="HTML",
        reply_markup=vip_tariffs_keyboard(),
    )


@dp.callback_query(F.data.startswith("buy_"))
async def process_order(callback: types.CallbackQuery):
    tariff = TARIFFS.get(callback.data.replace("buy_", ""))
    extra = random.randint(10, 300)
    total = tariff["price"] + extra
    orders[callback.from_user.id] = {
        "tariff_name": tariff["name"],
        "days": tariff["days"],
        "amount": total,
    }

    text = (
        "⏳ <b>Buyurtma 5 daqiqa amal qiladi. Muddat oʻtsa yangi buyurtma oching.</b>\n\n"
        "⚠️ \"Toʻlov qildim\" tugmasi faqat holatni tekshiradi, oʻzi toʻlovni tasdiqlamaydi.\n\n"
        f"⚠️ <b>Bir xil toʻlovlarni farqlash uchun +{extra} soʻm qoʻshildi.</b>"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💳 {CARD_NUMBER}",
                    callback_data=f"card_{CARD_NUMBER}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"💰 {total:,} soʻm".replace(",", " "),
                    callback_data="none",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Toʻlov qildim", callback_data="check_payment"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish", callback_data="cancel_payment"
                )
            ],
        ]
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data.startswith("card_"))
async def copy_card(callback: types.CallbackQuery):
    await callback.answer(
        f"Karta raqami: {callback.data.split('_')[1]}\n(Nusxalab oling)", show_alert=True
    )


# Foydalanuvchi "To'lov qildim" tugmasini bosganda
@dp.callback_query(F.data == "check_payment")
async def check_pay(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    order = orders.get(user_id)
    if not order:
        await callback.answer("Buyurtma muddati oʻtgan yoki topilmadi!", show_alert=True)
        return

    # Foydalanuvchiga bildirishnoma
    await callback.answer(
        "⏳ Soʻrovingiz adminga yuborildi. Toʻlov tekshirilgach VIP obunangiz faollashadi!",
        show_alert=True,
    )

    # Adminga tasdiqlash uchun xabar yuborish
    admin_confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data=f"adm_confirm_{user_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish", callback_data=f"adm_reject_{user_id}"
                ),
            ]
        ]
    )

    admin_text = (
        "🔔 <b>Yangi toʻlov soʻrovi!</b>\n\n"
        f"👤 Foydalanuvchi: <a href='tg://user?id={user_id}'>{callback.from_user.full_name}</a>\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📦 Tarif: <b>{order['tariff_name']}</b>\n"
        f"💰 Kutilayotgan summa: <b>{order['amount']:,} soʻm</b>\n"
        f"💎 Muddat: <b>{order['days']} kun</b>"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=admin_confirm_kb,
        )
    except Exception as e:
        logging.error(f"Adminga yuborishda xatolik: {e}")


# Admin "Tasdiqlash" tugmasini bosganda
@dp.callback_query(F.data.startswith("adm_confirm_"))
async def admin_confirm_payment(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Bu amal faqat adminga tegishli!", show_alert=True)
        return

    target_user_id = int(callback.data.split("_")[2])
    order = orders.pop(target_user_id, None)
    days = order["days"] if order else 30

    expiry = db.set_vip(target_user_id, days)

    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ <b>Toʻlov tasdiqlandi! (Muddat: {expiry} gacha)</b>",
        parse_mode="HTML",
    )

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"🎉 <b>Toʻlovingiz tasdiqlandi!</b>\n💎 VIP obunangiz <b>{expiry}</b> gacha faollashtirildi.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
    except Exception:
        pass
    await callback.answer("Tasdiqlandi!")


# Admin "Rad etish" tugmasini bosganda
@dp.callback_query(F.data.startswith("adm_reject_"))
async def admin_reject_payment(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Bu amal faqat adminga tegishli!", show_alert=True)
        return

    target_user_id = int(callback.data.split("_")[2])
    orders.pop(target_user_id, None)

    await callback.message.edit_text(
        f"{callback.message.text}\n\n❌ <b>Toʻlov rad etildi!</b>",
        parse_mode="HTML",
    )

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text="❌ Siz yuborgan toʻlov hisobga tushmadi yoki tasdiqlanmadi. Qayta urinib koʻring yoki adminga murojaat qiling.",
            reply_markup=main_menu(),
        )
    except Exception:
        pass
    await callback.answer("Rad etildi!")


@dp.callback_query(F.data == "cancel_payment")
async def cancel_pay(callback: types.CallbackQuery):
    orders.pop(callback.from_user.id, None)
    await callback.message.delete()
    await callback.message.answer(
        "Buyurtma bekor qilindi.", reply_markup=main_menu()
    )


@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Asosiy menyu:", reply_markup=main_menu()
    )


async def main():
   from aiohttp import web

async def handle_ping(request):
    return web.Response(text="Bot 24/7 ishlamoqda!")

async def main():
    # Render port talab qilgani uchun fonga kichik veb-server yoqamiz
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

    # Botni ishga tushirish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())