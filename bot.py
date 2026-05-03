import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

def menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(KeyboardButton("🛒 Voir produits"))
    kb.add(KeyboardButton("🛍 Mes commandes"), KeyboardButton("⭐ Avis"))
    return kb

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Bienvenue dans ma boutique !", reply_markup=menu())

@dp.message(lambda m: m.text == "🛒 Voir produits")
async def products(message: types.Message):
    await message.answer("""🛍 Produits disponibles :

1. T-shirt Noir - 29€ (Physique)
2. Formation Marketing - 19€ (Digital)

Tape /acheter1 ou /acheter2""")

@dp.message(Command("acheter1"))
async def acheter1(message: types.Message):
    await message.answer("✅ Produit physique sélectionné.\nPaiement en cours de configuration...")

@dp.message(Command("acheter2"))
async def acheter2(message: types.Message):
    await message.answer("✅ Produit digital sélectionné.\nOn va utiliser Telegram Stars.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
