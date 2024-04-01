import logging
from typing import Optional

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
# from asgiref.sync import sync_to_async
from social_bot.config.config import bot, dp
from social_bot.handlers.commom import RegistrCallback
from social_bot.keyboards.keyboards import (get_contact_keyboard,
                                            get_main_keyboard)
from users.models import Profile

router = Router()


class Registration(StatesGroup):
    entering_phone = State()
    entering_name = State()
    entering_country = State()
    entering_city = State()
    user_id = State()


async def offer_registration(message: types.Message):
    print('offer_registration')
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


async def show_profile_form(message, profile):
    print('show_profile_form')
    text = f"Ваш профиль:\n" \
           f"ID: {profile.telegram_id}\n" \
           f"Логин: {profile.username or 'Не указано'}\n" \
           f"Имя: {profile.first_name or 'Не указано'}\n" \
           f"Страна: {profile.country or 'Не указана'}\n" \
           f"Город: {profile.city or 'Не указан'}\n" \
           f"Основной язык: {profile.language_code or 'Не указан'}\n" \
           f"Номер телефона: {profile.phone_number or 'Не указан'}"
    keyboard = await get_main_keyboard()
    await message.answer(text, reply_markup=keyboard)


@dp.callback_query(StateFilter(None), RegistrCallback.filter(F.action == "back_start"))
async def back_start(message: types.Message, state: FSMContext):
    print('back_start2')
    await state.clear()
    keyboard = await get_main_keyboard()
    await message.answer("Выберите действие", reply_markup=keyboard)


@dp.message(F.text.lower() == "личный кабинет")
async def office_user(message: types.Message):
    print('office_user')
    telegram_id = message.from_user.id
    try:
        profile = await Profile.objects.aget(
            telegram_id=telegram_id)
        if profile.identification:
            await show_profile_form(message, profile)
        else:
            await offer_registration(message)
    except Profile.DoesNotExist:
        await offer_registration(message)
    except Exception as e:
        logging.error(f"Error in office_user: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")


# @router.message(StateFilter(None), F.text.lower() == "регистрация")
# async def start_registration(message: Message, state: FSMContext):
@dp.callback_query(
        StateFilter(None),
        RegistrCallback.filter(F.action == "registr"))
async def start_registration(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Registration.entering_phone)
    keyboard = await get_contact_keyboard()
    await callback.message.answer(
        "Укажите номер телефона, нажав на кнопку",
        reply_markup=keyboard)
    await state.set_state(Registration.entering_phone)


@router.message(Registration.entering_phone)
async def enter_phone(message: Message, state: FSMContext):
    if (message.contact is not None and
        hasattr(message.contact, 'phone_number') and
            message.contact.user_id == message.from_user.id):
        await state.update_data(
            phone_number=message.contact.phone_number,
            user_id=message.contact.user_id
            )
        await message.answer("Введите ваше имя.")
        await state.set_state(Registration.entering_name)
    else:
        keyboard = await get_contact_keyboard()
        await message.answer(
            "Укажите номер телефона, нажав на кнопку",
            reply_markup=keyboard)


@router.message(Registration.entering_name)
async def enter_name(message: Message, state: FSMContext):
    first_name = message.text
    telegram_id = message.from_user.id
    username = message.from_user.username
    language_code = message.from_user.language_code
    await state.update_data(
        first_name=first_name,
        telegram_id=telegram_id,
        username=username,
        language_code=language_code,
        )
    await message.answer("Введите вашу страну.")
    await state.set_state(Registration.entering_country)


@router.message(Registration.entering_country)
async def enter_country(message: Message, state: FSMContext):
    country = message.text
    await state.update_data(country=country)
    await message.answer("Введите ваш город.")
    await state.set_state(Registration.entering_city)


@router.message(Registration.entering_city)
async def enter_city(message: Message, state: FSMContext):
    city = message.text
    user_data = await state.get_data()
    try:
        profile = await Profile.objects.aget(telegram_id=user_data['telegram_id'])
        profile.phone_number = user_data.get('phone_number', '')
        profile.first_name = user_data.get('first_name', '')
        profile.country = user_data.get('country', '')
        profile.city = city
        profile.identification = True
        await profile.asave()
    except Profile.DoesNotExist:
        await Profile.objects.acreate(
            telegram_id=user_data['telegram_id'],
            username=user_data['username'],
            language_code=user_data['language_code'],
            phone_number=user_data.get('phone_number', ''),
            first_name=user_data.get('first_name', ''),
            country=user_data.get('country', ''),
            city=city,
            identification=True,
            )
    await message.answer(
        f"Спасибо за регистрацию! Ваши данные - (тестовые): {user_data}",)
    await state.clear()
