import json
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.core.services import (
    get_combined_dataframe, get_filter_options, get_columns,
    search_dataframe, get_mission_detail, get_metadata
)
from .models import FavoriteMission


def mission_list(request):
    return render(request, 'missions/list.html', {
        'columns': get_columns(),
    })


def api_missions(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))
    sort_col = request.GET.get('sort', '')
    sort_dir = request.GET.get('dir', 'asc')

    filters = {}
    for key in request.GET:
        if key.startswith('filter_') and request.GET[key]:
            col_name = key[7:]
            filters[col_name] = request.GET[key]

    result = search_dataframe(
        query=query, page=page, page_size=page_size,
        sort_col=sort_col, sort_dir=sort_dir, filters=filters
    )
    return JsonResponse(result)


def api_mission_detail(request, mission_id):
    mission = get_mission_detail(mission_id)
    if mission is None:
        return JsonResponse({'error': 'Mission not found'}, status=404)
    return JsonResponse({'mission': mission, 'mission_id': mission_id})


def mission_detail_page(request, mission_id):
    return render(request, 'missions/detail.html', {
        'mission_id': mission_id,
        'columns': get_columns(),
    })


@require_POST
def add_favorite(request):
    mission_name = request.POST.get('mission_name', '')
    mission_data = request.POST.get('mission_data', '{}')
    try:
        data = json.loads(mission_data)
    except json.JSONDecodeError:
        data = {}
    FavoriteMission.objects.create(mission_name=mission_name, mission_data=data)
    return JsonResponse({'status': 'ok'})


@require_POST
def remove_favorite(request, pk):
    try:
        FavoriteMission.objects.get(pk=pk).delete()
        return JsonResponse({'status': 'ok'})
    except FavoriteMission.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
