import datetime
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from yoomoney import Client, Quickpay
import requests
from bs4 import BeautifulSoup

# Создание экземпляра бота и диспетчера
bot = Bot(token='botToken')
dp = Dispatcher(bot)

# Конфигурация доступа к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("bot1.json", scope)
client = gspread.authorize(creds)
sheet = client.open("гугл_табличка").sheet1

# Конфигурация YooMoney
yoomoney_token = "yooMoneyToken"
client_yoomoney = Client(yoomoney_token)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Ленина 1", url="https://yandex.ru/maps/?text=Ленина%201"))
    keyboard.add(InlineKeyboardButton("Оплатить 2 рубля", callback_data="pay_2_rub"))
    keyboard.add(InlineKeyboardButton("Картинка", callback_data="send_image"))
    keyboard.add(InlineKeyboardButton("Получить значение А2", callback_data="get_value_a2"))
    await message.reply("Выберите действие:", reply_markup=keyboard)

# Обработчик нажатия на кнопки
# Обработчик кнопка 3: текст + картинка “img1.jpg”
@dp.callback_query_handler(lambda c: c.data == 'send_image')
async def process_callback_send_image(callback_query: types.CallbackQuery):
    with open('img1.jpg', 'rb') as photo:
        await bot.send_photo(callback_query.from_user.id, photo)
    await bot.answer_callback_query(callback_query.id)

# Обработчик кнопка 4: получить значение А2 гугл таблички “гугл_табличка”
@dp.callback_query_handler(lambda c: c.data == 'get_value_a2')
async def process_callback_get_value_a2(callback_query: types.CallbackQuery):
    value_a2 = sheet.cell(2, 1).value
    await bot.send_message(callback_query.from_user.id, f"Значение ячейки А2: {value_a2}")
    await bot.answer_callback_query(callback_query.id)

# Обработчик кнопка 2: текст + ссылка на оплату 2 р
@dp.callback_query_handler(lambda c: c.data == 'pay_2_rub')
async def process_callback_pay_2_rub(callback_query: types.CallbackQuery):
    quickpay = Quickpay(
        receiver="youMoneyAccount",
        quickpay_form="shop",
        targets="Оплата 2 рубля",
        paymentType="SB",
        sum=2,
    )
    await bot.send_message(callback_query.from_user.id, f"Оплатите 2 рубля по ссылке: {quickpay.redirected_url}")
    await bot.answer_callback_query(callback_query.id)

# Обработчик ввода даты
@dp.message_handler()
async def handle_date_input(message: types.Message):
    input_date = message.text
    # Проверяю формат даты на соответствие дд.мм.гг
    try:
        date_format = "%d.%m.%y"
        datetime.datetime.strptime(input_date, date_format)
    except ValueError:
        await message.reply("Дата введена неверно")
        return
    
    # Обращаемся к гугл табличке
    cell_list = sheet.col_values(2)
    next_row = len(cell_list) + 1
    sheet.update_cell(next_row, 2, input_date)
    await message.reply("Дата введена верно")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
