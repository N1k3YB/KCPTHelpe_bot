import logging
import asyncio
from aiogram import Router, F, Bot, Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton
from aiogram.filters import Command
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

logging.basicConfig(level=logging.INFO)
TARGET_BOT_USERNAME = "kcptraspisaniebot"
router = Router()

class States(StatesGroup):
    menu = State()
    chat_mode = State()

@router.message(Command("start"))
async def start(message, state: FSMContext):
    await show_menu(message, state)

# Отображение меню
async def show_menu(message, state: FSMContext):
    menu_keyboard = ReplyKeyboardBuilder()
    menu_keyboard.add(KeyboardButton(text="Сайт"))
    menu_keyboard.add(KeyboardButton(text="ИИ"))
    menu_keyboard.add(KeyboardButton(text="Расписание"))

    await message.answer("Выберите опцию:", reply_markup=menu_keyboard.as_markup(resize_keyboard=True))
    await state.set_state(States.menu)

# Обработчик нажатия кнопки "ИИ"
@router.message(F.text.contains("ИИ"), States.menu)
async def chat_mode(message, state: FSMContext):
    chat = GigaChat(credentials='ZmNlN2MxNjAtNDE3NC00NjlmLTlkNGEtZTdmODQ1ZGYxNWU4OjU0MTIwYTZiLTY2M2MtNGFhZS1iMjk4LWZhMzQwMjBkYTlhNA==', verify_ssl_certs=False, model="GigaChat:latest")
    messages = [SystemMessage(content="Ты - виртуальный помощник по учебе для студентов колледжа. Ты можешь помочь с различными задачами и вопросами, связанными с вашим обучением. Вот некоторые из моих возможностей: 📚 Помощь с заданиями и проектами по предметам, таким как программирование, дизайн, педагогика и т.д. Ты можешь объяснять концепции, давать примеры кода, проверять правильность решений. 🧠 Подготовка к экзаменам и тестам. Ты предоставляешь материалы для изучения, тренировочные задания, стратегии подготовки. 📝 Редактирование и проверка письменных работ - эссе, отчётов, презентаций. Ты поможешь с грамматикой, стилем, структурой и цитированием. 📖 Рекомендации по дополнительным учебным ресурсам - книгам, видео, онлайн-курсам по изучаемым предметам. 💬 Консультации по управлению временем, методам эффективного обучения, преодолению стресса и т.п. Ты всегда готов ответить на ваши вопросы, помочь разобраться в сложных темах и задачах. Просто обратитесь ко мне в любое удобное время! Так же не забудь, что ты написан и создан студентом 2 курса направления Информационные Системы и Программирование, Леванюком Никитой")]
    await state.update_data(messages=messages)
    back_keyboard = ReplyKeyboardBuilder()
    back_keyboard.add(KeyboardButton(text="Назад"))
    await message.answer("Что хотите узнать?", reply_markup=back_keyboard.as_markup(resize_keyboard=True))
    await state.set_state(States.chat_mode)

# Обработчик нажатия кнопки "Сайт"
@router.message(F.text.contains("Сайт"), States.menu)
async def open_website(message: types.Message, state: FSMContext):
    website_url = "https://kcpt72.ru/"  # Замените на нужный URL сайта
    await message.answer(f"Перейдите по ссылке, либо нажмите на кнопку ниже: {website_url}", reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Сайт колледжа", url=website_url)]]
    ))

@router.message(F.text.contains("Расписание"), States.menu)
async def send_to_target_bot(message: types.Message, state: FSMContext, bot: Bot):
    keyboard = ReplyKeyboardBuilder().as_markup(resize_keyboard=True)
    await bot.send_message(chat_id=message.chat.id, text=f"Для просмотра расписания перейдите в бота:", reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Расписание КЦПТ", url=f"https://t.me/{TARGET_BOT_USERNAME}")]]
    ))

# Обработчик сообщений в режиме чата
@router.message(F.text, States.chat_mode)
async def chat_handler(message, state: FSMContext):
    if message.text == "Назад":
        await back_to_menu(message, state)
        return
    chat = GigaChat(credentials='ZmNlN2MxNjAtNDE3NC00NjlmLTlkNGEtZTdmODQ1ZGYxNWU4OjU0MTIwYTZiLTY2M2MtNGFhZS1iMjk4LWZhMzQwMjBkYTlhNA==', verify_ssl_certs=False)
    data = await state.get_data()
    messages = data.get('messages', [])
    messages.append(HumanMessage(content=message.text))
    res = chat.invoke(messages)
    messages.append(res)
    await state.update_data(messages=messages)
    await message.answer(res.content)

# Обработчик нажатия кнопки "Назад"
@router.message(Command("Назад"), States.chat_mode)
async def back_to_menu(message, state: FSMContext):
    await state.set_state(States.menu)
    await show_menu(message, state)


async def main():
    API_TOKEN = '6502399298:AAFOP64SuLeETl8QTfQfhVuzVEptnu2f-BA'
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())