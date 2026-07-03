from django.shortcuts import render
from django.http import JsonResponse
from apps.core.analytics import (
    get_missions_per_year, get_success_rate_per_year,
    get_top_agencies, get_country_launches, get_rocket_usage,
    get_monthly_launches, get_mission_status_distribution,
    get_rocket_status_distribution, get_launch_frequency,
    get_agency_comparison, generate_insights,
    get_dashboard_stats, get_dynamic_chart_data
)
from apps.core.services import search_dataframe, get_combined_dataframe, get_columns
from apps.core.analytics import _find_column


CHART_TITLES = {
    'missions_per_year': 'Missions Per Year',
    'success_rate': 'Success Rate Per Year',
    'success_rate_trend': 'Success Rate Trend',
    'top_agencies': 'Top Agencies',
    'country_launches': 'Launches by Country',
    'rocket_usage': 'Rocket Usage',
    'monthly_launches': 'Monthly Launches',
    'status_dist': 'Mission Status Distribution',
    'mission_status': 'Mission Status Distribution',
    'rocket_status': 'Rocket Status Distribution',
    'launch_frequency': 'Launch Frequency',
    'agency_comparison': 'Agency Comparison',
}


def analytics_page(request):
    return render(request, 'analytics/analytics.html')


def drilldown_page(request, chart_id):
    title = CHART_TITLES.get(chart_id, chart_id.replace('_', ' ').title())
    return render(request, 'analytics/drilldown.html', {
        'chart_id': chart_id,
        'chart_title': title,
    })


def api_all_charts(request):
    charts = get_dynamic_chart_data()
    return JsonResponse({'charts': charts})


def api_chart_data(request, chart_id):
    chart_map = {
        'missions_per_year': get_missions_per_year,
        'success_rate': get_success_rate_per_year,
        'success_rate_trend': get_success_rate_per_year,
        'top_agencies': get_top_agencies,
        'country_launches': get_country_launches,
        'rocket_usage': get_rocket_usage,
        'monthly_launches': get_monthly_launches,
        'status_dist': get_mission_status_distribution,
        'mission_status': get_mission_status_distribution,
        'rocket_status': get_rocket_status_distribution,
        'launch_frequency': get_launch_frequency,
        'agency_comparison': get_agency_comparison,
    }
    func = chart_map.get(chart_id)
    if func:
        data = func()
        return JsonResponse({'chart_id': chart_id, 'data': data})
    return JsonResponse({'error': 'Unknown chart'}, status=404)


def api_drilldown_missions(request, chart_id):
    label = request.GET.get('label', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))

    if not label:
        return JsonResponse({'rows': [], 'total': 0, 'page': 1, 'pages': 0, 'columns': []})

    df = get_combined_dataframe()
    if df is None:
        return JsonResponse({'rows': [], 'total': 0, 'page': 1, 'pages': 0, 'columns': []})

    filter_col = _resolve_filter_column(df, chart_id)
    if filter_col and filter_col in df.columns:
        if _is_date_column(df, filter_col):
            mask = df[filter_col].dt.strftime('%Y-%m-%d').str.contains(label, na=False)
        else:
            mask = df[filter_col].astype(str).str.lower().str.contains(label.lower(), na=False)
        df = df[mask]

    total = len(df)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    page_df = df.iloc[start:start + page_size]

    columns = list(df.columns)
    rows = []
    for _, row in page_df.iterrows():
        row_dict = {}
        for col in columns:
            val = row[col]
            try:
                import pandas as pd
                if pd.isna(val):
                    row_dict[col] = None
                elif hasattr(val, 'isoformat'):
                    row_dict[col] = val.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    row_dict[col] = str(val)
            except (ValueError, TypeError):
                row_dict[col] = str(val) if val is not None else None
        rows.append(row_dict)

    return JsonResponse({
        'rows': rows,
        'total': total,
        'page': page,
        'pages': total_pages,
        'page_size': page_size,
        'columns': columns,
        'filter_label': label,
    })


def _resolve_filter_column(df, chart_id):
    if chart_id in ('missions_per_year', 'success_rate', 'success_rate_trend', 'launch_frequency'):
        return _find_column(df, ['datum', 'date', 'launch_date'])
    if chart_id in ('top_agencies', 'agency_comparison'):
        return _find_column(df, ['company name', 'company', 'agency', 'operator'])
    if chart_id == 'country_launches':
        return _find_column(df, ['location', 'launch_site', 'launch site'])
    if chart_id == 'rocket_usage':
        return _find_column(df, ['detail', 'rocket', 'vehicle', 'rocket_name'])
    if chart_id == 'monthly_launches':
        return _find_column(df, ['datum', 'date', 'launch_date'])
    if chart_id in ('mission_status', 'status_dist'):
        for col in df.columns:
            cl = col.lower().strip()
            if cl == 'status mission' or cl == 'mission_status':
                return col
        return _find_column(df, ['status mission', 'mission_status'])
    if chart_id == 'rocket_status':
        for col in df.columns:
            cl = col.lower().strip()
            if cl == 'status rocket' or cl == 'rocket_status':
                return col
        return _find_column(df, ['status rocket', 'rocket_status'])
    return None


def _is_date_column(df, col):
    try:
        import pandas as pd
        return pd.api.types.is_datetime64_any_dtype(df[col])
    except Exception:
        return False
