import logging

from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from social_bot.config.config import dp
from social_bot.keyboards.keyboards import get_main_keyboard
from users.models import User


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    username = message.from_user.username or ''
    language_code = message.from_user.language_code
    try:
        await User.objects.aget(telegram_id=telegram_id)
        keyboard = await get_main_keyboard()
        await message.answer("Добро пожаловать снова!", reply_markup=keyboard)
    except User.DoesNotExist:
        await User.objects.acreate(
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

