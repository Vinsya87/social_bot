import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)
battles_logger = logging.getLogger('battles')
from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from events.models import BattleFormat, BattleType, ElementalBattle
from main.models import City, Country
from social_bot.config.config import dp, storage
from social_bot.handlers.common import (BattleCreation, BattleCreationCallback,
                                        BattleListCallback,
                                        BattleTypeCreationCallback,
                                        CityCallback, ConfirmCallback,
                                        CountryCallback, check_city,
                                        check_country, confirm_data,
                                        parse_date, parse_time)
from social_bot.keyboards.keyboards import (city_confirmation_keyboard,
                                            city_inline_key,
                                            country_confirmation_keyboard,
                                            make_battle_keyboard,
                                            offer_registration_key)
from users.models import User

router = Router()


async def print_all_data(storage):
    all_data = {}
    for key in storage.storage.keys():
        data = await storage.get_data(key)
        all_data[key] = data
    print(f'all_data - {all_data}')


async def print_fsm_data(state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    print(f'Current state: {current_state}')
    print(f'Data in state: {data}')


@dp.message(F.text.lower() == "test1")
async def test_battle(message: types.Message, state: FSMContext):
    await print_all_data(storage)
    await print_fsm_data(state)





@dp.message(F.text.lower() == "создать событие")
async def create_battle(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    try:
        profile = await User.objects.select_related(
            'country', 'city').aget(telegram_id=telegram_id)
        city = profile.city if profile.city else False
        country = profile.country if profile.country else False
        if not profile.identification:
            await offer_registration_key(message)
            return
        await city_inline_key(message, city)
        await state.update_data(
            country_of_battle=country,
            country_id=country.id,
            city_id=city.id,
            city_of_battle=city)
    except ObjectDoesNotExist as e:
        battles_logger.exception(f"Ошибка в create_battle: {e}")
        await offer_registration_key(message)
    except Exception as e:
        report = f"Ошибка в create_battle: {e}"
        battles_logger.info(report)


@dp.callback_query(
        StateFilter(None),
        BattleCreationCallback.filter(F.action == "city_create_battle"))
async def batlle_start_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Укажите точный адрес и место")
    await state.set_state(BattleCreation.address_of_battle)


@dp.callback_query(
        StateFilter(None),
        BattleCreationCallback.filter(F.action == "create_battle"))
async def batlle_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Укажите страну события")
    await state.set_state(BattleCreation.country_of_battle)


@router.message(BattleCreation.country_of_battle)
async def event_country(message: Message, state: FSMContext):
    country_of_battle = message.text
    telegram_id = message.from_user.id
    await state.update_data(
            telegram_id=telegram_id,
            country_of_battle=country_of_battle
            )
    found_countries = await check_country(country_of_battle)
    if found_countries:
        keyboard = country_confirmation_keyboard(found_countries)
        await message.answer(
            "Подтвердите страну",
            reply_markup=keyboard)
    else:
        await message.answer(
            "Такой страны нет в базе. Пожалуйста, введите другую страну.")


@dp.callback_query(
        StateFilter(BattleCreation),
        CountryCallback.filter(F.action == "country"))
async def get_input_country(
        callback_query: types.CallbackQuery,
        callback_data: CountryCallback,
        state: FSMContext):
    await callback_query.answer()
    country_id = callback_data.value
    await state.update_data(
        country_id=country_id,
        )
    await state.set_state(BattleCreation.city_of_battle)
    await callback_query.message.answer("Укажите город")


@dp.callback_query(
        StateFilter(BattleCreation),
        CountryCallback.filter(F.action == "get_edit_country"))
async def get_edit_country(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.message.answer("Введите другую страну")
    await state.set_state(BattleCreation.country_of_battle)


@dp.callback_query(
        StateFilter(BattleCreation),
        CityCallback.filter(F.action == "get_edit_city"))
async def get_edit_city(
        callback_query: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    await callback_query.message.answer("Введите другой город")
    await state.set_state(BattleCreation.city_of_battle)


@router.message(BattleCreation.city_of_battle)
async def event_city(message: Message, state: FSMContext):
    city_of_battle = message.text
    await state.update_data(
        city_of_battle=city_of_battle
        )
    user_data = await state.get_data()
    country_id = user_data.get('country_id')
    found_cities = await check_city(city_of_battle, country_id)
    if found_cities:
        keyboard = city_confirmation_keyboard(found_cities)
        await message.answer(
            "Подтвердите город",
            reply_markup=keyboard)
    else:
        countries = []
        keyboard = country_confirmation_keyboard(countries)
        await message.answer(
            "Такого города не найдено, попробуйте снова, или выберете другую страну",
            reply_markup=keyboard)


@dp.callback_query(
        StateFilter(BattleCreation),
        CityCallback.filter(F.action == "city"))
async def get_input_city(
        callback_query: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    await callback_query.answer()
    city_id = callback_data.value
    await state.update_data(
        city_id=city_id,
        )
    await state.set_state(BattleCreation.address_of_battle)
    await callback_query.message.answer("Укажите точный адрес и место")


@router.message(BattleCreation.address_of_battle)
async def event_address(message: Message, state: FSMContext):
    address_of_battle = message.text
    await confirm_data(message, state, address_of_battle, 'address_of_battle')


@dp.callback_query(
        StateFilter(BattleCreation),
        ConfirmCallback.filter(F.action == "address_of_battle"))
async def event_address_confirm(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.answer()
    await state.set_state(BattleCreation.name_of_battle)
    await callback_query.message.answer("Название события")


@router.message(BattleCreation.name_of_battle)
async def event_name(message: Message, state: FSMContext):
    name_of_battle = message.text
    telegram_id = message.from_user.id
    await state.update_data(
        telegram_id=telegram_id,
        )
    await confirm_data(message, state, name_of_battle, 'name_of_battle')


@dp.callback_query(
        StateFilter(BattleCreation),
        ConfirmCallback.filter(F.action == "name_of_battle"))
async def event_name_confirm(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.answer()
    await state.set_state(BattleCreation.description_of_battle)
    await callback_query.message.answer("Описание события")


@router.message(BattleCreation.description_of_battle)
async def event_description(message: Message, state: FSMContext):
    description_of_battle = message.text
    await confirm_data(
        message,
        state,
        description_of_battle,
        'description_of_battle')


@dp.callback_query(
        StateFilter(BattleCreation),
        ConfirmCallback.filter(F.action == "description_of_battle"))
async def event_description_confirm(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.answer()
    await state.set_state(BattleCreation.start_date_of_battle)
    await callback_query.message.answer("Укажите дату события, формат ввода '12.05.2020'")


@router.message(BattleCreation.start_date_of_battle)
async def event_start_date(message: Message, state: FSMContext):
    start_date_of_battle = message.text
    start_date = parse_date(start_date_of_battle)
    if start_date is not None:
        try:
            await confirm_data(message, state, start_date, 'start_date_of_battle')
        except ValueError:
            await message.answer(
                "Некорректный формат даты. Пожалуйста, введите дату в формате 'день месяц год', например, '20 03 2024'.")
    else:
        await message.answer(
            "Некорректный формат даты или введенная дата меньше текущей. Пожалуйста, введите дату в формате 'день месяц год', например, '20 03 2024'.")


@dp.callback_query(
        StateFilter(BattleCreation),
        ConfirmCallback.filter(F.action == "start_date_of_battle"))
async def event_start_date_confirm(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.answer()
    await state.set_state(BattleCreation.start_time_of_battle)
    await callback_query.message.answer("Укажите время начала события, формат ввода '12:15'")


@router.message(BattleCreation.start_time_of_battle)
async def event_start_time(message: Message, state: FSMContext):
    start_time_of_battle = message.text
    start_time = parse_time(start_time_of_battle)
    if start_time is not None:
        try:
            await confirm_data(message, state, start_time, 'start_time_of_battle')
        except ValueError:
            await message.answer("Некорректный формат времени. Пожалуйста, введите в формате 'часы минуты', например, '20 10'.")
    else:
        await message.answer("Некорректный формат времени. Пожалуйста, введите в формате 'часы минуты', например, '20 10'.")


@dp.callback_query(
        StateFilter(BattleCreation),
        ConfirmCallback.filter(F.action == "start_time_of_battle"))
async def event_start_time_confirm(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.answer()
    await state.set_state(BattleCreation.battle_type_of_battle)
    battle = await storage.get_data("battle_types")
    keyboard = await make_battle_keyboard(battle, "battle_types")
    await callback_query.message.answer(
        text="Выберите тип битвы:",
        reply_markup=keyboard
    )


@dp.callback_query(
        StateFilter(BattleCreation),
        BattleTypeCreationCallback.filter(F.type == "battle_types"))
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


@dp.callback_query(
        StateFilter(BattleCreation),
        BattleTypeCreationCallback.filter(F.type == "battle_formats"))
async def event_end(
        message: Message,
        callback_data: BattleTypeCreationCallback,
        state: FSMContext):
    user_data = await state.get_data()
    battle_format_id = callback_data.value
    country_id = user_data.get('country_id')
    city_id = user_data.get('city_id')
    start_time = user_data['start_time_of_battle']
    start_date = user_data['start_date_of_battle']
    battle_types_id = user_data.get('battle_types_id')
    try:
        country = await Country.objects.aget(id=country_id)
        city = await City.objects.aget(id=city_id)
        battle_format = await BattleFormat.objects.aget(
            id=battle_format_id)
        battle_type = await BattleType.objects.aget(
            id=battle_types_id)
        user = await User.objects.aget(
                telegram_id=user_data['telegram_id'])
        event = await ElementalBattle.objects.acreate(
            country=country,
            city=city,
            address=user_data['address_of_battle'],
            name=user_data['name_of_battle'],
            description=user_data['description_of_battle'],
            start_date=start_date,
            start_time=start_time,
            organizer=user,
            battle_format_id=battle_format_id,
            battle_type_id=battle_types_id,
            )
        text = f"Вы создали событие:\n" \
               f"Страна: {event.country}\n" \
               f"Город: {event.city or 'Не указано'}\n"\
               f"Адрес: {event.address or 'Не указано'}\n"\
               f"Название: {event.name or 'Не указана'}\n" \
               f"Описание: {event.description or 'Не указан'}\n" \
               f"Формат: {battle_format or 'Не указан'}\n" \
               f"Тип: {battle_type or 'Не указан'}\n" \
               f"Дата: {event.start_date or 'Не указан'}\n" \
               f"Начало: {event.start_time or 'Не указан'}"
        await message.answer(
            text=f"{text}",
            show_alert=True
            )

    except ElementalBattle.DoesNotExist:
        report = "Ошибка при создании события: event_end"
        battles_logger.exception(report)
        await message.answer(
            "Произошла ошибка при создании события.")
    except Exception as e:
        report = f"Ошибка при создании события: {e}"
        battles_logger.exception(report)
        await message.answer(
            "Произошла ошибка при создании события.")
    await state.clear()
