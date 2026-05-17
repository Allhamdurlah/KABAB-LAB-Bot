import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MENU = {
    "Lula Kabab": {
        "narxlar": {"kichik": 18000, "orta": 25000, "katta": 35000},
        "rasm": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Lula-kebab.jpg/1200px-Lula-kebab.jpg",
        "tavsif": "Nozik maydalangan go'shtdan tayyorlangan, ko'mir ustida qovurilgan kabab",
    },
    "Toshkent Kabab": {
        "narxlar": {"kichik": 20000, "orta": 28000, "katta": 38000},
        "rasm": "https://chefspencil.com/wp-content/uploads/Uzbek-Shish-Kebab.jpg",
        "tavsif": "O'zbek uslubidagi an'anaviy kabab, sabzavotlar bilan",
    },
    "Adana Kabab": {
        "narxlar": {"kichik": 22000, "orta": 30000, "katta": 42000},
        "rasm": "https://www.mommyandkitchen.com/wp-content/uploads/2022/08/adana-kebab.jpg",
        "tavsif": "Achchiq ziravorlar bilan qovurilgan kabab",
    },
    "Shashlik": {
        "narxlar": {"kichik": 25000, "orta": 35000, "katta": 50000},
        "rasm": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1a/f6/e4/b0/caption.jpg",
        "tavsif": "Marinadlangan go'sht parchalaridan tayyorlangan klassik shashlik",
    },
    "Tandır Kabab": {
        "narxlar": {"kichik": 28000, "orta": 38000, "katta": 55000},
        "rasm": "https://travelinuzbekistan.com/wp-content/uploads/2020/09/tandir-kebab.jpg",
        "tavsif": "Tandır pechida pishirilgan mazali kabab",
    },
    "Baliq Kabab": {
        "narxlar": {"kichik": 30000, "orta": 42000, "katta": 60000},
        "rasm": "https://yummyfoodrecipes.in/wp-content/uploads/2021/fish-kabab.jpg",
        "tavsif": "Toza baliqdan tayyorlangan, limon va o'tlar bilan qovurilgan kabab",
    },
}

SIZE_DISPLAY = {"kichik": "Kichik", "orta": "O'rta", "katta": "Katta"}
SIZE_KEYS = list(SIZE_DISPLAY.keys())
KABAB_NAMES = list(MENU.keys())

ASK_NAME, ASK_KABAB, ASK_SIZE, ASK_ADDRESS, ASK_PHONE = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🔥 *KABABLEB*ga xush kelibsiz!\n\n"
        "Biz eng mazali va sifatli kabab tayyorlaymiz — "
        "har bir kabab sevuvchi uchun!\n\n"
        "📋 *Mavjud buyruqlar:*\n"
        "/menyu — Kabab menyusi va narxlar\n"
        "/buyurtma — Buyurtma berish\n"
        "/aloqa — Bog'lanish ma'lumotlari\n"
        "/ish\\_vaqti — Ish vaqtimiz\n\n"
        "Buyurtma qilishni xohlaysizmi? /buyurtma buyrug'ini bosing! 🍖",
        parse_mode="Markdown",
    )


async def menyu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = ["🍖 *KABABLEB MENYUSI*\n"]
    for name, info in MENU.items():
        narxlar = info["narxlar"]
        lines.append(f"🍢 *{name}*")
        lines.append(f"• Kichik — {narxlar['kichik']:,} so'm")
        lines.append(f"• O'rta — {narxlar['orta']:,} so'm")
        lines.append(f"• Katta — {narxlar['katta']:,} so'm")
        lines.append("")
    lines.append("Buyurtma berish uchun /buyurtma buyrug'ini bosing\\! 🛒")
    await update.message.reply_text("\n".join(lines), parse_mode="MarkdownV2")


async def buyurtma_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "🛒 *Buyurtma berish*\n\n"
        "Bekor qilish uchun /cancel bosing.\n\n"
        "Ismingizni kiriting (ism va familiya):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_NAME


async def ask_kabab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    keyboard = [[k] for k in KABAB_NAMES]
    await update.message.reply_text(
        f"Rahmat, *{context.user_data['name']}*! 👋\n\n"
        "Qaysi kabab turini tanlaysiz?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return ASK_KABAB


async def ask_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chosen = update.message.text.strip()
    if chosen not in MENU:
        keyboard = [[k] for k in KABAB_NAMES]
        await update.message.reply_text(
            "Iltimos, quyidagi ro'yxatdan tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return ASK_KABAB
    context.user_data["kabab"] = chosen
    keyboard = [[v] for v in SIZE_DISPLAY.values()]
    await update.message.reply_text(
        f"*{chosen}* — ajoyib tanlov! 🔥\n\nQaysi o'lchamni xohlaysiz?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return ASK_SIZE


async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    size_raw = update.message.text.strip()
    reverse_map = {v: k for k, v in SIZE_DISPLAY.items()}
    if size_raw not in reverse_map:
        keyboard = [[v] for v in SIZE_DISPLAY.values()]
        await update.message.reply_text(
            "Iltimos, o'lchamni ro'yxatdan tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return ASK_SIZE
    size_key = reverse_map[size_raw]
    context.user_data["size_display"] = size_raw
    context.user_data["size_key"] = size_key
    kabab = context.user_data["kabab"]
    price = MENU[kabab]["narxlar"][size_key]
    context.user_data["price"] = price
    await update.message.reply_text(
        f"✅ *{size_raw} {kabab}* — {price:,} so'm\n\n"
        "Yetkazib berish manzilingizni kiriting:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_ADDRESS


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["address"] = update.message.text.strip()
    await update.message.reply_text(
        "📞 Telefon raqamingizni kiriting\n(masalan: +998901234567):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_PHONE


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text.strip()
    d = context.user_data
    summary = (
        "🎉 *Buyurtmangiz qabul qilindi!*\n\n"
        f"👤 Ism: {d['name']}\n"
        f"🍖 Kabab: {d['kabab']}\n"
        f"📏 O'lcham: {d['size_display']}\n"
        f"💰 Narx: {d['price']:,} so'm\n"
        f"📍 Manzil: {d['address']}\n"
        f"📞 Telefon: {d['phone']}\n\n"
        "Tez orada operatorimiz siz bilan bog'lanadi.\n"
        "Kababingiz *30-45 daqiqa* ichida yetkaziladi! 🚴\n\n"
        "Yana buyurtma berish uchun /buyurtma bosing."
    )
    await update.message.reply_text(summary, parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ Buyurtma bekor qilindi.\n\n"
        "Istalgan vaqt /buyurtma orqali qayta buyurtma bera olasiz.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def aloqa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📞 *KABABLEB — Aloqa ma'lumotlari*\n\n"
        "📱 Telefon: +998 90 123 45 67\n"
        "📱 Telegram: @kabableb\\_bot\n"
        "📍 Manzil: Toshkent sh., Chilonzor tumani,\n"
        "   Bunyodkor ko'chasi, 12\\-uy\n\n"
        "📧 Email: info@kabableb\\.uz\n\n"
        "Buyurtma berish: /buyurtma",
        parse_mode="MarkdownV2",
    )


async def ish_vaqti(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🕐 *KABABLEB — Ish vaqti*\n\n"
        "🗓 *Dushanba — Shanba:*\n"
        "   🌅 10:00 — 22:00\n\n"
        "🗓 *Yakshanba:*\n"
        "   🌅 11:00 — 21:00\n\n"
        "🚴 *Yetkazib berish:*\n"
        "   Buyurtmalarni ish vaqtimiz davomida qabul qilamiz.\n"
        "   Yetkazib berish vaqti: 30-45 daqiqa\n\n"
        "Buyurtma berish uchun: /buyurtma",
        parse_mode="Markdown",
    )


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN muhit o'zgaruvchisi topilmadi!")

    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("buyurtma", buyurtma_start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_kabab)],
            ASK_KABAB: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_size)],
            ASK_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menyu", menyu))
    app.add_handler(CommandHandler("aloqa", aloqa))
    app.add_handler(CommandHandler("ish_vaqti", ish_vaqti))
    app.add_handler(conv_handler)

    logger.info("KABABLEB bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
