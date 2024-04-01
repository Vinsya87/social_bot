from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.cache import caches
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django.views.generic import ListView
from events.models import ElementalBattle


class BaseMixin(
        ):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class IndexView(
        BaseMixin,
        ListView):
    template_name = 'index.html'
    model = ElementalBattle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
                elemental_battles=ElementalBattle.objects.all()
                )
        return context


def paginator_page(request, page_pagi):
    # paginator = Paginator(page_pagi, settings.PER_PAGE)
    paginator = Paginator(page_pagi, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
@staff_member_required
@require_GET
def clear_cache(request):
    cache = caches['default']
    cache.clear()
    return redirect('main_url:main_index')


@login_required
@staff_member_required
@require_GET
def clear_session(request):
    cache = caches['sessions']
    cache.clear()
    return redirect('main_url:main_index')
