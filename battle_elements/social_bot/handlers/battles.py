import logging
from datetime import datetime
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from events.models import ElementalBattle
from social_bot.config.config import bot, dp, storage
from social_bot.handlers.commom import (BattleCreation, BattleCreationCallback,
                                        BattleTypeCreationCallback,
                                        RegistrCallback, parse_date,
                                        parse_time)
from social_bot.handlers.user_registr import offer_registration
from social_bot.keyboards.keyboards import city_inline, make_battle_keyboard
from users.models import Profile

router = Router()


async def get_list_of_battles(message):
    try:
        all_battles = await sync_to_async(list)(
            ElementalBattle.objects
            .select_related('battle_format', 'organizer').all())
        response_text = "Список всех битв:\n"
        for battle in all_battles:
            response_text += f"- {battle.name}\n" \
                             f"- {battle.description}\n" \
                             f"- {battle.country}\n" \
                             f"- {battle.city}\n" \
                             f"- {battle.photographer}\n" \
                             f"- {battle.battle_format.name}\n" \
                             f"- {battle.organizer.first_name}\n" \
                             f"- {battle.get_status_display()}\n" \
                             "----------------------------------\n"
        await message.answer(response_text)
    except Exception as e:
        logging.error(f"Ошибка при отправке списка битв: {e}")
        await message.answer(
            "Произошла ошибка при попытке получить список битв.")


@dp.message(F.text.lower() == "список битв стихии")
async def list_battles(message: types.Message):
    telegram_id = message.from_user.id
    try:
        print('list_battles')
        profile = await Profile.objects.aget(telegram_id=telegram_id)
        if profile.identification:
            await get_list_of_battles(message)
        else:
            await offer_registration(message)
    except ObjectDoesNotExist:
        await offer_registration(message)


@dp.message(F.text.lower() == "создать событие")
async def create_battle(message: types.Message):
    telegram_id = message.from_user.id
    try:
        profile = await Profile.objects.aget(telegram_id=telegram_id)
        city = profile.city if profile.city else False
        await city_inline(message, city)
    except ObjectDoesNotExist:
        await offer_registration(message)


# @router.message(BattleCreation.entering_name)
@dp.callback_query(
        StateFilter(None),
        BattleCreationCallback.filter(F.action == "create_battle"))
async def batlle_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Укажите страну события")
    await state.set_state(BattleCreation.country_of_battle)


@router.message(BattleCreation.country_of_battle)
async def event_city(message: Message, state: FSMContext):
    country_of_battle = message.text
    await state.update_data(country_of_battle=country_of_battle)
    await message.answer("Укажите город")
    await state.set_state(BattleCreation.city_of_battle)


@router.message(BattleCreation.city_of_battle)
async def event_address(message: Message, state: FSMContext):
    city_of_battle = message.text
    await state.update_data(city_of_battle=city_of_battle)
    await message.answer("Адрес")
    await state.set_state(BattleCreation.address_of_battle)


@router.message(BattleCreation.address_of_battle)
async def event_name(message: Message, state: FSMContext):
    address_of_battle = message.text
    await state.update_data(address_of_battle=address_of_battle)
    await message.answer("Название события")
    await state.set_state(BattleCreation.name_of_battle)


@router.message(BattleCreation.name_of_battle)
async def event_description(message: Message, state: FSMContext):
    name_of_battle = message.text
    await state.update_data(name_of_battle=name_of_battle)
    await message.answer("Описание события")
    await state.set_state(BattleCreation.description_of_battle)


@router.message(BattleCreation.description_of_battle)
async def event_start_date(message: Message, state: FSMContext):
    description_of_battle = message.text
    await state.update_data(description_of_battle=description_of_battle)
    await message.answer("Укажите дату события, формат ввода '12.05.2020'")
    await state.set_state(BattleCreation.start_date_of_battle)


@router.message(BattleCreation.start_date_of_battle)
async def event_start_time(message: Message, state: FSMContext):
    start_date_of_battle = message.text
    start_date = parse_date(start_date_of_battle)
    if start_date is not None:
        try:
            await state.update_data(start_date_of_battle=start_date)
            await message.answer("Укажите время начала события, формат ввода '12:15'")
            await state.set_state(BattleCreation.start_time_of_battle)
        except ValueError:
            await message.answer("Некорректный формат даты. Пожалуйста, введите дату в формате 'день месяц год', например, '20 03 2024'.")
    else:
        await message.answer("Некорректный формат даты. Пожалуйста, введите дату в формате 'день месяц год', например, '20 03 2024'.")


@router.message(BattleCreation.start_time_of_battle)
async def event_start_time(message: Message, state: FSMContext):
    start_time_of_battle = message.text
    start_time = parse_time(start_time_of_battle)
    print(f'start_time {start_time}')
    if start_time is not None:
        try:
            await state.update_data(start_time_of_battle=start_time)
            battle = await storage.get_data("battle_types")
            keyboard = await make_battle_keyboard(battle, "battle_types")
            await message.answer(
                text="Выберите тип битвы:",
                reply_markup=keyboard
            )
            await state.set_state(BattleCreation.battle_type_of_battle)
        except ValueError:
            await message.answer("Некорректный формат времени. Пожалуйста, введите в формате 'часы минуты', например, '20 10'.")
    else:
        await message.answer("22Некорректный формат времени. Пожалуйста, введите в формате 'часы минуты', например, '20 10'.")


# @router.message(BattleCreation.battle_type_of_battle)
@dp.callback_query(BattleTypeCreationCallback.filter(F.type == "battle_types"))
async def event_battle_types(
        callback: types.CallbackQuery,
        callback_data: BattleTypeCreationCallback,
        state: FSMContext):
    battle_types_id = callback_data.value
    await state.update_data(battle_types_id=battle_types_id)
    battle = await storage.get_data("battle_formats")
    keyboard = await make_battle_keyboard(battle, "battle_formats")
    await callback.message.answer(
        text="Выберите формат битвы:",
        reply_markup=keyboard
    )
    await state.set_state(BattleCreation.battle_format_of_battle)


# @router.message(BattleCreation.battle_format_of_battle)
@dp.callback_query(BattleTypeCreationCallback.filter(F.type == "battle_formats"))
async def event_end(
        message: Message,
        callback_data: BattleTypeCreationCallback,
        state: FSMContext):
    user_data = await state.get_data()
    battle_format_id = callback_data.value

    start_time = user_data['start_time_of_battle']
    start_date = user_data['start_date_of_battle']
    print(f'state {state}')
    try:
        await ElementalBattle.objects.acreate(
            country=user_data['country_of_battle'],
            city=user_data['city_of_battle'],
            address=user_data['address_of_battle'],
            name=user_data['name_of_battle'],
            description=user_data['description_of_battle'],
            start_date=start_date,
            start_time=start_time,
            organizer=await Profile.objects.aget(
                telegram_id=message.from_user.id),
            battle_format_id=battle_format_id,
            battle_type_id=user_data['battle_types_id'],
            )
    except ElementalBattle.DoesNotExist:
        pass
        
    await message.answer(
        "Спасибо! Событие - (тестовые):",)
    print(f"Спасибо! Событие - (тестовые): {user_data}")
    await state.clear()


# @dp.message(F.text.lower() == "test1")
async def test_battle(message: types.Message):
    battle = await storage.get_data("battle_types")
    keyboard = await make_battle_keyboard(message, battle)
    
    await message.answer(
        text="Выберите тип битвы:",
        reply_markup=keyboard
    )


@dp.message(F.text.lower() == "test1")
async def test_battle(message: types.Message):
    battle = await storage.get_data("battle_formats")
    keyboard = await make_battle_keyboard(message, battle, "battle_formats")
    
    await message.answer(
        text="Выберите формат битвы:",
        reply_markup=keyboard
    )
