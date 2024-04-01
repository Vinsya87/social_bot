from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from social_bot.handlers.commom import (BattleCreationCallback,
                                        BattleTypeCreationCallback,
                                        RegistrCallback)


async def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Список Битв стихии"),
        types.KeyboardButton(text="Личный кабинет")
    )
    builder.row(
        types.KeyboardButton(text="Создать событие"),
        types.KeyboardButton(text="Test1")
    )
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard


async def get_contact_keyboard():
    kb = [
        [
            types.KeyboardButton(
                text="Номер телефона",
                request_contact=True),
            types.KeyboardButton(text="Назад"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Нажмите на кнопку"
    )
    return keyboard


async def city_inline(message: types.Message, city):
    builder = InlineKeyboardBuilder()
    if city:
        print('offer_registration')
        builder.row(types.InlineKeyboardButton(
            text="Да",
            callback_data="city_inline")
        )
        builder.row(types.InlineKeyboardButton(
            text="Нет",
            callback_data=BattleCreationCallback(action="create_battle").pack())
        )
        # builder.row(types.InlineKeyboardButton(
        #     text="Назад",
        #     callback_data=RegistrCallback(action="back_start").pack())
        # )
    else:
        print('NOO')
        builder.row(types.InlineKeyboardButton(
            text="NOO",
            callback_data=BattleCreationCallback(action="create_battle").pack())
        )
    await message.answer(
        f"Создать в городе {city}?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


async def make_battle_keyboard(battle, battle_type_key):
    builder = InlineKeyboardBuilder()
    for battle_type in battle[battle_type_key]:
        callback_data = BattleTypeCreationCallback(
            action="change",
            type=battle_type_key,
            value=battle_type['id']
        )
        builder.button(
            text=battle_type["name"],
            callback_data=callback_data
        )
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard