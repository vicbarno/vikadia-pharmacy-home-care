from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Category, Product


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "style": "width: 100%;"
                }
            ),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px; height:80px; object-fit:contain;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Image"

    form = ProductAdminForm

    list_display = (
        "image_preview",
        "name",
        "category",
        "description",
        "price",
        "buying_price",
        "stock_quantity",
        "min_stock_level",
        "expiry_date",
        "requires_prescription",
        "is_active",
    )

    list_filter = (
        "category",
        "requires_prescription",
        "is_active",
    )

    search_fields = (
        "name",
        "item_id",
        "description",
    )

    list_editable = (
        "description",
        "price",
        "buying_price",
        "stock_quantity",
        "min_stock_level",
        "is_active",
    )

    ordering = ("name",)