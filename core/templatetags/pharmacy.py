from urllib.parse import urlencode

from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()


CATEGORY_ICONS = {
    "pain relief": "pill",
    "analgesic injection": "pill",
    "analgesic syrup": "pill",
    "tablets analgesic": "pill",
    "antibiotics": "pill",
    "antacids": "pill",
    "anti amoeba": "pill",
    "antihistamines": "pill",
    "antitussives": "pill",
    "antifungals": "pill",
    "anti hypertensives": "heart-pulse",
    "dm drugs": "droplet",
    "diabetes care": "droplet",
    "vitamins & minerals": "leaf",
    "appetite & vitamins": "leaf",
    "search": "search",
    "baby care": "baby",
    "skin care": "droplet",
    "creams & topicals": "droplet",
    "first aid": "first-aid",
    "supplies & consumables": "first-aid",
    "medical devices": "stethoscope",
    "diagnostic gadgets": "heart-pulse",
    "prescription medicines": "prescription",
    "injectables": "prescription",
    "home care": "home-care",
    "home based care": "home-care",
    "wellness products": "wellness",
    "customer support": "message",
    "delivery": "truck",
    "opening hours": "clock",
    "blood pressure monitoring": "heart-pulse",
    "blood pressure": "heart-pulse",
    "blood sugar": "droplet",
    "bmi": "wellness",
    "weight monitoring": "heart-pulse",
    "medication review": "prescription",
    "vaccinations": "prescription",
    "telephone": "phone",
    "location": "map-pin",
    "cart": "shopping-bag",
}


@register.filter
def category_icon_name(category):
    if hasattr(category, "name"):
        category = category.name
    normalized = " ".join(str(category or "").split()).casefold()
    return CATEGORY_ICONS.get(normalized, "package")


@register.filter
def has_product_image(product):
    if not product.image or not product.image.name:
        return False
    return product.image.storage.exists(product.image.name)


def _whatsapp_number():
    number = "".join(
        character
        for character in str(settings.PHARMACY_WHATSAPP_NUMBER)
        if character.isdigit()
    )
    if not number:
        raise ValueError("PHARMACY_WHATSAPP_NUMBER must contain digits.")
    return number


@register.simple_tag
def pharmacy_whatsapp_url():
    return f"https://wa.me/{_whatsapp_number()}"


@register.simple_tag
def pharmacy_phone_number():
    number = "".join(
        character
        for character in str(settings.PHARMACY_PHONE_NUMBER)
        if character.isdigit()
    )
    if not number:
        raise ValueError("PHARMACY_PHONE_NUMBER must contain digits.")
    return number


@register.simple_tag
def pharmacy_phone_display():
    number = pharmacy_phone_number()
    if number.startswith("254") and len(number) == 12:
        return f"+254 {number[3:6]} {number[6:9]} {number[9:]}"
    return f"+{number}"


@register.simple_tag
def product_enquiry_message(product):
    message = [
        "Hello Vikadia Pharmacy and Home Care,",
        f"I would like to enquire about {product.name}.",
        f"Listed price: KSh {product.price:.2f}.",
        f"Availability shown on the website: "
        f"{'in stock' if product.stock_quantity > 0 else 'out of stock'}.",
    ]
    if product.requires_prescription:
        message.append(
            "This product is marked as prescription-required. "
            "Please advise on the prescription review process."
        )
    message.extend(
        [
            "Please confirm current availability and next steps. "
            "This is an enquiry only, not a confirmed order.",
            "Call: +"
            + "".join(
                character
                for character in str(settings.PHARMACY_PHONE_NUMBER)
                if character.isdigit()
            ),
        ]
    )
    return "\n".join(message)


@register.simple_tag
def product_enquiry_url(product, quantity=1):
    message = product_enquiry_message(product)
    if not product.requires_prescription and product.stock_quantity > 0:
        message += f"\nRequested quantity: {quantity}."
    return format_html(
        "https://wa.me/{}?{}",
        _whatsapp_number(),
        urlencode({"text": message}),
    )


@register.simple_tag
def category_icon(category, extra_class=""):
    icon_name = category_icon_name(category)
    return format_html(
        '<svg class="{}" aria-hidden="true" focusable="false">'
        '<use href="#icon-{}"></use></svg>',
        extra_class,
        icon_name,
    )
