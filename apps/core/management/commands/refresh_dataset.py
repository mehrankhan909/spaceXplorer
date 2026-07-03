from django.core.management.base import BaseCommand
from apps.core.services import clear_dataset_cache, load_all_datasets


class Command(BaseCommand):
    help = 'Refresh dataset cache and reload all CSV files'

    def handle(self, *args, **options):
        clear_dataset_cache()
        dataframes = load_all_datasets(force=True)
        if dataframes:
            for name, df in dataframes.items():
                self.stdout.write(f"Loaded '{name}.csv': {len(df)} rows, {len(df.columns)} columns")
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(dataframes)} dataset(s)."))
        else:
            self.stdout.write(self.style.WARNING("No CSV files found in project_dataset/."))
