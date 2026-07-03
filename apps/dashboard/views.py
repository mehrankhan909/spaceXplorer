import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.core.services import get_combined_dataframe, scan_csv_files, get_filter_options, get_metadata, get_search_suggestions, search_dataframe
from apps.core.analytics import (
    get_dashboard_stats, get_missions_per_year,
    get_success_rate_per_year, get_top_agencies,
    get_mission_status_distribution, get_rocket_usage,
    generate_insights, get_dynamic_chart_data
)
from .models import Bookmark


def home(request):
    return render(request, 'dashboard/home.html')


def api_dashboard_stats(request):
    stats = get_dashboard_stats()
    return JsonResponse(stats)


def api_dashboard_charts(request):
    charts = get_dynamic_chart_data()
    return JsonResponse({'charts': charts})


def api_insights(request):
    insights = generate_insights()
    return JsonResponse({'insights': insights})


def api_search(request):
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


def api_search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = get_search_suggestions(query)
    return JsonResponse({'suggestions': suggestions})


def api_filter_options(request):
    options = get_filter_options()
    return JsonResponse({'options': options})


def api_metadata(request):
    meta = get_metadata()
    return JsonResponse({'metadata': meta})


def bookmarks(request):
    bookmarks_list = Bookmark.objects.all()
    return render(request, 'dashboard/bookmarks.html', {'bookmarks': bookmarks_list})


@require_POST
def add_bookmark(request):
    mission_name = request.POST.get('mission_name', '')
    mission_data = request.POST.get('mission_data', '{}')
    try:
        data = json.loads(mission_data)
    except json.JSONDecodeError:
        data = {}
    Bookmark.objects.create(mission_name=mission_name, mission_data=data)
    return JsonResponse({'status': 'ok'})


@require_POST
def remove_bookmark(request, pk):
    try:
        Bookmark.objects.get(pk=pk).delete()
        return JsonResponse({'status': 'ok'})
    except Bookmark.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
