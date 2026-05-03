import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Menu principal en boutons dans le message
def main_menu():
    kb = [
        [InlineKeyboardButton(text="🛒 Voir les produits", callback_data="show_products")],
        [InlineKeyboardButton(text="🛍 Mes commandes", callback_data="my_orders")],
        [InlineKeyboardButton(text="⭐ Avis", callback_data="reviews")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Bienvenue dans ma boutique !\nQue veux-tu faire ?", reply_markup=main_menu())

# Affichage des produits
@dp.callback_query(lambda c: c.data == "show_products")
async def show_products(callback: types.CallbackQuery):
    kb = [
        [InlineKeyboardButton(text="👕 T-shirt Noir - 29€", callback_data="buy_1")],
        [InlineKeyboardButton(text="📚 Formation Marketing - 19€", callback_data="buy_2")],
        [InlineKeyboardButton(text="⬅️ Retour", callback_data="back_to_menu")]
    ]
    await callback.message.edit_text(
        "🛍 **Produits disponibles :**\n\n"
        "1. T-shirt Noir - 29€ (Physique)\n"
        "2. Formation Marketing - 19€ (Digital)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("👋 Bienvenue dans ma boutique !\nQue veux-tu faire ?", reply_markup=main_menu())

# Achat (à améliorer plus tard)
@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    product = callback.data
    if product == "buy_1":
        await callback.answer("✅ T-shirt sélectionné ! (Paiement à venir)")
    else:
        await callback.answer("✅ Formation sélectionnée ! (Paiement Stars à venir)")

@dp.callback_query(lambda c: c.data == "my_orders")
async def my_orders(callback: types.CallbackQuery):
    await callback.answer("Aucune commande pour l'instant.")

@dp.callback_query(lambda c: c.data == "reviews")
async def reviews(callback: types.CallbackQuery):
    await callback.answer("Système d'avis bientôt disponible.")

async def main():
    print("✅ Bot amélioré démarré !")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
