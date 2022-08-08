from csv import DictReader
from pathlib import Path
from django.core.management import BaseCommand

from recipes.models import Ingredient

DATA_TABLE = {
    Ingredient: "ingredients.csv",
}
DATA_DIR = Path(__file__).parent.parent.resolve()


class Command(BaseCommand):
    help = "Loads data from foodgram-project/data"

    def handle(self, *args, **options):
        for model, csv_file in DATA_TABLE.items():
            with open(
                f'/app/data/{csv_file}',
                "r",
                encoding="utf-8",
            ) as file:
                reader = DictReader(file)
                model.objects.bulk_create(model(**data) for data in reader)
        self.stdout.write(
            self.style.SUCCESS("***Data was succesfully loaded***")
        )
