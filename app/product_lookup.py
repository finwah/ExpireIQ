import requests


IMPORTANT_CATEGORY_KEYWORDS = {
    "eggs": "Eggs",
    "egg": "Eggs",
    "fresh-eggs": "Eggs",
    "chicken-eggs": "Eggs",

    "milk": "Dairy",
    "milks": "Dairy",
    "dairies": "Dairy",
    "cheeses": "Dairy",
    "cheese": "Dairy",
    "yogurts": "Dairy",
    "yoghurt": "Dairy",

    "fruits": "Fruit",
    "fruit": "Fruit",
    "strawberries": "Fruit",
    "strawberry": "Fruit",
    "bananas": "Fruit",
    "banana": "Fruit",
    "apples": "Fruit",
    "apple": "Fruit",
    "grapes": "Fruit",

    "vegetables": "Vegetables",
    "vegetable": "Vegetables",
    "carrots": "Vegetables",
    "carrot": "Vegetables",
    "broccoli": "Vegetables",
    "onions": "Vegetables",
    "onion": "Vegetables",
    "peppers": "Vegetables",

    "meats": "Meat",
    "meat": "Meat",
    "poultries": "Meat",
    "poultry": "Meat",
    "chicken": "Meat",
    "beef": "Meat",
    "pork": "Meat",

    "seafood": "Seafood",
    "fish": "Seafood",
    "tuna": "Seafood",
    "salmon": "Seafood",

    "breads": "Bread",
    "bread": "Bread",
    "bakery": "Bread",

    "breakfast-cereals": "Cereal",
    "cereals": "Cereal",
    "cereal": "Cereal",

    "pastas": "Pasta",
    "pasta": "Pasta",

    "rice": "Rice",

    "frozen-foods": "Frozen",
    "frozen": "Frozen",

    "ready-meals": "Ready Meals",
    "ready-meal": "Ready Meals",

    "soups": "Soup",
    "soup": "Soup",

    "sauces": "Sauces",
    "sauce": "Sauces",
    "condiments": "Condiments",

    "snacks": "Snacks",
    "sweet-snacks": "Snacks",
    "biscuits": "Snacks",
    "confectioneries": "Snacks",
    "chocolates": "Snacks",

    "beverages": "Drinks",
    "drinks": "Drinks",
    "carbonated-drinks": "Drinks",
    "sodas": "Drinks",
    "colas": "Drinks"
}


CATEGORY_PRIORITY = {
    "Eggs": 100,
    "Dairy": 95,
    "Fruit": 90,
    "Vegetables": 90,
    "Meat": 85,
    "Seafood": 85,
    "Bread": 80,
    "Cereal": 78,
    "Pasta": 76,
    "Rice": 76,
    "Frozen": 72,
    "Ready Meals": 70,
    "Soup": 68,
    "Sauces": 65,
    "Condiments": 64,
    "Snacks": 60,
    "Drinks": 50,
    "Other": 1
}


def readable_category_name(category: str):
    category = category.replace("en:", "")
    category = category.replace("-", " ")
    return category.title()


def build_full_category(category_tags):
    if not category_tags:
        return ""

    cleaned = []

    for category in category_tags:
        readable = readable_category_name(category)

        if readable and readable not in cleaned:
            cleaned.append(readable)

    return ", ".join(cleaned)


def get_clean_categories(category_tags):
    if not category_tags:
        return []

    selected = []

    for raw_category in category_tags:
        category = raw_category.replace("en:", "").strip().lower()

        for keyword, clean_name in IMPORTANT_CATEGORY_KEYWORDS.items():
            if keyword in category and clean_name not in selected:
                selected.append(clean_name)

    return selected


def build_display_category(category_tags):
    clean_categories = get_clean_categories(category_tags)

    if not clean_categories:
        return "Other"

    sorted_categories = sorted(
        clean_categories,
        key=lambda category: CATEGORY_PRIORITY.get(category, 10),
        reverse=True
    )

    return sorted_categories[0]


def lookup_product_by_barcode(barcode: str):
    barcode = barcode.strip()

    url = f"https://uk.openfoodfacts.org/api/v2/product/{barcode}"

    headers = {
        "User-Agent": "ExpireIQ/1.0 (student project)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()

    except Exception as e:
        print("Lookup error:", e)
        return None

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    category_tags = product.get("categories_tags")

    return {
        "barcode": barcode,
        "name": (
            product.get("product_name_en")
            or product.get("product_name")
            or "Unknown Product"
        ),
        "brand": product.get("brands") or "",
        "size": product.get("quantity") or "",
        "category": build_display_category(category_tags),
        "full_category": build_full_category(category_tags),
        "image_url": product.get("image_url") or ""
    }