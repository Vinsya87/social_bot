from django.contrib import admin
from events.models import (BattleFormat, BattleType, ElementalBattle, Event,
                           EventType, Festival, League, Location,
                           Participation, Role, Series)


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizer', 'coordinator', 'start_date', 'status')
    search_fields = ('name', 'organizer__username', 'coordinator__username')
    inlines = [ParticipationInline]


@admin.register(BattleType)
class BattleTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'event_type', 'can_be_series', 'can_be_league', 'can_be_festival')
    list_filter = ('can_be_series', 'can_be_league', 'can_be_festival')


@admin.register(ElementalBattle)
class ElementalBattleAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'start_time', 'end_time', 'country', 'city', 'address', 'organizer', 'coordinator', 'status', 'is_active', 'battle_format', 'battle_type')
    search_fields = ('name', 'organizer__username', 'coordinator__username')
    list_filter = ('status', 'is_active', 'battle_format', 'battle_type')


@admin.register(BattleFormat)
class BattleFormatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


admin.site.register(Role)
admin.site.register(Participation)
admin.site.register(Series)
admin.site.register(League)
admin.site.register(Festival)
admin.site.register(Location)
