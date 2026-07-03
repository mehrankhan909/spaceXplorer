import json
import pandas as pd
from io import BytesIO
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.core.services import get_combined_dataframe, get_columns, get_metadata
from apps.core.analytics import get_statistics, get_data_quality, generate_insights


def reports_page(request):
    return render(request, 'reports/reports.html', {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })


def statistics_page(request):
    return render(request, 'reports/statistics.html')


def data_quality_page(request):
    return render(request, 'reports/data_quality.html')


def api_report_summary(request):
    df = get_combined_dataframe()
    return JsonResponse({
        'columns': get_columns(),
        'total_rows': len(df) if df is not None else 0,
        'insights': generate_insights(),
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })


def api_statistics(request):
    stats = get_statistics()
    return JsonResponse({'stats': stats})


def api_data_quality(request):
    quality = get_data_quality()
    return JsonResponse({'quality': quality})


def export_csv(request):
    df = get_combined_dataframe()
    if df is None:
        return HttpResponse('No data available', status=404)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="space_missions_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    df.to_csv(response, index=False)
    return response


def export_excel(request):
    df = get_combined_dataframe()
    if df is None:
        return HttpResponse('No data available', status=404)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Missions')
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="space_missions_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    return response
