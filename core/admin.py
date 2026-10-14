from django.contrib import admin
from django import forms
from django.db.models import F
from django.utils.html import format_html
from .models import Category, Product


class ProductAdminForm(forms.ModelForm):
    stock_quantity = forms.IntegerField(
        min_value=0,
        help_text="Available units. Use 0 when the product is unavailable.",
    )
    min_stock_level = forms.IntegerField(
        min_value=0,
        help_text="Show a low-stock warning at or below this quantity.",
    )

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


class StockStatusFilter(admin.SimpleListFilter):
    title = "stock status"
    parameter_name = "stock_status"

    def lookups(self, request, model_admin):
        return (
            ("available", "Available"),
            ("low", "Low stock"),
            ("unavailable", "Unavailable"),
        )

    def queryset(self, request, queryset):
        if self.value() == "available":
            return queryset.filter(stock_quantity__gt=F("min_stock_level"))
        if self.value() == "low":
            return queryset.filter(
                stock_quantity__gt=0,
                stock_quantity__lte=F("min_stock_level"),
            )
        if self.value() == "unavailable":
            return queryset.filter(stock_quantity=0)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    def image_preview(self, obj):
        if obj.image and obj.image.storage.exists(obj.image.name):
            return format_html(
                '<img src="{}" alt="{}" style="width:64px;height:64px;'
                'object-fit:contain;background:#f8fafc;border-radius:8px;" />',
                obj.image.url,
                obj.name,
            )
        return format_html(
            '<span style="display:inline-grid;width:64px;height:64px;'
            'place-items:center;background:#f1f5f9;border-radius:8px;'
            'color:#64748b;">{}</span>',
            "No photo",
        )

    image_preview.short_description = "Product image"

    @admin.display(description="Availability", ordering="stock_quantity")
    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            label, background, foreground = "Unavailable", "#fef2f2", "#b91c1c"
        elif obj.min_stock_level and obj.stock_quantity <= obj.min_stock_level:
            label, background, foreground = "Low stock", "#fff7ed", "#9a3412"
        else:
            label, background, foreground = "Available", "#ecfdf5", "#047857"
        return format_html(
            '<span style="display:inline-block;padding:4px 9px;'
            'border-radius:999px;background:{};color:{};font-weight:600;">'
            '{}</span>',
            background,
            foreground,
            label,
        )

    form = ProductAdminForm

    list_display = (
        "image_preview",
        "name",
        "category",
        "stock_status",
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
        StockStatusFilter,
        "requires_prescription",
        "is_active",
        "expiry_date",
    )

    search_fields = (
        "name",
        "item_id",
        "description",
        "category__name",
    )

    list_editable = (
        "price",
        "buying_price",
        "stock_quantity",
        "min_stock_level",
        "is_active",
    )

    ordering = ("name",)
    list_per_page = 50
    list_select_related = ("category",)
    autocomplete_fields = ("category",)
    show_full_result_count = False