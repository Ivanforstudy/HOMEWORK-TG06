import asyncio
import random
import sqlite3
import logging
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Кнопки меню
button_registr = KeyboardButton(text="Регистрация в телеграм боте")
button_fact = KeyboardButton(text="Интересный факт о животных")
button_tips = KeyboardButton(text="Советы по уходу")
button_pets = KeyboardButton(text="Мои питомцы")

keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_fact],
    [button_tips, button_pets]
], resize_keyboard=True)

# База данных
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    pet1 TEXT,
    pet2 TEXT,
    pet3 TEXT,
    trait1 TEXT,
    trait2 TEXT,
    trait3 TEXT
)
''')
conn.commit()

# Машина состояний
class PetForm(StatesGroup):
    pet1 = State()
    trait1 = State()
    pet2 = State()
    trait2 = State()
    pet3 = State()
    trait3 = State()

# Старт
@dp.message(Command("start"))
async def send_start(message: Message):
    await message.answer("Привет! Я бот-любитель животных. Выберите одну из опций:", reply_markup=keyboards)

# Регистрация
@dp.message(F.text == "Регистрация в телеграм боте")
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.answer("Вы уже зарегистрированы!")
    else:
        cursor.execute('INSERT INTO users (telegram_id, name) VALUES (?, ?)', (telegram_id, name))
        conn.commit()
        await message.answer("Вы успешно зарегистрированы!")

# Интересный факт
@dp.message(F.text == "Интересный факт о животных")
async def animal_fact(message: Message):
    facts = [
        "Осьминоги имеют три сердца и синюю кровь.",
        "Коровы могут дружить и даже расстраиваются, если их разлучить.",
        "Собаки чувствуют запах времени — они могут определять, сколько времени прошло."
    ]
    await message.answer(random.choice(facts))

# Советы по уходу
@dp.message(F.text == "Советы по уходу")
async def care_tips(message: Message):
    tips = [
        "Регулярно чистите миски питомцев и меняйте воду.",
        "Выгуливайте собак не менее двух раз в день.",
        "Убедитесь, что у вашего питомца есть пространство для отдыха и игр."
    ]
    await message.answer(random.choice(tips))

# Ввод информации о питомцах
@dp.message(F.text == "Мои питомцы")
async def start_pet_input(message: Message, state: FSMContext):
    await state.set_state(PetForm.pet1)
    await message.reply("Введите имя первого питомца:")

@dp.message(PetForm.pet1)
async def enter_trait1(message: Message, state: FSMContext):
    await state.update_data(pet1=message.text)
    await state.set_state(PetForm.trait1)
    await message.reply("Введите интересную особенность этого питомца:")

@dp.message(PetForm.trait1)
async def enter_pet2(message: Message, state: FSMContext):
    await state.update_data(trait1=message.text)
    await state.set_state(PetForm.pet2)
    await message.reply("Введите имя второго питомца:")

@dp.message(PetForm.pet2)
async def enter_trait2(message: Message, state: FSMContext):
    await state.update_data(pet2=message.text)
    await state.set_state(PetForm.trait2)
    await message.reply("Введите интересную особенность этого питомца:")

@dp.message(PetForm.trait2)
async def enter_pet3(message: Message, state: FSMContext):
    await state.update_data(trait2=message.text)
    await state.set_state(PetForm.pet3)
    await message.reply("Введите имя третьего питомца:")

@dp.message(PetForm.pet3)
async def enter_trait3(message: Message, state: FSMContext):
    await state.update_data(pet3=message.text)
    await state.set_state(PetForm.trait3)
    await message.reply("Введите интересную особенность этого питомца:")

@dp.message(PetForm.trait3)
async def finish_input(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id
    cursor.execute('''UPDATE users SET 
                      pet1 = ?, trait1 = ?, 
                      pet2 = ?, trait2 = ?, 
                      pet3 = ?, trait3 = ? 
                      WHERE telegram_id = ?''',
                   (data['pet1'], data['trait1'], data['pet2'], data['trait2'], data['pet3'], message.text, telegram_id))
    conn.commit()
    await state.clear()
    await message.answer("Информация о питомцах сохранена!")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
