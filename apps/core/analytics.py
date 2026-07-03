import pandas as pd
import numpy as np
from apps.core.services import (
    get_combined_dataframe, get_date_column,
    get_numeric_columns, get_categorical_columns, get_columns
)


def _find_column(df: pd.DataFrame, candidates: list) -> str:
    if df is None:
        return None
    for candidate in candidates:
        for col in df.columns:
            if col.lower().strip() == candidate.lower():
                return col
            if candidate.lower() in col.lower():
                return col
    return None


def _extract_country(location: str) -> str:
    if pd.isna(location):
        return 'Unknown'
    parts = str(location).split(',')
    if len(parts) >= 2:
        country = parts[-1].strip()
        if 'USA' in country or 'United States' in country:
            return 'USA'
        return country
    return str(location).strip()


def get_dashboard_stats() -> dict:
    df = get_combined_dataframe()
    if df is None:
        return {'total_missions': 0, 'successful': 0, 'failed': 0,
                'success_rate': 0, 'agencies': 0, 'launch_sites': 0,
                'rockets': 0, 'first_year': 0, 'latest_year': 0}

    stats = {'total_missions': len(df)}

    status_col = _find_column(df, ['status mission', 'status', 'mission_status'])
    if status_col:
        stats['successful'] = int((df[status_col] == 'Success').sum())
        stats['failed'] = int((df[status_col].str.contains('Fail', case=False, na=False)).sum())
        stats['success_rate'] = round(stats['successful'] / max(stats['total_missions'], 1) * 100, 1)
    else:
        stats['successful'] = 0
        stats['failed'] = 0
        stats['success_rate'] = 0

    company_col = _find_column(df, ['company name', 'company', 'agency', 'operator'])
    stats['agencies'] = int(df[company_col].nunique()) if company_col else 0

    location_col = _find_column(df, ['location', 'launch_site', 'launch site', 'site'])
    stats['launch_sites'] = int(df[location_col].nunique()) if location_col else 0

    detail_col = _find_column(df, ['detail', 'rocket', 'vehicle', 'rocket_name'])
    stats['rockets'] = int(df[detail_col].nunique()) if detail_col else 0

    date_col = get_date_column()
    if date_col:
        years = df[date_col].dropna().dt.year
        stats['first_year'] = int(years.min()) if not years.empty else 0
        stats['latest_year'] = int(years.max()) if not years.empty else 0
    else:
        stats['first_year'] = 0
        stats['latest_year'] = 0

    return stats


def get_missions_per_year() -> dict:
    df = get_combined_dataframe()
    date_col = get_date_column()
    if df is None or date_col is None:
        return {'labels': [], 'data': []}
    years = df[date_col].dropna().dt.year.astype(int)
    counts = years.value_counts().sort_index()
    return {'labels': counts.index.tolist(), 'data': counts.values.tolist()}


def get_success_rate_per_year() -> dict:
    df = get_combined_dataframe()
    date_col = get_date_column()
    status_col = _find_column(df, ['status mission', 'status', 'mission_status'])
    if df is None or date_col is None or status_col is None:
        return {'labels': [], 'data': []}
    temp = df[[date_col, status_col]].dropna()
    temp['year'] = temp[date_col].dt.year.astype(int)
    grouped = temp.groupby('year')
    rates = grouped.apply(lambda g: round((g[status_col] == 'Success').sum() / max(len(g), 1) * 100, 1))
    return {'labels': rates.index.tolist(), 'data': rates.values.tolist()}


def get_top_agencies(top_n: int = 10) -> dict:
    df = get_combined_dataframe()
    company_col = _find_column(df, ['company name', 'company', 'agency', 'operator'])
    if df is None or company_col is None:
        return {'labels': [], 'data': []}
    counts = df[company_col].value_counts().head(top_n)
    return {'labels': counts.index.tolist(), 'data': counts.values.tolist()}


def get_country_launches() -> dict:
    df = get_combined_dataframe()
    location_col = _find_column(df, ['location', 'launch_site', 'launch site'])
    if df is None or location_col is None:
        return {'labels': [], 'data': []}
    countries = df[location_col].apply(_extract_country)
    counts = countries.value_counts().head(15)
    return {'labels': counts.index.tolist(), 'data': counts.values.tolist()}


def get_rocket_usage(top_n: int = 10) -> dict:
    df = get_combined_dataframe()
    detail_col = _find_column(df, ['detail', 'rocket', 'vehicle', 'rocket_name'])
    if df is None or detail_col is None:
        return {'labels': [], 'data': []}
    rockets = df[detail_col].dropna()
    rocket_names = rockets.apply(lambda x: str(x).split('|')[0].strip() if '|' in str(x) else str(x).strip())
    counts = rocket_names.value_counts().head(top_n)
    return {'labels': counts.index.tolist(), 'data': counts.values.tolist()}


def get_monthly_launches() -> dict:
    df = get_combined_dataframe()
    date_col = get_date_column()
    if df is None or date_col is None:
        return {'labels': [], 'data': []}
    months = df[date_col].dropna().dt.month
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    counts = months.value_counts().sort_index()
    labels = [month_names[i - 1] for i in counts.index]
    return {'labels': labels, 'data': counts.values.tolist()}


def get_mission_status_distribution() -> dict:
    df = get_combined_dataframe()
    status_col = _find_column(df, ['status mission', 'status', 'mission_status'])
    if df is None or status_col is None:
        return {'labels': [], 'data': []}
    counts = df[status_col].value_counts()
    return {'labels': counts.index.tolist(), 'data': counts.values.tolist()}


def get_rocket_status_distribution() -> dict:
    df = get_combined_dataframe()
    rocket_status_col = _find_column(df, ['status rocket', 'rocket status'])
    if df is None or rocket_status_col is None:
        return {'labels': [], 'data': []}
    counts = df[rocket_status_col].value_counts()
    return {'labels': counts.index.tolist(), 'data': counts.values.tolist()}


def get_launch_frequency() -> dict:
    df = get_combined_dataframe()
    date_col = get_date_column()
    if df is None or date_col is None:
        return {'labels': [], 'data': [], 'average': 0}
    dates = df[date_col].dropna().sort_values()
    if len(dates) < 2:
        return {'labels': [], 'data': [], 'average': 0}
    yearly = dates.dt.year.astype(int).value_counts().sort_index()
    avg = yearly.mean()
    return {
        'labels': yearly.index.tolist(),
        'data': yearly.values.tolist(),
        'average': round(float(avg), 1)
    }


def get_agency_comparison() -> dict:
    df = get_combined_dataframe()
    company_col = _find_column(df, ['company name', 'company', 'agency', 'operator'])
    status_col = _find_column(df, ['status mission', 'status', 'mission_status'])
    if df is None or company_col is None or status_col is None:
        return {'labels': [], 'success_data': [], 'failure_data': []}
    top = df[company_col].value_counts().head(8).index.tolist()
    filtered = df[df[company_col].isin(top)]
    grouped = filtered.groupby(company_col)[status_col].value_counts().unstack(fill_value=0)
    success_data = []
    fail_data = []
    for agency in top:
        if agency in grouped.index:
            success_data.append(int(grouped.loc[agency].get('Success', 0)))
            fail_data.append(int(grouped.loc[agency].get('Failure', 0)))
        else:
            success_data.append(0)
            fail_data.append(0)
    return {'labels': top, 'datasets': [{'label': 'Success', 'data': success_data}, {'label': 'Failure', 'data': fail_data}]}


def generate_insights() -> list:
    df = get_combined_dataframe()
    if df is None:
        return ['No dataset loaded. Please add CSV files to the project_dataset folder.']

    insights = []
    company_col = _find_column(df, ['company name', 'company', 'agency', 'operator'])
    status_col = _find_column(df, ['status mission', 'status', 'mission_status'])
    date_col = get_date_column()
    detail_col = _find_column(df, ['detail', 'rocket', 'vehicle', 'rocket_name'])
    location_col = _find_column(df, ['location', 'launch_site', 'launch site'])

    if company_col and not df[company_col].empty:
        top_agency = df[company_col].value_counts().index[0]
        top_count = int(df[company_col].value_counts().values[0])
        insights.append(f"{top_agency} conducted the highest number of missions with {top_count} launches.")

    if status_col:
        total = len(df)
        success = int((df[status_col] == 'Success').sum())
        success_rate = round(success / max(total, 1) * 100, 1)
        insights.append(f"Overall success rate across all missions is {success_rate}%.")

    if date_col and status_col:
        temp = df[[date_col, status_col]].dropna()
        if not temp.empty:
            temp['year'] = temp[date_col].dt.year
            pre_2005 = temp[temp['year'] < 2005]
            post_2005 = temp[temp['year'] >= 2005]
            if len(pre_2005) > 0 and len(post_2005) > 0:
                rate_before = (pre_2005[status_col] == 'Success').sum() / len(pre_2005) * 100
                rate_after = (post_2005[status_col] == 'Success').sum() / len(post_2005) * 100
                if rate_after > rate_before:
                    insights.append(f"The success rate improved from {rate_before:.1f}% before 2005 to {rate_after:.1f}% after 2005.")
                else:
                    insights.append(f"The success rate changed from {rate_before:.1f}% before 2005 to {rate_after:.1f}% after 2005.")

    if date_col:
        years = df[date_col].dropna().dt.year
        if not years.empty:
            peak_year = int(years.value_counts().index[0])
            peak_count = int(years.value_counts().values[0])
            insights.append(f"The year {peak_year} had the most launches with {peak_count} missions.")

    if detail_col:
        rocket_names = df[detail_col].dropna().apply(lambda x: str(x).split('|')[0].strip() if '|' in str(x) else str(x).strip())
        if not rocket_names.empty:
            top_rocket = rocket_names.value_counts().index[0]
            top_rocket_count = int(rocket_names.value_counts().values[0])
            insights.append(f"The most used rocket is {top_rocket} with {top_rocket_count} launches.")

    if location_col:
        countries = df[location_col].apply(_extract_country)
        if not countries.empty:
            top_country = countries.value_counts().index[0]
            top_country_count = int(countries.value_counts().values[0])
            insights.append(f"{top_country} leads in total launches with {top_country_count} missions.")

    if date_col:
        years = df[date_col].dropna().dt.year
        if not years.empty:
            avg_per_year = round(len(df) / max((int(years.max()) - int(years.min()) + 1), 1), 1)
            insights.append(f"Average launches per year is approximately {avg_per_year}.")

    if company_col and date_col:
        temp = df[[company_col, date_col]].dropna()
        if not temp.empty:
            temp['year'] = temp[date_col].dt.year
            recent = temp[temp['year'] >= 2010]
            if not recent.empty:
                growth = recent[company_col].value_counts()
                if len(growth) > 0:
                    fastest = growth.index[0]
                    insights.append(f"Fastest growing agency in recent years is {fastest}.")

    if status_col and company_col:
        failures = df[df[status_col].str.contains('Fail', case=False, na=False)]
        if not failures.empty:
            fail_agency = failures[company_col].value_counts().index[0]
            insights.append(f"{fail_agency} has the most mission failures.")

    return insights


def get_statistics() -> dict:
    df = get_combined_dataframe()
    if df is None:
        return {}

    stats = {}
    numeric_cols = get_numeric_columns()
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        stats[col] = {
            'mean': round(float(series.mean()), 2),
            'median': round(float(series.median()), 2),
            'mode': float(series.mode().iloc[0]) if not series.mode().empty else None,
            'min': round(float(series.min()), 2),
            'max': round(float(series.max()), 2),
            'std': round(float(series.std()), 2),
            'variance': round(float(series.var()), 2),
            'count': int(series.count()),
            'unique': int(series.nunique()),
        }

    categorical = get_categorical_columns()
    for col in categorical:
        series = df[col].dropna()
        if series.empty:
            continue
        vc = series.value_counts()
        stats[col] = {
            'count': int(series.count()),
            'unique': int(series.nunique()),
            'top': str(vc.index[0]) if not vc.empty else '',
            'top_count': int(vc.values[0]) if not vc.empty else 0,
        }

    stats['meta'] = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': int(df.isnull().sum().sum()),
        'duplicate_rows': int(df.duplicated().sum()),
        'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
    }

    return stats


def get_data_quality() -> dict:
    df = get_combined_dataframe()
    if df is None:
        return {}

    quality = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': {},
    }

    for col in df.columns:
        col_info = {
            'dtype': str(df[col].dtype),
            'null_count': int(df[col].isnull().sum()),
            'null_percent': round(df[col].isnull().sum() / max(len(df), 1) * 100, 2),
            'unique_count': int(df[col].nunique()),
            'duplicate_count': int(df[col].duplicated().sum()),
        }

        if pd.api.types.is_numeric_dtype(df[col]):
            series = df[col].dropna()
            if not series.empty:
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                outliers = ((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum()
                col_info['outliers'] = int(outliers)
                col_info['min'] = round(float(series.min()), 2)
                col_info['max'] = round(float(series.max()), 2)

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            invalid_dates = df[col].isnull().sum()
            col_info['invalid_dates'] = int(invalid_dates)

        quality['columns'][col] = col_info

    return quality


def get_dynamic_chart_data() -> list:
    df = get_combined_dataframe()
    if df is None:
        return []

    charts = []
    date_col = get_date_column()
    status_col = _find_column(df, ['status mission', 'status', 'mission_status'])
    company_col = _find_column(df, ['company name', 'company', 'agency', 'operator'])
    location_col = _find_column(df, ['location', 'launch_site', 'launch site'])
    detail_col = _find_column(df, ['detail', 'rocket', 'vehicle', 'rocket_name'])

    if date_col:
        years = df[date_col].dropna().dt.year.astype(int)
        counts = years.value_counts().sort_index()
        charts.append({
            'id': 'missions_per_year',
            'title': 'Missions Per Year',
            'type': 'line',
            'labels': counts.index.tolist(),
            'data': counts.values.tolist(),
            'available': True,
        })

    if status_col:
        counts = df[status_col].value_counts()
        charts.append({
            'id': 'mission_status',
            'title': 'Mission Status Distribution',
            'type': 'doughnut',
            'labels': counts.index.tolist(),
            'data': counts.values.tolist(),
            'available': True,
        })

    if company_col:
        counts = df[company_col].value_counts().head(10)
        charts.append({
            'id': 'top_agencies',
            'title': 'Top 10 Agencies',
            'type': 'bar',
            'labels': counts.index.tolist(),
            'data': counts.values.tolist(),
            'available': True,
        })

    if location_col:
        countries = df[location_col].apply(_extract_country)
        counts = countries.value_counts().head(10)
        charts.append({
            'id': 'country_launches',
            'title': 'Launches by Country',
            'type': 'bar',
            'labels': counts.index.tolist(),
            'data': counts.values.tolist(),
            'available': True,
        })

    if detail_col:
        rockets = df[detail_col].dropna().apply(lambda x: str(x).split('|')[0].strip() if '|' in str(x) else str(x).strip())
        counts = rockets.value_counts().head(10)
        charts.append({
            'id': 'rocket_usage',
            'title': 'Most Used Rockets',
            'type': 'bar',
            'labels': counts.index.tolist(),
            'data': counts.values.tolist(),
            'available': True,
        })

    if date_col:
        months = df[date_col].dropna().dt.month
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        counts = months.value_counts().sort_index()
        labels = [month_names[i - 1] for i in counts.index]
        charts.append({
            'id': 'monthly_launches',
            'title': 'Monthly Launches',
            'type': 'bar',
            'labels': labels,
            'data': counts.values.tolist(),
            'available': True,
        })

    if date_col and status_col:
        temp = df[[date_col, status_col]].dropna()
        temp['year'] = temp[date_col].dt.year.astype(int)
        grouped = temp.groupby('year')
        rates = grouped.apply(lambda g: round((g[status_col] == 'Success').sum() / max(len(g), 1) * 100, 1))
        charts.append({
            'id': 'success_rate_trend',
            'title': 'Success Rate Over Time',
            'type': 'line',
            'labels': rates.index.tolist(),
            'data': rates.values.tolist(),
            'available': True,
        })

    if company_col and status_col:
        top = df[company_col].value_counts().head(6).index.tolist()
        filtered = df[df[company_col].isin(top)]
        grouped = filtered.groupby(company_col)[status_col].value_counts().unstack(fill_value=0)
        success_data = []
        fail_data = []
        for agency in top:
            if agency in grouped.index:
                success_data.append(int(grouped.loc[agency].get('Success', 0)))
                fail_data.append(int(grouped.loc[agency].get('Failure', 0)))
            else:
                success_data.append(0)
                fail_data.append(0)
        charts.append({
            'id': 'agency_comparison',
            'title': 'Agency Success vs Failure',
            'type': 'stacked_bar',
            'labels': top,
            'datasets': [
                {'label': 'Success', 'data': success_data},
                {'label': 'Failure', 'data': fail_data},
            ],
            'available': True,
        })

    return charts
