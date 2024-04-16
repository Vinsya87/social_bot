from django.contrib import admin
from django.db.models import Q
from events.models import (BattleFormat, BattleType, ElementalBattle, Event,
                           Festival, League, Participation, Role, Series)


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'get_city_name',
        'organizer',
        'coordinator',
        'start_date',
        'status')
    search_fields = (
        'name',
        'organizer__username',
        'coordinator__username')
    inlines = [ParticipationInline]

    def get_city_name(self, obj):
        return obj.city.name if obj.city else None
    get_city_name.short_description = 'City'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='coordinator').exists():
            coordinator = request.user.coordinator_profile
            return qs.filter(
                Q(city=coordinator.city) |
                Q(city__in=coordinator.cities.all()))
        return qs


@admin.register(BattleType)
class BattleTypeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'event_type', 'can_be_series',
        'can_be_league', 'can_be_festival')
    list_filter = (
        'can_be_series',
        'can_be_league',
        'can_be_festival')


@admin.register(ElementalBattle)
class ElementalBattleAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'start_date',
        'start_time', 'end_time',
        'country', 'city', 'address',
        'organizer', 'coordinator',
        'status', 'is_active',
        'battle_format', 'battle_type')
    search_fields = (
        'name', 'organizer__username', 'coordinator__username')
    list_filter = ('status', 'is_active', 'battle_format', 'battle_type')


@admin.register(BattleFormat)
class BattleFormatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


admin.site.register(Role)
admin.site.register(Participation)
admin.site.register(Series)
admin.site.register(League)
admin.site.register(Festival)
