import re
from datetime import datetime
from typing import Optional

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Q
from main.models import City, Country


class BattleCreation(StatesGroup):
    country_of_battle = State()
    city_of_battle = State()
    address_of_battle = State()
    name_of_battle = State()
    description_of_battle = State()
    start_date_of_battle = State()
    start_time_of_battle = State()
    battle_type_of_battle = State()
    battle_format_of_battle = State()
    photographer_of_battle = State()
    format_of_battle = State()
    organizer_of_battle = State()


class BattleList(StatesGroup):
    country_of_battle = State()
    city_of_battle = State()
    address_of_battle = State()
    name_of_battle = State()


class BattleCreationCallback(CallbackData, prefix="battlebot"):
    action: str
    value: Optional[int] = None


class BattleListCallback(CallbackData, prefix="battlelist"):
    action: str
    value: Optional[int] = None


class BattleTypeCreationCallback(CallbackData, prefix="battletypebot"):
    action: str
    type: str
    value: Optional[int] = None


class EditOfficeCallback(CallbackData, prefix="editbot"):
    action: str
    value: Optional[int] = None


class CountryCallback(CallbackData, prefix="country"):
    action: str
    name: Optional[str] = None
    value: Optional[int] = None


class ConfirmCallback(CallbackData, prefix="confirm"):
    action: str
    type: Optional[str] = None
    value: Optional[int] = None


class CityCallback(CallbackData, prefix="city"):
    action: str
    value: Optional[int] = None


class RegistrCallback(CallbackData, prefix="regbot"):
    action: str
    value: Optional[int] = None


def parse_date(input_date):
    match = re.match(r'(\d{1,2})\D+(\d{1,2})\D+(\d{4})', input_date)
    if match:
        day, month, year = map(int, match.groups())
        try:
            parsed_date = datetime(year, month, day).date()
            if parsed_date < datetime.now().date():
                return None
            return parsed_date
        except ValueError:
            return None
    else:
        return None


def parse_time(input_time):
    match = re.match(r'(\d{1,2})\D*(\d{1,2})', input_time)
    if match:
        hours, minutes = map(int, match.groups())
        if 0 <= hours < 24 and 0 <= minutes < 60:
            formatted_time = f"{hours:02d}:{minutes:02d}"
            return datetime.strptime(formatted_time, '%H:%M').time()
        else:
            return None
    else:
        return None


async def check_country(query):
    try:
        found_countries = []
        async for country in Country.objects.filter(
                Q(name__icontains=query) |
                Q(name__icontains=query.lower()) |
                Q(name__icontains=query.capitalize())
                ):
            country_name = country.name.capitalize()
            found_countries.append({'name': country_name, 'id': country.id})
        return found_countries
    except Country.DoesNotExist:
        return False


async def check_city(query, country_id):
    try:
        found_cities = []
        query_conditions = (
            Q(name__icontains=query) |
            Q(name__icontains=query.lower()) |
            Q(name__icontains=query.capitalize()))
        country_condition = Q(country_id=country_id)
        async for city in City.objects.filter(
            query_conditions & country_condition
        ):
            city_name = city.name.capitalize()
            found_cities.append({'name': city_name, 'id': city.id})
        return found_cities
    except City.DoesNotExist:
        return []


def confirm_keyboard(action):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
            text="Подтвердить",
            callback_data=ConfirmCallback(action=action).pack())
        )
    builder.row(types.InlineKeyboardButton(
            text="Отмена",
            callback_data=EditOfficeCallback(
                action="no_edit").pack()))
    keyboard = builder.as_markup()
    return keyboard


async def confirm_data(message, state, text, action):
    keyboard = confirm_keyboard(action)
    await state.update_data(**{action: text})
    report = "Подтвердите ввод или введите новое значение:\n" \
             f"<b>{text}</b>"
    await message.answer(
            f"{report}",
            reply_markup=keyboard)
