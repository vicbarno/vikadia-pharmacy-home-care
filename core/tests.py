from decimal import Decimal
from urllib.parse import parse_qs, urlparse

from django.test import TestCase
from django.contrib import admin
from core.admin import ProductAdmin, ProductAdminForm
from core.models import Category, Product
from core.templatetags.pharmacy import (
    category_icon_name,
    has_product_image,
    product_enquiry_url,
)


class StorefrontTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Pain Relief")
        cls.product = Product.objects.create(
            category=cls.category,
            item_id="ITEM-unique",
            name="Catalog product 00",
            description="Unique catalog description",
            price=Decimal("125.00"),
            stock_quantity=5,
            requires_prescription=True,
            image="products/paracetamol.jpg",
        )
        for index in range(1, 26):
            Product.objects.create(
                category=cls.category,
                item_id=f"ITEM-{index:03}",
                name=f"Catalog product {index:02}",
                description="Everyday pharmacy product",
                price=Decimal("75.00"),
                stock_quantity=0 if index == 25 else 3,
            )
        for name in (
            "Prescription Medicines",
            "Vitamins & Minerals",
            "Baby Care",
            "Skin Care",
            "First Aid",
            "Medical Devices",
            "Wellness Products",
        ):
            Category.objects.create(name=name)

    def test_home_renders_real_catalog_shortcuts_and_photo(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "hero-pharmacy-C_73Yvld.jpg")
        self.assertContains(response, 'class="category-shortcut"', count=8)
        self.assertContains(response, "Browse products")
        self.assertContains(response, "id=\"primary-navigation\"")
        self.assertContains(response, 'src="/media/products/paracetamol.jpg"')
        self.assertContains(response, 'alt="Catalog product 00 product image"')

    def test_catalog_is_paginated_and_keeps_query_parameters(self):
        response = self.client.get(
            "/products/",
            {
                "page": 2,
                "category": "Pain Relief",
                "availability": "in_stock",
                "sort": "price_desc",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "25 results")
        self.assertContains(response, "Page 2 of 2")
        self.assertContains(response, "Catalog product 24")
        self.assertContains(response, "category=Pain%20Relief")
        self.assertContains(response, "availability=in_stock")
        self.assertContains(response, "sort=price_desc")

    def test_filters_and_sorting_can_be_combined(self):
        response = self.client.get(
            "/products/",
            {
                "q": "Pain Relief",
                "category": "Pain Relief",
                "availability": "in_stock",
                "sort": "price_desc",
            },
        )

        self.assertEqual(response.context["product_count"], 25)
        self.assertEqual(
            response.context["products"][0].name,
            "Catalog product 00",
        )

    def test_empty_results_offer_filter_reset(self):
        response = self.client.get(
            "/products/",
            {"q": "no-such-item", "availability": "out_of_stock"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No matching products")
        self.assertContains(response, "View all products")

    def test_search_matches_description_and_item_code(self):
        description_response = self.client.get(
            "/products/", {"q": "unique catalog description"}
        )
        item_code_response = self.client.get(
            "/products/", {"q": "ITEM-unique"}
        )

        self.assertContains(description_response, "Catalog product 00")
        self.assertContains(item_code_response, "Catalog product 00")
        self.assertNotContains(description_response, "Catalog product 01")

    def test_prescription_product_offers_pharmacist_contact_not_direct_order(self):
        response = self.client.get(f"/product/{self.product.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ask pharmacist about prescription")
        self.assertContains(response, "requires a prescription")
        self.assertNotContains(response, "Requested quantity:")
        self.assertContains(response, "This is an enquiry only")

    def test_product_enquiry_url_encodes_product_and_requested_quantity(self):
        product = Product.objects.create(
            category=self.category,
            name="Care & Comfort 500mg",
            description="Test formulation",
            price=Decimal("24.50"),
            stock_quantity=4,
        )

        url = product_enquiry_url(product, quantity=2)
        message = parse_qs(urlparse(url).query)["text"][0]

        self.assertIn("Care & Comfort 500mg", message)
        self.assertIn("Requested quantity: 2", message)
        self.assertIn("Call: +254708282765", message)
        self.assertIn("not a confirmed order", message)

    def test_image_fallback_and_category_icons_are_consistent(self):
        missing_photo = Product.objects.create(
            category=self.category,
            item_id="ITEM-no-photo",
            name="Missing photo item",
            description="Test product without a saved photo",
            price=Decimal("10.00"),
            stock_quantity=2,
            image="products/no-such-test-image.jpg",
        )

        self.assertTrue(has_product_image(self.product))
        self.assertFalse(has_product_image(missing_photo))
        self.assertEqual(category_icon_name(self.category), "pill")

        response = self.client.get(
            "/products/",
            {"q": "Missing photo item"},
        )
        self.assertContains(response, "No product photo available")
        self.assertContains(response, "#icon-pill")
        self.assertNotContains(response, missing_photo.image.name)

    def test_product_detail_uses_category_icon_for_missing_photo(self):
        product = Product.objects.create(
            category=self.category,
            name="Missing detail image",
            description="No image assigned on disk",
            price=Decimal("10.00"),
            stock_quantity=0,
            image="products/no-such-detail-test-image.jpg",
        )

        response = self.client.get(f"/product/{product.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No product photo available")
        self.assertContains(response, "#icon-pill")
        self.assertContains(response, "Out of stock")
        self.assertContains(response, "Check availability")
        self.assertNotContains(response, "requested-quantity")

    def test_admin_stock_badges_distinguish_unavailable_low_and_available(self):
        product_admin = ProductAdmin(Product, admin.site)
        self.product.stock_quantity = 0
        self.assertIn("Unavailable", product_admin.stock_status(self.product))
        self.product.stock_quantity = 2
        self.product.min_stock_level = 2
        self.assertIn("Low stock", product_admin.stock_status(self.product))
        self.product.stock_quantity = 3
        self.assertIn("Available", product_admin.stock_status(self.product))

    def test_inactive_products_are_not_visible_on_detail_routes(self):
        self.product.is_active = False
        self.product.save(update_fields=["is_active"])

        response = self.client.get(f"/product/{self.product.pk}/")

        self.assertEqual(response.status_code, 404)

    def test_stock_admin_form_rejects_negative_inventory(self):
        form = ProductAdminForm(
            data={
                "category": self.category.pk,
                "item_id": "ITEM-invalid",
                "name": "Invalid stock product",
                "description": "",
                "price": "25.00",
                "buying_price": "",
                "stock_quantity": "-1",
                "min_stock_level": "0",
                "expiry_date": "",
                "requires_prescription": "",
                "is_active": "on",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("stock_quantity", form.errors)
