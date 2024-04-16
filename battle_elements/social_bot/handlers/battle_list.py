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
from social_bot.handlers.common import (BattleList, BattleListCallback,
                                        BattleTypeCreationCallback,
                                        CityCallback, ConfirmCallback,
                                        CountryCallback, check_city,
                                        check_country, confirm_data,
                                        parse_date, parse_time)
from social_bot.keyboards.keyboards import (battle_list_key,
                                            city_confirmation_keyboard,
                                            city_inline_key,
                                            country_confirmation_keyboard,
                                            make_battle_keyboard,
                                            offer_registration_key)
from users.models import User

router = Router()


async def get_list_of_battles(
        message,
        list_battles,
        state: FSMContext,
        is_user):
    """Выдает список событий, на основе - юзеру, или общие
    """
    try:
        response_text = "Список всех битв:\n"
        if not list_battles:
            text = "В данном городе нет событий"
            await message.answer(text)
            await state.clear()
            return
        for battle in list_battles:
            photographer = 'Будет' if battle['photographer']  else "Нет"
            is_active = 'Прошла' if battle['is_active']  else "Ожидает проверки"
            rated_game = 'Да' if battle['rated_game']  else "Нет"
            battle_format = battle['battle_format'] if battle['battle_format'] else "Не указано"
            battle_type = battle['battle_type'] if battle['battle_type'] else "Не указано"
            response_text += f"Название: {battle['name']}\n" \
                             f"Описание: {battle['description']}\n" \
                             f"Страна: {battle['country']}\n" \
                             f"Город: {battle['city']}\n" \
                             f"Фотограф: {photographer}\n" \
                             f"Формат: {battle_format}\n" \
                             f"Тип: {battle_type}\n" \
                             f"Рейтинговая: {rated_game}\n" \
                             f"Организатор: {battle['organizer']}\n" \
                             f"Статус: {battle['status']}\n"
            if is_user:
                response_text += f"Проверка: {is_active}\n"
                response_text += "----------------------------------\n"
            else:
                response_text += "----------------------------------\n"
        await message.answer(response_text)
    except Exception as e:
        logging.error(f"Ошибка при отправке списка битв: {e}")
        await message.answer(
            "Произошла ошибка при попытке получить список битв.")
    await state.clear()


@dp.message(F.text.lower() == "список битв стихии")
async def list_battles(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    try:
        profile = await User.objects.select_related(
            'city').aget(telegram_id=telegram_id)
        city = profile.city if profile.city else False
        if profile.identification:
            await battle_list_key(message, city, city.id)
        else:
            await offer_registration_key(message)
    except ObjectDoesNotExist as e:
        battles_logger.exception(f"Ошибка в list_battles: {e}")
        await offer_registration_key(message)
    except Exception as e:
        report = f"Ошибка в list_battles: {e}"
        battles_logger.info(report)


@dp.callback_query(
        StateFilter(None),
        BattleListCallback.filter(F.action == "battle_list"))
async def batlle_start_user(
        callback: types.CallbackQuery,
        callback_data: BattleListCallback,
        state: FSMContext):
    """Выбор страны для списка событий"""
    await callback.message.answer("Укажите страну события")
    await state.set_state(BattleList.country_of_battle)


@router.message(BattleList.country_of_battle)
async def event_country(message: Message, state: FSMContext):
    """Проверка страны"""
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
        StateFilter(BattleList),
        CountryCallback.filter(F.action == "country"))
async def get_input_country(
        callback_query: types.CallbackQuery,
        callback_data: CountryCallback,
        state: FSMContext):
    """Подтверждение страны"""
    await callback_query.answer()
    country_id = callback_data.value
    await state.update_data(
        country_id=country_id,
        )
    await state.set_state(BattleList.city_of_battle)
    await callback_query.message.answer("Укажите город")


@dp.callback_query(
        StateFilter(BattleList),
        CountryCallback.filter(F.action == "get_edit_country"))
async def get_edit_country(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    """Выбор другой страны"""
    await callback_query.message.answer("Введите другую страну")
    await state.set_state(BattleList.country_of_battle)


@dp.callback_query(
        StateFilter(BattleList),
        CityCallback.filter(F.action == "get_edit_city"))
async def get_edit_city(
        callback_query: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    """Выбор другого города"""
    await callback_query.message.answer("Введите другой город")
    await state.set_state(BattleList.city_of_battle)


@router.message(BattleList.city_of_battle)
async def event_city(message: Message, state: FSMContext):
    city_of_battle = message.text
    await state.update_data(
        city_of_battle=city_of_battle
        )
    """Проверка города"""
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
        StateFilter(BattleList),
        CityCallback.filter(F.action == "city"))
async def get_input_city(
        callback: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    """Подтверждение города"""
    await callback.answer()
    city_id = callback_data.value
    await batlle_start_list(callback.message, city_id, state)


@dp.callback_query(
        StateFilter(None),
        BattleListCallback.filter(F.action == "battle_list_city"))
async def batlle_start_user(
        callback: types.CallbackQuery,
        callback_data: BattleListCallback,
        state: FSMContext):
    """Получаем список на основе города юзера"""
    city_id = callback_data.value
    await batlle_start_list(callback.message, city_id, state)


async def batlle_start_list(message, city_id, state):
    """Формирование списка и передача его в печать"""
    list_battles = []
    print('batlle_start_list')
    async for battle in ElementalBattle.objects.select_related(
            'country',
            'battle_format',
            'battle_type',
            'organizer',
            'city').filter(city_id=city_id, is_active=True):
        list_battles.append(
            {
                'name': battle.name,
                'description': battle.description,
                'country': battle.country,
                'city': battle.city,
                'photographer': battle.photographer,
                'battle_format': battle.battle_format,
                'battle_type': battle.battle_type,
                'organizer': battle.organizer.first_name,
                'rated_game': battle.rated_game,
                'is_active': battle.is_active,
                'status': battle.get_status_display(),
            })
    await get_list_of_battles(message, list_battles, state, is_user=False)


@dp.message(F.text.lower() == "мои события")
async def list_battles_user(message: Message, state: FSMContext):
    """Получение юзера для передачи в формирование списка"""
    await state.clear()
    telegram_id = message.from_user.id
    try:
        profile = await User.objects.select_related(
            'city').aget(telegram_id=telegram_id)
        user_id = profile.id
        if profile.identification:
            await batlle_user_list(message, user_id, state)
        else:
            await offer_registration_key(message)
    except ObjectDoesNotExist as e:
        battles_logger.exception(f"Ошибка ObjectDoesNotExist в list_battles_user: {e}")
        await offer_registration_key(message)
    except Exception as e:
        report = f"Ошибка Exception в list_battles_user: {e}"
        battles_logger.info(report)


async def batlle_user_list(message, user_id, state):
    """Формирование списка событий юзера и передача его в печать"""
    list_battles = []
    print('batlle_start_list')
    async for battle in ElementalBattle.objects.select_related(
            'country',
            'battle_format',
            'battle_type',
            'organizer',
            'city').filter(organizer_id=user_id):
        print(battle)
        list_battles.append(
            {
                'name': battle.name,
                'description': battle.description,
                'country': battle.country,
                'city': battle.city,
                'photographer': battle.photographer,
                'battle_format': battle.battle_format,
                'battle_type': battle.battle_type,
                'organizer': battle.organizer.first_name,
                'rated_game': battle.rated_game,
                'status': battle.get_status_display(),
                'is_active': battle.is_active,
            })
    await get_list_of_battles(message, list_battles, state, is_user=True)
