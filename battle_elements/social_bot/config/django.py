from asgiref.sync import sync_to_async
from django.core.cache import cache
from events.models import BattleFormat, BattleType
from social_bot.config.config import storage


class DataLoader:
    def __init__(self, storage):
        self.storage = storage

    # async def load_data(self, data_type, queryset):
    #     data = await sync_to_async(list)(queryset)
    #     # await self.storage.set_data(key=None, data={data_type: list(data)})
    #     await self.storage.set_data(key=data_type, data={data_type: list(data)})
    #     print(data)
    async def load_data(self, data_type, queryset):
        data = await sync_to_async(list)(queryset)
        formatted_data = [{"id": item.id, "name": str(item)} for item in data]
        await self.storage.set_data(key=data_type, data={data_type: formatted_data})
        print(formatted_data)


async def load_data():
    loader = DataLoader(storage)
    await loader.load_data("battle_formats", BattleFormat.objects.all())
    await loader.load_data("battle_types", BattleType.objects.all())
