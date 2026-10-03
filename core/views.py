from django.shortcuts import render, get_object_or_404
from .models import Product


def home(request):
    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
        .order_by("category__name", "name")
    )

    categories = {}
    featured_products = []

    for product in products:
        if product.category:
            category_name = product.category.name

            if category_name not in categories:
                categories[category_name] = product
                featured_products.append(product)

    return render(
        request,
        "core/home.html",
        {
            "products": featured_products,
        },
    )


def products(request):
    all_products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
        .order_by("name")
    )

    search_query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()

    if search_query:
        all_products = all_products.filter(
            name__icontains=search_query
        )

    if category_filter:
        all_products = all_products.filter(
            category__name=category_filter
        )

    categories = (
        Product.objects
        .filter(is_active=True, category__isnull=False)
        .values_list("category__name", flat=True)
        .distinct()
        .order_by("category__name")
    )

    return render(
        request,
        "core/products.html",
        {
            "products": all_products,
            "categories": categories,
            "search_query": search_query,
            "category_filter": category_filter,
        },
    )


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(
        request,
        "core/product_detail.html",
        {
            "product": product,
        },
    )