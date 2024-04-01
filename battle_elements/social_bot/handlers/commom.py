import re
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from social_bot.config.config import bot, dp


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


class BattleCreationCallback(CallbackData, prefix="battlebot"):
    action: str
    value: Optional[int] = None


class BattleTypeCreationCallback(CallbackData, prefix="battletypebot"):
    action: str
    type: str
    value: Optional[int] = None



class RegistrCallback(CallbackData, prefix="regbot"):
    action: str
    value: Optional[int] = None


def parse_date(input_date):
    match = re.match(r'(\d{1,2})\D+(\d{1,2})\D+(\d{4})', input_date)
    if match:
        day, month, year = map(int, match.groups())
        try:
            return datetime(year, month, day).date()
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
