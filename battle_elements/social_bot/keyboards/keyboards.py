from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from social_bot.handlers.common import (BattleCreationCallback,
                                        BattleListCallback,
                                        BattleTypeCreationCallback,
                                        CityCallback, ConfirmCallback,
                                        CountryCallback, EditOfficeCallback,
                                        RegistrCallback)


async def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Список Битв стихии"),
        types.KeyboardButton(text="Личный кабинет")
    )
    builder.row(
        types.KeyboardButton(text="Создать событие"),
        types.KeyboardButton(text="Мои события")
    )
    builder.row(
        types.KeyboardButton(text="Test1")
    )
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard


async def offer_registration_key(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Регистрация",
        callback_data=RegistrCallback(action="registr").pack())
    )
    builder.row(types.InlineKeyboardButton(
        text="Назад",
        callback_data=RegistrCallback(action="back_start").pack())
    )

    await message.answer(
        "Вы не зарегистрированы. Пройти регистрацию?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


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


async def city_inline_key(message: types.Message, city):
    builder = InlineKeyboardBuilder()
    print('city_inline_key')
    builder.row(types.InlineKeyboardButton(
        text="Да",
        callback_data=BattleCreationCallback(
            action="city_create_battle").pack())
    )
    builder.row(types.InlineKeyboardButton(
        text="Нет",
        callback_data=BattleCreationCallback(
            action="create_battle").pack())
    )
    await message.answer(
        f"Создать в городе {city}?",
        reply_markup=builder.as_markup(resize_keyboard=True),
        )


async def battle_list_key(message: types.Message, city, city_id):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Да",
        callback_data=BattleListCallback(
            action="battle_list_city",
            value=city_id).pack())
    )
    builder.row(types.InlineKeyboardButton(
        text="Выбрать другой",
        callback_data=BattleListCallback(
            action="battle_list").pack())
    )
    await message.answer(
        f"Показать события в {city}?",
        reply_markup=builder.as_markup(resize_keyboard=True),
        )


async def make_battle_keyboard(battle, battle_type_key):
    """Клавиатура для типа или формата"""
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


def edit_change_data_keyboard(options: list):
    """Клавиатура для редактирования профиля"""
    builder = InlineKeyboardBuilder()
    for option in options:
        if option == 'Оставить без изменений':
            builder.row(types.InlineKeyboardButton(
                    text=option,
                    callback_data=EditOfficeCallback(action="no_edit").pack())
                )
        else:
            builder.row(types.InlineKeyboardButton(
                    text=option,
                    callback_data=EditOfficeCallback(action=option).pack())
                )
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard


def country_confirmation_keyboard(countries: list[str]):
    """Выбор страны"""
    builder = InlineKeyboardBuilder()
    if countries:
        for country in countries:
            builder.row(types.InlineKeyboardButton(
                text=country["name"],
                callback_data=CountryCallback(
                    action="country",
                    # name=country["name"],
                    value=country["id"]).pack())
            )
        builder.row(types.InlineKeyboardButton(
                text="Ввести другую страну",
                callback_data=CountryCallback(
                    action="get_edit_country").pack()))
    else:
        builder.row(types.InlineKeyboardButton(
                text="Ввести другую страну",
                callback_data=CountryCallback(
                    action="get_edit_country").pack()))
    builder.row(types.InlineKeyboardButton(
            text="Отмена",
            callback_data=EditOfficeCallback(action="no_edit").pack()))
    keyboard = builder.as_markup()
    return keyboard


def city_confirmation_keyboard(cities: list[str]):
    """Выбор города"""
    builder = InlineKeyboardBuilder()
    for city in cities:
        builder.row(types.InlineKeyboardButton(
            text=city["name"],
            callback_data=CityCallback(action="city", value=city["id"]).pack())
        )
    builder.row(types.InlineKeyboardButton(
            text="Ввести другой город",
            callback_data=CityCallback(action="get_edit_city").pack())
        )
    builder.row(types.InlineKeyboardButton(
            text="Выбрать другую страну",
            callback_data=CountryCallback(action="get_edit_country").pack())
        )
    builder.row(types.InlineKeyboardButton(
            text="Отмена",
            callback_data=EditOfficeCallback(action="no_edit").pack()))
    keyboard = builder.as_markup()
    return keyboard

