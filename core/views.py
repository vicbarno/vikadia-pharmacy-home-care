from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Category, Product


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

    category_navigation = Category.objects.filter(
        name__in=[
            "Pain Relief",
            "Prescription Medicines",
            "Vitamins & Minerals",
            "Baby Care",
            "Skin Care",
            "First Aid",
            "Medical Devices",
            "Wellness Products",
        ]
    ).order_by("name")

    return render(
        request,
        "core/home.html",
        {
            "products": featured_products,
            "category_navigation": category_navigation,
        },
    )


def products(request):
    all_products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
    )

    search_query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()
    availability_filter = request.GET.get("availability", "").strip()
    sort_by = request.GET.get("sort", "name").strip()

    if search_query:
        all_products = all_products.filter(
            Q(name__icontains=search_query)
            | Q(item_id__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    if category_filter:
        all_products = all_products.filter(
            category__name=category_filter
        )

    if availability_filter == "in_stock":
        all_products = all_products.filter(stock_quantity__gt=0)
    elif availability_filter == "out_of_stock":
        all_products = all_products.filter(stock_quantity=0)
    else:
        availability_filter = ""

    sort_options = {
        "name": ("name", "pk"),
        "price_asc": ("price", "name", "pk"),
        "price_desc": ("-price", "name", "pk"),
        "newest": ("-created_at", "-pk"),
        "availability": ("-stock_quantity", "name", "pk"),
    }
    if sort_by not in sort_options:
        sort_by = "name"
    all_products = all_products.order_by(*sort_options[sort_by])

    categories = (
        Product.objects
        .filter(is_active=True, category__isnull=False)
        .values_list("category__name", flat=True)
        .distinct()
        .order_by("category__name")
    )
    page_obj = Paginator(all_products, 24).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "core/products.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "product_count": page_obj.paginator.count,
            "categories": categories,
            "search_query": search_query,
            "category_filter": category_filter,
            "availability_filter": availability_filter,
            "sort_by": sort_by,
            "sort_options": (
                ("name", "Name: A to Z"),
                ("price_asc", "Price: low to high"),
                ("price_desc", "Price: high to low"),
                ("newest", "Newest"),
                ("availability", "Availability"),
            ),
        },
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.filter(is_active=True).select_related("category"),
        id=product_id,
    )

    return render(
        request,
        "core/product_detail.html",
        {
            "product": product,
        },
    )