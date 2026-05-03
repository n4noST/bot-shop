import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# États pour le panier
class Cart(StatesGroup):
    waiting = State()

products = {
    "1": {"name": "T-shirt Noir", "price": 29, "type": "physical"},
    "2": {"name": "Formation Marketing", "price": 19, "type": "digital"},
    "3": {"name": "Casquette", "price": 15, "type": "physical"},
    "4": {"name": "Ebook Recettes", "price": 12, "type": "digital"},
}

user_cart = {}

def main_menu():
    kb = [
        [InlineKeyboardButton(text="🛒 Catalogue", callback_data="catalog")],
        [InlineKeyboardButton(text="🛍 Mon Panier", callback_data="view_cart")],
        [InlineKeyboardButton(text="📦 Mes Commandes", callback_data="my_orders")],
        [InlineKeyboardButton(text="⭐ Laisser un Avis", callback_data="leave_review")],
        [InlineKeyboardButton(text="ℹ️ Aide", callback_data="help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Bienvenue dans ma Boutique !\nQue veux-tu faire ?", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "catalog")
async def catalog(callback: types.CallbackQuery):
    kb = []
    for pid, p in products.items():
        kb.append([InlineKeyboardButton(text=f"{p['name']} - {p['price']}€", callback_data=f"add_{pid}")])
    kb.append([InlineKeyboardButton(text="⬅️ Retour", callback_data="back_menu")])
    await callback.message.edit_text("🛍 **Catalogue :**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(pid)
    await callback.answer(f"✅ {products[pid]['name']} ajouté au panier !")

@dp.callback_query(lambda c: c.data == "view_cart")
async def view_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart = user_cart.get(user_id, [])
    if not cart:
        await callback.answer("Panier vide !")
        return
    text = "🛍 Ton panier :\n\n"
    total = 0
    for pid in cart:
        p = products[pid]
        text += f"- {p['name']} - {p['price']}€\n"
        total += p['price']
    text += f"\n**Total : {total}€**"
    kb = [[InlineKeyboardButton(text="💳 Payer", callback_data="pay_cart")],
          [InlineKeyboardButton(text="⬅️ Retour", callback_data="back_menu")]]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "pay_cart")
async def pay_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart = user_cart.get(user_id, [])
    if not cart:
        await callback.answer("Panier vide")
        return
    # Paiement Stars (pour simplifier, on prend le total)
    total_stars = sum(products[p]["price"] * 100 for p in cart)  # exemple
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Paiement Panier",
        description="Merci pour votre achat",
        payload="cart_payment",
        provider_token="", 
        currency="XTR",
        prices=[types.LabeledPrice(label="Total", amount=total_stars)]
    )

@dp.message(types.SuccessfulPayment)
async def successful_payment(message: types.Message):
    await message.answer("🎉 Paiement réussi ! Merci pour ton achat.\nTes produits arrivent bientôt.")

@dp.callback_query(lambda c: c.data == "back_menu")
async def back_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("👋 Bienvenue dans ma boutique !", reply_markup=main_menu())

# Autres boutons (à compléter)
@dp.callback_query(lambda c: c.data in ["my_orders", "leave_review", "help"])
async def other_features(callback: types.CallbackQuery):
    await callback.answer("Cette fonctionnalité arrive bientôt !")

async def main():
    print("✅ Bot PRO démarré avec paiements et options !")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
