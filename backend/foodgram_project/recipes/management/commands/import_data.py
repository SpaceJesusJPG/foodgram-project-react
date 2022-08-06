from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredient

DATA_TABLE = {
    Ingredient: "ingredients.csv",
}


class Command(BaseCommand):
    help = "Loads data from C:/Dev/foodgram-project-react/data"

    def handle(self, *args, **options):
        for model, csv_file in DATA_TABLE.items():
            with open(
                f"C:/Dev/foodgram-project-react/data/{csv_file}",
                "r",
                encoding="utf-8",
            ) as file:
                reader = DictReader(file)
                model.objects.bulk_create(model(**data) for data in reader)
        self.stdout.write(
            self.style.SUCCESS("***Data was succesfully loaded***")
        )
