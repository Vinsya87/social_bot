from users.models import User


async def update_profile(telegram_id: int, **params):
    profile = await User.objects.aget(telegram_id=telegram_id)
    for key, value in params.items():
        setattr(profile, key, value)
    await profile.asave()
