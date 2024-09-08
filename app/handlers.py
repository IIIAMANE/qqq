from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq

router = Router()


class Buy(StatesGroup):
    item_name = State()


class SendMessage(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_message_text = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer("Добро пожаловать в магазин кроссовок!", reply_markup=kb.main)


@router.message(F.text == "Каталог")
async def catalog(message: Message):
    await message.answer(
        "Выберите категорию товара", reply_markup=await kb.categories()
    )


@router.message(F.text == "Корзина")
async def basket(message: Message):
    basket_data = await rq.get_basket(message.from_user.id)

    if basket_data and basket_data.item_name:
        items = {
            i.split(":")[0]: int(i.split(":")[1])
            for i in basket_data.item_name.split(",")
        }

        basket_content = "\n".join(
            [f"{item}: {quantity} шт." for item, quantity in items.items()]
        )
        await message.answer(
            f"Ваша корзина:\n{basket_content}", reply_markup=await kb.button_to_main()
        )
    else:
        await message.answer(
            "Ваша корзина пуста.", reply_markup=await kb.button_to_main()
        )


@router.callback_query(F.data.startswith("category_"))
async def category_callback(callback: CallbackQuery):
    await callback.answer("Вы выбрали категорию")
    await callback.message.answer(
        "Выберите товар по категории",
        reply_markup=await kb.items(int(callback.data.split("_")[1])),
    )


@router.callback_query(F.data.startswith("item_"))
async def item_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Buy.item_name)
    item_data = await rq.get_item(int(callback.data.split("_")[1]))
    await state.update_data(item_name=item_data.name)
    await callback.answer("Вы выбрали товар")
    await callback.message.answer(
        f"Название: {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price}$",
        reply_markup=await kb.shop_menu(),
    )


@router.callback_query(F.data == "to_basket")
async def basket_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item_name = data.get("item_name")
    tg_id = callback.from_user.id

    await rq.add_item_in_basket(tg_id, item_name)
    await callback.answer("Товар добавлен в корзину")
    await callback.message.answer(
        "Товар добавлен в корзину", reply_markup=await kb.button_to_main()
    )
    await state.clear()


@router.callback_query(F.data == "to_main")
async def back_to_menu(callback: CallbackQuery):
    await callback.answer("Вы вернулись на страницу каталога")
    await callback.message.answer(
        "Выберете категорию товара", reply_markup=await kb.categories()
    )


@router.message(Command("negr"))
async def StartSending(message: Message, state: FSMContext):
    if message.from_user.id == 500654705 or message.from_user.id == 1215183389:
        await message.answer("Вводи айди, кому отправлять")
        await state.set_state(SendMessage.waiting_for_user_id)


@router.message(SendMessage.waiting_for_user_id)
async def InputTgId(message: Message, state: FSMContext):
    await state.update_data(TgId=message.text)
    await state.set_state(SendMessage.waiting_for_message_text)
    await message.answer("Вводи сообщение")


@router.message(SendMessage.waiting_for_message_text)
async def final_send(message: Message, state: FSMContext):
    await state.update_data(TgMessage=message.text)
    data = await state.get_data()
    bot = message.bot
    await rq.send_message_to_user(bot, data["TgId"], data["TgMessage"])
    await message.answer("Сообщение отправлено")
    await state.clear()
    return data["TgId"], data["TgMessage"]
