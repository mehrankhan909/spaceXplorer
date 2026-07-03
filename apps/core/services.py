import os
import pandas as pd
import numpy as np
from pathlib import Path
from django.conf import settings
from django.core.cache import cache
from typing import Optional


_CACHE_KEY_DATASET = 'ds_combined_v2'
_CACHE_KEY_DATAFRAMES = 'ds_all_v2'
_CACHE_KEY_METADATA = 'ds_meta_v2'


def get_dataset_path() -> Path:
    return getattr(settings, 'DATASET_DIR', settings.BASE_DIR / 'project_dataset')


def scan_csv_files() -> list:
    dataset_path = get_dataset_path()
    if not dataset_path.exists():
        return []
    return sorted(dataset_path.glob('*.csv'))


def load_csv_file(filepath: Path) -> Optional[pd.DataFrame]:
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc)
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    try:
        return pd.read_csv(filepath)
    except Exception:
        return None


def load_all_datasets(force: bool = False) -> dict:
    if not force:
        cached = cache.get(_CACHE_KEY_DATAFRAMES)
        if cached:
            return cached

    csv_files = scan_csv_files()
    dataframes = {}
    for filepath in csv_files:
        df = load_csv_file(filepath)
        if df is not None and not df.empty:
            dataframes[filepath.stem] = df

    cache.set(_CACHE_KEY_DATAFRAMES, dataframes, 600)
    return dataframes


def get_combined_dataframe(force: bool = False) -> Optional[pd.DataFrame]:
    if not force:
        cached = cache.get(_CACHE_KEY_DATASET)
        if cached is not None:
            return cached

    dataframes = load_all_datasets(force=force)
    if not dataframes:
        return None

    if len(dataframes) == 1:
        df = list(dataframes.values())[0]
    else:
        frames = list(dataframes.values())
        df = pd.concat(frames, ignore_index=True)

    df = clean_dataframe(df)
    cache.set(_CACHE_KEY_DATASET, df, 600)
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    unnamed_cols = [c for c in df.columns if c.startswith('Unnamed')]
    for col in unnamed_cols:
        df.drop(columns=[col], inplace=True, errors='ignore')

    df.columns = [c.strip() for c in df.columns]

    for col in df.columns:
        if 'date' in col.lower() or 'datum' in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip() if df[col].notna().any() else df[col]

    return df


def clear_dataset_cache():
    for key in [_CACHE_KEY_DATASET, _CACHE_KEY_DATAFRAMES, _CACHE_KEY_METADATA]:
        cache.delete(key)


def get_columns() -> list:
    df = get_combined_dataframe()
    if df is None:
        return []
    return list(df.columns)


def get_date_column() -> Optional[str]:
    df = get_combined_dataframe()
    if df is None:
        return None
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    return None


def get_numeric_columns() -> list:
    df = get_combined_dataframe()
    if df is None:
        return []
    return list(df.select_dtypes(include=[np.number]).columns)


def get_categorical_columns() -> list:
    df = get_combined_dataframe()
    if df is None:
        return []
    numeric = set(get_numeric_columns())
    date_col = get_date_column()
    return [c for c in df.columns if c not in numeric and c != date_col]


def get_filter_options(max_unique: int = 200) -> dict:
    df = get_combined_dataframe()
    if df is None:
        return {}
    options = {}
    categorical = get_categorical_columns()
    for col in categorical:
        vals = df[col].dropna().unique()
        if len(vals) <= max_unique:
            options[col] = sorted([str(v) for v in vals])
    date_col = get_date_column()
    if date_col and date_col in df.columns:
        years = df[date_col].dropna().dt.year
        if not years.empty:
            options['_year_range'] = [int(years.min()), int(years.max())]
    return options


def get_metadata(force: bool = False) -> dict:
    if not force:
        cached = cache.get(_CACHE_KEY_METADATA)
        if cached:
            return cached

    df = get_combined_dataframe()
    if df is None:
        return {}

    meta = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': [],
        'categorical_columns': get_categorical_columns(),
        'numeric_columns': get_numeric_columns(),
        'date_column': get_date_column(),
        'filter_options': get_filter_options(),
    }

    for col in df.columns:
        col_info = {
            'name': col,
            'dtype': str(df[col].dtype),
            'null_count': int(df[col].isnull().sum()),
            'null_percent': round(df[col].isnull().sum() / max(len(df), 1) * 100, 2),
            'unique_count': int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info['type'] = 'numeric'
            series = df[col].dropna()
            if not series.empty:
                col_info['min'] = round(float(series.min()), 2)
                col_info['max'] = round(float(series.max()), 2)
                col_info['mean'] = round(float(series.mean()), 2)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_info['type'] = 'date'
            series = df[col].dropna()
            if not series.empty:
                col_info['min'] = str(series.min().date())
                col_info['max'] = str(series.max().date())
        else:
            col_info['type'] = 'categorical'
            vals = df[col].dropna().unique()
            col_info['sample_values'] = [str(v) for v in vals[:10]]

        meta['columns'].append(col_info)

    cache.set(_CACHE_KEY_METADATA, meta, 600)
    return meta


def search_dataframe(query: str = '', page: int = 1, page_size: int = 25,
                     sort_col: str = '', sort_dir: str = 'asc',
                     filters: dict = None) -> dict:
    df = get_combined_dataframe()
    if df is None:
        return {'rows': [], 'total': 0, 'page': 1, 'pages': 0, 'columns': []}

    total_unfiltered = len(df)

    if filters:
        for col_name, value in filters.items():
            if not value or value == '' or value is None:
                continue
            if col_name == '_year_range':
                continue
            if col_name in df.columns:
                if isinstance(value, list):
                    mask = df[col_name].astype(str).isin([str(v) for v in value])
                    df = df[mask]
                else:
                    df = df[df[col_name].astype(str).str.lower() == str(value).lower()]

    if query and query.strip():
        query_lower = query.strip().lower()
        mask = pd.Series([False] * len(df), index=df.index)
        for col in df.columns:
            if df[col].dtype == object:
                mask = mask | df[col].str.lower().str.contains(query_lower, na=False)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                mask = mask | df[col].dt.strftime('%Y-%m-%d').str.lower().str.contains(query_lower, na=False)
            else:
                mask = mask | df[col].astype(str).str.lower().str.contains(query_lower, na=False)
        df = df[mask]

    total = len(df)

    if sort_col and sort_col in df.columns:
        ascending = sort_dir == 'asc'
        df = df.sort_values(by=sort_col, ascending=ascending, key=lambda x: x.str.lower() if x.dtype == object else x)

    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    columns = list(df.columns)
    rows = []
    for idx, row in page_df.iterrows():
        row_dict = {}
        for col in columns:
            val = row[col]
            if hasattr(val, 'isoformat'):
                row_dict[col] = val.strftime('%Y-%m-%d %H:%M:%S')
            elif pd.isna(val) if hasattr(val, '__class__') and 'NaT' in str(type(val)) else (val != val if isinstance(val, float) else False):
                row_dict[col] = None
            else:
                row_dict[col] = val
        rows.append(row_dict)

    return {
        'rows': rows,
        'total': total,
        'total_unfiltered': total_unfiltered,
        'page': page,
        'pages': total_pages,
        'page_size': page_size,
        'columns': columns,
    }


def get_mission_detail(mission_id: int) -> Optional[dict]:
    df = get_combined_dataframe()
    if df is None or mission_id < 0 or mission_id >= len(df):
        return None

    row = df.iloc[mission_id]
    columns = list(df.columns)
    mission = {}
    for col in columns:
        val = row[col]
        if hasattr(val, 'isoformat'):
            mission[col] = val.strftime('%Y-%m-%d %H:%M:%S')
        elif pd.isna(val) if hasattr(val, '__class__') and 'NaT' in str(type(val)) else (val != val if isinstance(val, float) else False):
            mission[col] = 'N/A'
        else:
            mission[col] = str(val) if val is not None else 'N/A'

    return mission


def get_search_suggestions(query: str, limit: int = 10) -> list:
    if not query or len(query) < 2:
        return []

    df = get_combined_dataframe()
    if df is None:
        return []

    query_lower = query.strip().lower()
    suggestions = set()

    categorical = get_categorical_columns()
    for col in categorical[:5]:
        vals = df[col].dropna().unique()
        for v in vals:
            if query_lower in str(v).lower():
                suggestions.add(str(v))
                if len(suggestions) >= limit:
                    return list(suggestions)[:limit]

    return list(suggestions)[:limit]
