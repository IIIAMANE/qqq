from app.database.models import async_session
from app.database.models import User, Category, Item, Basket
from sqlalchemy import select


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))


async def get_basket(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Basket).where(Basket.tg_id == tg_id))


async def add_item_in_basket(tg_id, item_name):
    async with async_session() as session:
        basket = await session.scalar(select(Basket).where(Basket.tg_id == tg_id))

        if basket:
            items = {}
            if basket.item_name:
                items = {
                    i.split(":")[0]: int(i.split(":")[1])
                    for i in basket.item_name.split(",")
                }

            if item_name in items:
                items[item_name] += 1
            else:
                items[item_name] = 1

            basket.item_name = ",".join([f"{k}:{v}" for k, v in items.items()])
        else:
            basket = Basket(tg_id=tg_id, item_name=f"{item_name}:1")
            session.add(basket)

        await session.commit()


async def send_message_to_user(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)
