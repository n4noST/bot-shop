import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Products database
products = {
    "1": {"name": "Black T-Shirt", "price": 29, "type": "physical"},
    "2": {"name": "Marketing Course", "price": 19, "type": "digital"},
    "3": {"name": "Cap", "price": 15, "type": "physical"},
    "4": {"name": "Recipe Ebook", "price": 12, "type": "digital"},
    "5": {"name": "Hoodie", "price": 45, "type": "physical"},
}

user_cart = {}
user_orders = {}
user_reviews = {}

class CartStates(StatesGroup):
    waiting = State()

def main_menu():
    kb = [
        [InlineKeyboardButton(text="Catalog", callback_data="catalog")],
        [InlineKeyboardButton(text="My Cart", callback_data="view_cart")],
        [InlineKeyboardButton(text="My Orders", callback_data="my_orders")],
        [InlineKeyboardButton(text="Leave Review", callback_data="leave_review")],
        [InlineKeyboardButton(text="Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Welcome to my Shop!\nWhat do you want to do?", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    kb = []
    for pid, p in products.items():
        kb.append([InlineKeyboardButton(text=f"{p['name']} - {p['price']} EUR", callback_data=f"add_{pid}")])
    kb.append([InlineKeyboardButton(text="Back", callback_data="back_menu")])
    
    text = "Available Products:\n\n"
    for pid, p in products.items():
        text += f"{pid}. {p['name']} - {p['price']} EUR ({p['type']})\n"
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    pid = callback.data.split("_")[1]
    user_id = callback.from_user.id
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(pid)
    await callback.answer(f"{products[pid]['name']} added to cart!")

@dp.callback_query(lambda c: c.data == "view_cart")
async def view_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart = user_cart.get(user_id, [])
    if not cart:
        await callback.answer("Your cart is empty!")
        return
    
    text = "Your Cart:\n\n"
    total = 0
    for pid in cart:
        p = products[pid]
        text += f"- {p['name']} - {p['price']} EUR\n"
        total += p['price']
    text += f"\nTotal: {total} EUR"
    
    kb = [
        [InlineKeyboardButton(text="Pay Now", callback_data="pay_cart")],
        [InlineKeyboardButton(text="Back", callback_data="back_menu")]
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(lambda c: c.data == "pay_cart")
async def pay_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart = user_cart.get(user_id, [])
    if not cart:
        await callback.answer("Cart is empty")
        return
    
    total_stars = int(sum(products[p]["price"] for p in cart) * 100)
    await bot.send_invoice(
        chat_id=user_id,
        title="Shop Payment",
        description="Thank you for your purchase",
        payload="cart_payment",
        provider_token="",  # Telegram Stars
        currency="XTR",
        prices=[types.LabeledPrice(label="Total", amount=total_stars)]
    )

@dp.message(types.SuccessfulPayment)
async def successful_payment(message: types.Message):
    user_id = message.from_user.id
    # Save order
    if user_id not in user_orders:
        user_orders[user_id] = []
    user_orders[user_id].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": user_cart.get(user_id, []),
        "status": "Paid"
    })
    user_cart[user_id] = []
    await message.answer("Payment successful! Thank you.\nYour order has been saved.")

@dp.callback_query(lambda c: c.data == "my_orders")
async def my_orders(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    orders = user_orders.get(user_id, [])
    if not orders:
        await callback.answer("You have no orders yet.")
        return
    text = "Your Orders:\n\n"
    for order in orders:
        text += f"Date: {order['date']}\nStatus: {order['status']}\n\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Back", callback_data="back_menu")]]))

@dp.callback_query(lambda c: c.data == "leave_review")
async def leave_review(callback: types.CallbackQuery):
    await callback.answer("Review system coming soon. Thank you for your feedback!")

@dp.callback_query(lambda c: c.data == "help")
async def help_command(callback: types.CallbackQuery):
    text = "Shop Help:\n\n- Browse catalog and add to cart\n- Pay with Telegram Stars\n- Track your orders\n- Leave reviews"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Back", callback_data="back_menu")]]))

@dp.callback_query(lambda c: c.data == "back_menu")
async def back_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("Welcome to my Shop!\nWhat do you want to do?", reply_markup=main_menu())

async def main():
    print("Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
