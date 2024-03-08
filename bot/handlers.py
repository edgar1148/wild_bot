import os

from typing import Union

from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from bot.utils import get_product_info
from bot.keyboards import keyboard_start, keyboard_handle_product_sku, keyboard_stop_not
from bot.database import add_query_to_history, get_last_5_queries

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
router = Router()


class States(StatesGroup):
    waiting_for_product_sku = State()
    waiting_for_product_info = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Функция для старта"""
    text = (
        "Чтобы воспользоваться "
        "основными функциями бота, "
        "воспользуйтесь следующими кнопками, либо меню:\n"
    )
    await message.answer(text, reply_markup=keyboard_start())


async def get_history_handler(message_or_callback: Union[Message, CallbackQuery]):
    """Функция для получения истории запросов"""

    rows = await get_last_5_queries()

    if rows:
        history_message = "Последние 5 запросов из БД:\n\n"
        for row in rows:
            user_id, query_time, product_sku = row
            history_message += (
                f"ID пользователя: {user_id}\n"
                f"Время запроса: {query_time}\n"
                f"Артикул товара: {product_sku}\n\n"
            )
    else:
        history_message = "История запросов пуста."

    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(history_message)
    elif isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.answer(history_message)


@router.callback_query(F.data == "get_history")
async def callback_get_history(callback: CallbackQuery):
    """Кнопка для получения истории запросов"""
    await get_history_handler(callback)


@router.message(Command("get_history"))
async def command_get_history(message: Message):
    """Команда для получения истории запросов"""
    await get_history_handler(message)


async def product_info_handler(message_or_callback: Union[Message, CallbackQuery]):
    """Функция для ввода артикула"""
    text = (
        "Введите артикул товара на Wildberries: \n\n"
        "Например: 211695539"
    )
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text)
    elif isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.answer(text)


@router.callback_query(F.data == "product_info")
async def callback_product_info(callback: CallbackQuery):
    """Кнопка для ввода артикула"""
    await product_info_handler(callback)


@router.message(Command("product_info"))
async def command_product_info(message: Message):
    """Команда для ввода артикула"""
    await product_info_handler(message)


@router.message(StateFilter(States.waiting_for_product_sku))
@router.message(F.text)
async def handle_product_sku(message: Message, state: FSMContext):
    """Функция для обработки артикула"""
    product_sku = message.text
    product_info = await get_product_info(product_sku)

    if product_info:
        info_message = "Информация о товаре:\n\n"
        for key, value in product_info.items():
            info_message += f"{key}: {value}\n"
        await message.answer(info_message, reply_markup=keyboard_handle_product_sku())
        #Добавляем запрос в базу данных
        await add_query_to_history(message.from_user.id, product_sku)
    else:
        await message.answer("Информация о товаре не найдена.")
    await state.set_state(States.waiting_for_product_info)
    await state.update_data(product_sku=product_sku)


async def process_product_info(product_sku, chat_id):
    """Функция для обработки артикула по подписке"""
    product_info = await get_product_info(product_sku)

    if product_info:
        info_message = "Информация о товаре:\n\n"
        for key, value in product_info.items():
            info_message += f"{key}: {value}\n"

        await bot.send_message(chat_id, info_message, reply_markup=keyboard_stop_not())

    else:
        print("Товар не найден")


async def schedule_subscribe_task(product_sku, chat_id):
    """Функция для запуска задачи по расписанию"""

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        process_product_info,
        "interval",
        args=[product_sku, chat_id],
        minutes=1,
        name="ProcessProductInfo"
    )

    scheduler.start()
    return scheduler


subscriptions = {}


@router.message(StateFilter(States.waiting_for_product_info))
@router.callback_query(F.data == "subscribe")
async def subscribe(callback: CallbackQuery, state: FSMContext):
    """Функция для подписки на уведомления"""
    text = (
        "Вы подписаны на уведомления!\n\n"
        "Сообщения будут приходить в чат каждые 5 минут."
    )
    await callback.message.answer(text)

    data = await state.get_data()
    product_sku = str(data["product_sku"])
    chat_id = callback.message.chat.id

    scheduler = await schedule_subscribe_task(product_sku, chat_id)
    subscriptions[(product_sku, chat_id)] = scheduler


async def stop_subscription_handler(message_or_callback: Union[Message, CallbackQuery], state: FSMContext):
    """Функция для отписки от уведомлений"""

    text = "Вы отписались от уведомлений!\n\n"

    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text)
    elif isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.answer(text)

    data = await state.get_data()
    product_sku = str(data["product_sku"])
    chat_id = message_or_callback.message.chat.id

    scheduler = subscriptions.get((product_sku, chat_id))

    if scheduler:
        scheduler.shutdown()
        del subscriptions[(product_sku, chat_id)]
    else:
        print("Уведомления не найдены.")


@router.callback_query(F.data == "stop_not")
async def callback_stop_subscription(callback: CallbackQuery, state: FSMContext):
    """Кнопка для отписки от уведомлений"""
    await stop_subscription_handler(callback, state)


@router.message(Command("stop_not"))
async def command_stop_subscription(message: Message, state: FSMContext):
    """Команда для отписки от уведомлений"""
    await stop_subscription_handler(message, state)
