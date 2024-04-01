import logging
from typing import Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from events.models import ElementalBattle
from social_bot.config.config import bot, dp
from social_bot.handlers.user_registr import offer_registration
from social_bot.keyboards.keyboards import get_main_keyboard
from users.models import Profile

# @dp.message(F.text.lower() == "список битв стихии")
# async def list_battles(message: types.Message):
#     telegram_id = message.from_user.id
#     try:
#         profile = await sync_to_async(
#             Profile.objects.get)(telegram_id=telegram_id)
#         if profile.identification:
#             try:
#                 all_battles = await sync_to_async(list)(
#                     ElementalBattle.objects
#                     .select_related('battle_format', 'organizer').all())
#                 response_text = "Список всех битв:\n"
#                 for battle in all_battles:
#                     response_text += f"- {battle.name}\n" \
#                                      f"- {battle.description}\n" \
#                                      f"- {battle.country}\n" \
#                                      f"- {battle.city}\n" \
#                                      f"- {battle.photographer}\n" \
#                                      f"- {battle.battle_format.name}\n" \
#                                      f"- {battle.organizer.first_name}\n" \
#                                      f"- {battle.get_status_display()}\n" \
#                                      "----------------------------------\n"
#                 await message.answer(response_text)
#             except Exception as e:
#                 logging.error(f"Ошибка при отправке списка битв: {e}")
#                 await message.answer(
#                     "Произошла ошибка при попытке получить список битв.")
#         else:
#             await offer_registration(message)
#     except ObjectDoesNotExist:
#         await offer_registration(message)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or ''
    language_code = message.from_user.language_code
    try:
        await Profile.objects.aget(telegram_id=telegram_id)
        keyboard = await get_main_keyboard()
        await message.answer("Добро пожаловать!", reply_markup=keyboard)
    except Profile.DoesNotExist:
        await Profile.objects.acreate(
            telegram_id=telegram_id,
            username=username,
            language_code=language_code
        )
        keyboard = await get_main_keyboard()
        await message.answer("Добро пожаловать!", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды /start: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")


@dp.message(F.text.lower() == "назад")
async def back_start(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = await get_main_keyboard()
    await message.answer("Выберите действие", reply_markup=keyboard)

