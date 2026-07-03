def dataset_context(request):
    from apps.core.services import scan_csv_files, get_combined_dataframe
    csv_files = scan_csv_files()
    df = get_combined_dataframe()
    return {
        'dataset_files': [f.name for f in csv_files],
        'dataset_loaded': df is not None,
        'dataset_rows': len(df) if df is not None else 0,
    }
