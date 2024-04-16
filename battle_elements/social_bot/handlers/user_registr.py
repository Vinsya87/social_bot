import logging

logger = logging.getLogger(__name__)
registr_logger = logging.getLogger('registr')
from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from main.models import City, Country
from social_bot.command.clients import update_profile
# from asgiref.sync import sync_to_async
from social_bot.config.config import dp
from social_bot.handlers.common import (CityCallback, CountryCallback,
                                        EditOfficeCallback, RegistrCallback,
                                        check_city, check_country)
from social_bot.keyboards.keyboards import (city_confirmation_keyboard,
                                            country_confirmation_keyboard,
                                            edit_change_data_keyboard,
                                            get_contact_keyboard,
                                            get_main_keyboard,
                                            offer_registration_key)
from users.models import User

router = Router()


class Registration(StatesGroup):
    entering_phone = State()
    entering_name = State()
    entering_country = State()
    entering_city = State()
    user_id = State()


class EditOffice(StatesGroup):
    edit_phone = State()
    edit_name = State()
    edit_country = State()
    edit_city = State()
    # user_id = State()


async def show_profile_form(message, profile):
    print('show_profile_form')
    text = f"Ваш профиль:\n" \
           f"ID: {profile.telegram_id}\n" \
           f"Логин: {profile.username or 'Не указано'}\n"\
           f"Имя: {profile.first_name or 'Не указано'}\n"\
           f"Страна: {profile.country or 'Не указана'}\n" \
           f"Город: {profile.city or 'Не указан'}\n" \
           f"Основной язык: {profile.language_code or 'Не указан'}\n" \
           f"Номер телефона: {profile.phone_number or 'Не указан'}"
    options = ['Имя',
               'Город',
               'Номер телефона',
               'Оставить без изменений'
               ]
    keyboard = await get_main_keyboard()
    await message.answer(text, reply_markup=keyboard)
    await message.answer(
            'Что нужно изменить?',
            reply_markup=edit_change_data_keyboard(options)
        )


@dp.callback_query(
        StateFilter(None),
        RegistrCallback.filter(F.action == "back_start"))
async def back_start(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = await get_main_keyboard()
    await message.answer("Выберите действие", reply_markup=keyboard)


@dp.message(F.text.lower() == "личный кабинет")
async def office_user(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    try:
        profile = await User.objects.select_related(
            'country', 'city').aget(telegram_id=telegram_id)
        print(f'profile {profile.country}')
        if profile.identification:
            await show_profile_form(message, profile)
        else:
            await offer_registration_key(message)
    except User.DoesNotExist:
        await offer_registration_key(message)
    except Exception as e:
        logging.error(f"Error in office_user: {e}")
        print(f"Error in office_user: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")


@dp.callback_query(
        StateFilter(None),
        RegistrCallback.filter(F.action == "registr"))
async def start_registration(callback: types.CallbackQuery, state: FSMContext):
    keyboard = await get_contact_keyboard()
    await callback.message.answer(
        "Укажите номер телефона, нажав на кнопку",
        reply_markup=keyboard)
    await state.set_state(Registration.entering_phone)


@dp.callback_query(EditOfficeCallback.filter(F.action == 'no_edit'))
async def get_no_edit_office(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    print('get_no_edit_office')
    keyboard = await get_main_keyboard()
    await callback_query.message.answer(
        'Отмена',
        reply_markup=keyboard)
    await state.clear()


@dp.callback_query(StateFilter(None), EditOfficeCallback.filter(F.action))
async def get_edit_office(
        callback_query: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext):
    print('get_edit_office')
    await callback_query.answer()
    if callback_data.action == 'Имя':
        await callback_query.message.answer('Введите ваше имя')
        await state.set_state(EditOffice.edit_name)
    elif callback_data.action == 'Город':
        await callback_query.message.answer(
            'Сначала введите страну в который вы сейчас')
        await state.set_state(EditOffice.edit_country)
    elif callback_data.action == 'Номер телефона':
        keyboard = await get_contact_keyboard()
        await callback_query.message.answer(
            "Изменился номер телефона? Нажмите на кнопку",
            reply_markup=keyboard)
        await state.set_state(EditOffice.edit_phone)


async def update_profile_wrapper(
        message: Message,
        state: FSMContext,
        params: dict):
    telegram_id = message.from_user.id
    await update_profile(telegram_id, **params)
    keyboard = await get_main_keyboard()
    await message.answer(
        f"{params.get('report')}",
        reply_markup=keyboard)
    await state.clear()


@router.message(EditOffice.edit_name)
async def edit_name(message: Message, state: FSMContext):
    report = f"Спасибо, ваше имя записано как {message.text}"
    await update_profile_wrapper(message, state, {
        'report': report,
        'first_name': message.text})


@router.message(EditOffice.edit_country)
async def edit_country(message: Message, state: FSMContext):
    country_name = message.text
    telegram_id = message.from_user.id
    await state.update_data(
            telegram_id=telegram_id,
            )
    found_countries = await check_country(country_name)
    if found_countries:
        keyboard = country_confirmation_keyboard(found_countries)
        await message.answer(
            "Подтвердите страну",
            reply_markup=keyboard)
    else:
        await message.answer(
            "Такой страны нет в базе. Пожалуйста, введите другую страну.")


@dp.callback_query(
        StateFilter(EditOffice),
        CountryCallback.filter(F.action == "get_edit_country"))
async def get_edit_country_office(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.message.answer("Введите другую страну")
    await state.set_state(EditOffice.edit_country)


@dp.callback_query(
        StateFilter(EditOffice),
        CityCallback.filter(F.action == "get_edit_city"))
async def get_edit_city_office(
        callback_query: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    await callback_query.message.answer("Введите другой город")
    await state.set_state(EditOffice.entering_city)


@dp.callback_query(
        StateFilter(EditOffice),
        CountryCallback.filter(F.action == "country"))
async def get_input_country_office(
        callback_query: types.CallbackQuery,
        callback_data: CountryCallback,
        state: FSMContext):
    print('get_input_country_office')
    await callback_query.answer()
    country_id = callback_data.value
    await state.update_data(
            country_id=country_id,
            )
    country = await Country.objects.aget(id=country_id)
    telegram_id = await state.get_data()
    telegram_id = telegram_id.get('telegram_id')
    params = {
        'country': country}
    await update_profile(telegram_id, **params)
    await callback_query.message.answer(
            'Введите город')
    await state.set_state(EditOffice.edit_city)


@router.message(EditOffice.edit_city)
async def edit_city(message: Message, state: FSMContext):
    city_name = message.text
    user_data = await state.get_data()
    country_id = user_data.get('country_id')
    found_cities = await check_city(city_name, country_id)
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
        StateFilter(EditOffice),
        CityCallback.filter(F.action == "city"))
async def get_input_city_office(
        callback_query: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    city_id = callback_data.value
    city = await City.objects.aget(id=city_id)
    telegram_id = await state.get_data()
    telegram_id = telegram_id.get('telegram_id')
    report = f"Спасибо, город записан как {city.name.capitalize()}"
    params = {
        'city': city}
    await update_profile(telegram_id, **params)
    keyboard = await get_main_keyboard()
    await state.clear()
    await callback_query.message.answer(
        f"{report}",
        reply_markup=keyboard)


@router.message(EditOffice.edit_phone)
async def edit_phone(message: Message, state: FSMContext):
    if (message.contact is not None and
        hasattr(message.contact, 'phone_number') and
            message.contact.user_id == message.from_user.id):
        profile = await User.objects.aget(
            telegram_id=message.contact.user_id)
        current_phone_number = profile.phone_number if profile else None
        new_phone_number = message.contact.phone_number
        if new_phone_number == current_phone_number:
            keyboard = await get_main_keyboard()
            await state.clear()
            await message.answer(
                "Текущий номер телефона уже записан в профиле.",
                reply_markup=keyboard)
        else:
            report = f"Спасибо, телефон записан как {message.contact.phone_number}"
            await update_profile_wrapper(message, state, {
                'report': report,
                'phone_number': message.contact.phone_number
                })
    else:
        keyboard = await get_contact_keyboard()
        await message.answer(
            "Укажите номер телефона, нажав на кнопку",
            reply_markup=keyboard)


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
    await message.answer("Введите страну в который вы сейчас")
    await state.set_state(Registration.entering_country)


@router.message(Registration.entering_country)
async def enter_country(message: Message, state: FSMContext):
    country_name = message.text
    found_countries = await check_country(country_name)
    if found_countries:
        keyboard = country_confirmation_keyboard(found_countries)
        await message.answer(
            "Подтвердите страну",
            reply_markup=keyboard)
    else:
        await message.answer(
            "Такой страны нет в базе. Пожалуйста, введите другую страну.")


@dp.callback_query(
        StateFilter(Registration),
        CountryCallback.filter(F.action == "get_edit_country"))
async def get_edit_country(
        callback_query: types.CallbackQuery,
        state: FSMContext):
    await callback_query.message.answer("Введите другую страну")
    await state.set_state(Registration.entering_country)


@dp.callback_query(
        StateFilter(Registration),
        CityCallback.filter(F.action == "get_edit_city"))
async def get_edit_city(
        callback_query: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    await callback_query.message.answer("Введите другой город")
    await state.set_state(Registration.entering_city)


@dp.callback_query(
        StateFilter(Registration),
        CountryCallback.filter(F.action == "country"))
async def get_input_country(
        callback_query: types.CallbackQuery,
        callback_data: CountryCallback,
        state: FSMContext):
    await callback_query.answer()
    # country = callback_data.name
    country_id = callback_data.value
    await state.update_data(
        country_id=country_id,
        # country=country
        )
    await state.set_state(Registration.entering_city)
    await callback_query.message.answer("Введите ваш город")


@router.message(Registration.entering_city)
async def enter_city(message: Message, state: FSMContext):
    city_name = message.text
    user_data = await state.get_data()
    country_id = user_data.get('country_id')
    found_cities = await check_city(city_name, country_id)
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
        StateFilter(Registration),
        CityCallback.filter(F.action == "city"))
async def get_input_city(
        callback_query: types.CallbackQuery,
        callback_data: CityCallback,
        state: FSMContext):
    user_data = await state.get_data()
    try:
        profile = await User.objects.aget(
            telegram_id=user_data['telegram_id'])
    except User.DoesNotExist:
        profile = await User.objects.acreate(
            telegram_id=user_data['telegram_id'],
            username=user_data['username'],
            language_code=user_data['language_code'],
            )
    country_id = user_data.get('country_id')
    city_id = callback_data.value
    print(f'country_id {country_id}')
    country = await Country.objects.aget(id=country_id)
    city = await City.objects.aget(id=city_id)
    print(f'country {country}')
    profile.phone_number = user_data.get('phone_number', '')
    first_name = user_data.get('first_name', '')
    profile.first_name = first_name.capitalize()
    profile.country = country
    profile.city = city
    profile.identification = True
    await profile.asave()
    text = f"Спасибо за регистрацию!\n" \
           f"Ваш профиль:\n" \
           f"ID: {profile.telegram_id}\n" \
           f"Логин: {profile.username or 'Не указано'}\n" \
           f"Имя: {profile.first_name or 'Не указано'}\n" \
           f"Страна: {profile.country or 'Не указана'}\n" \
           f"Город: {profile.city or 'Не указан'}\n" \
           f"Основной язык: {profile.language_code or 'Не указан'}\n" \
           f"Номер телефона: {profile.phone_number or 'Не указан'}"
    keyboard = await get_main_keyboard()
    await callback_query.message.answer(
        text,
        reply_markup=keyboard)
    await state.clear()
