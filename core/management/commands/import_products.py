import openpyxl

from django.core.management.base import BaseCommand
from core.models import Category, Product


class Command(BaseCommand):
    help = "Import products from the Product Catalog Excel sheet"

    def add_arguments(self, parser):
        parser.add_argument("file_path")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        workbook = openpyxl.load_workbook(
            file_path,
            data_only=True
        )

        sheet = workbook["Product Catalog"]

        imported = 0
        skipped = 0

        for row in sheet.iter_rows(min_row=2, values_only=True):

            product_name = row[0]
            category_name = row[1]
            description = row[2]
            price = row[3]
            stock_quantity = row[4]
            prescription_requirement = row[5]

            if not product_name:
                skipped += 1
                continue

            # Create or find the category
            category = None

            if category_name:
                category, created = Category.objects.get_or_create(
                    name=str(category_name).strip()
                )

            # Convert prescription requirement to True/False
            prescription_text = str(
                prescription_requirement or ""
            ).strip().lower()

            requires_prescription = prescription_text in [
                "yes",
                "required",
                "prescription required",
                "true",
            ]

            # Update existing product or create a new one
            Product.objects.update_or_create(
                name=str(product_name).strip(),
                defaults={
                    "category": category,
                    "description": str(description or "").strip(),
                    "price": price or 0,
                    "stock_quantity": int(stock_quantity or 0),
                    "requires_prescription": requires_prescription,
                    "is_active": True,
                },
            )

            imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {imported} products processed, "
                f"{skipped} rows skipped."
            )
        )