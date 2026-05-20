from .expiry_service import expiry_status

#Maps different product names into standardised ingredient categories for recipe matching purposes
INGREDIENT_ALIASES = {
    "egg": [
        "egg",
        "eggs",
        "large eggs",
        "free range eggs",
        "chicken eggs"
    ],
    "milk": [
        "milk",
        "whole milk",
        "semi skimmed milk",
        "semi-skimmed milk",
        "skimmed milk",
        "dairy milk"
    ],
    "cheese": [
        "cheese",
        "cheddar",
        "mozzarella",
        "parmesan",
        "red leicester"
    ],
    "butter": [
        "butter",
        "spread"
    ],
    "bread": [
        "bread",
        "loaf",
        "toast",
        "rolls",
        "baguette"
    ],
    "pasta": [
        "pasta",
        "spaghetti",
        "penne",
        "fusilli",
        "macaroni"
    ],
    "rice": [
        "rice",
        "basmati",
        "jasmine rice",
        "long grain"
    ],
    "noodle": [
        "noodle",
        "noodles"
    ],
    "tomato": [
        "tomato",
        "tomatoes",
        "passata"
    ],
    "sauce": [
        "sauce",
        "pasta sauce",
        "tomato sauce",
        "stir fry sauce"
    ],
    "vegetable": [
        "vegetable",
        "vegetables",
        "carrot",
        "carrots",
        "pepper",
        "peppers",
        "broccoli",
        "onion",
        "onions",
        "lettuce",
        "spinach",
        "sweetcorn",
        "peas"
    ],
    "fruit": [
        "fruit",
        "banana",
        "bananas",
        "apple",
        "apples",
        "berries",
        "strawberry",
        "strawberries",
        "grapes"
    ],
    "yogurt": [
        "yogurt",
        "yoghurt",
        "greek yogurt",
        "greek yoghurt"
    ],
    "cereal": [
        "cereal",
        "cornflakes",
        "weetabix",
        "granola"
    ],
    "oats": [
        "oats",
        "porridge"
    ],
    "beans": [
        "beans",
        "baked beans"
    ],
    "soup": [
        "soup",
        "tomato soup",
        "vegetable soup"
    ],
    "chicken": [
        "chicken",
        "chicken breast",
        "chicken thighs",
        "roast chicken"
    ],
    "ham": [
        "ham",
        "wafer thin ham"
    ],
    "tuna": [
        "tuna"
    ],
    "potato": [
        "potato",
        "potatoes",
        "jacket potato"
    ],
    "wrap": [
        "wrap",
        "wraps",
        "tortilla"
    ],
    "stock": [
        "stock",
        "stock cube"
    ],
    "honey": [
        "honey"
    ]
}

#Rule-based recipe list. Recipes are matched based on the presence of required and optional ingredients, with priority given to those using items expiring soon.
RECIPE_LIBRARY = [
    {
        "title": "Cheese Omelette",
        "required": ["egg"],
        "optional": ["cheese", "milk", "butter"],
        "time": "10 mins",
        "difficulty": "Easy",
        "description": "A quick meal using eggs and dairy products.",
    },
    {
        "title": "Scrambled Eggs on Toast",
        "required": ["egg", "bread"],
        "optional": ["milk", "butter", "cheese"],
        "time": "10 mins",
        "difficulty": "Easy",
        "description": "A simple breakfast or snack using eggs and bread.",
    },
    {
        "title": "Pasta with Tomato Sauce",
        "required": ["pasta"],
        "optional": ["tomato", "sauce", "cheese", "vegetable"],
        "time": "20 mins",
        "difficulty": "Easy",
        "description": "A simple pasta dish using cupboard and fridge items.",
    },
    {
        "title": "Vegetable Stir Fry",
        "required": ["vegetable"],
        "optional": ["rice", "noodle", "sauce", "chicken"],
        "time": "15 mins",
        "difficulty": "Easy",
        "description": "A flexible meal for using vegetables before they expire.",
    },
    {
        "title": "Chicken Rice Bowl",
        "required": ["chicken", "rice"],
        "optional": ["vegetable", "sauce"],
        "time": "25 mins",
        "difficulty": "Medium",
        "description": "A filling rice bowl using protein, rice, and vegetables.",
    },
    {
        "title": "Cheese Toastie",
        "required": ["bread", "cheese"],
        "optional": ["ham", "chicken", "butter"],
        "time": "10 mins",
        "difficulty": "Easy",
        "description": "A fast way to use bread and cheese.",
    },
    {
        "title": "Fruit Yogurt Bowl",
        "required": ["fruit", "yogurt"],
        "optional": ["cereal", "oats", "honey"],
        "time": "5 mins",
        "difficulty": "Easy",
        "description": "A quick breakfast or snack using fruit and yogurt.",
    },
    {
        "title": "Cereal Breakfast Bowl",
        "required": ["cereal", "milk"],
        "optional": ["fruit", "yogurt"],
        "time": "5 mins",
        "difficulty": "Easy",
        "description": "A simple breakfast using cereal and milk.",
    },
    {
        "title": "Beans on Toast",
        "required": ["beans", "bread"],
        "optional": ["cheese", "butter"],
        "time": "10 mins",
        "difficulty": "Easy",
        "description": "A simple hot meal using bread and beans.",
    },
    {
        "title": "Soup and Bread",
        "required": ["soup"],
        "optional": ["bread", "cheese", "butter"],
        "time": "10 mins",
        "difficulty": "Easy",
        "description": "A quick meal using soup with bread or toppings.",
    },
    {
        "title": "Ham and Cheese Sandwich",
        "required": ["bread"],
        "optional": ["ham", "cheese", "lettuce", "butter"],
        "time": "5 mins",
        "difficulty": "Easy",
        "description": "A simple cold meal using bread and fridge fillings.",
    },
    {
        "title": "Egg Fried Rice",
        "required": ["egg", "rice"],
        "optional": ["vegetable", "chicken", "sauce"],
        "time": "15 mins",
        "difficulty": "Medium",
        "description": "A good way to use rice, eggs, and leftover vegetables.",
    },
    {
        "title": "Chicken Pasta",
        "required": ["chicken", "pasta"],
        "optional": ["cheese", "sauce", "vegetable"],
        "time": "25 mins",
        "difficulty": "Medium",
        "description": "A filling meal using chicken and pasta.",
    },
    {
        "title": "Vegetable Pasta",
        "required": ["pasta", "vegetable"],
        "optional": ["cheese", "sauce"],
        "time": "20 mins",
        "difficulty": "Easy",
        "description": "A simple vegetarian meal using pasta and vegetables.",
    },
    {
        "title": "Loaded Jacket Potato",
        "required": ["potato"],
        "optional": ["cheese", "beans", "tuna", "butter"],
        "time": "45 mins",
        "difficulty": "Easy",
        "description": "A filling meal using potatoes and available toppings.",
    },
    {
        "title": "Tuna Pasta",
        "required": ["tuna", "pasta"],
        "optional": ["sweetcorn", "cheese", "sauce"],
        "time": "20 mins",
        "difficulty": "Easy",
        "description": "A quick cupboard-based pasta meal.",
    },
    {
        "title": "Breakfast Smoothie",
        "required": ["fruit", "milk"],
        "optional": ["yogurt", "oats", "banana"],
        "time": "5 mins",
        "difficulty": "Easy",
        "description": "A quick drink using fruit and dairy.",
    },
    {
        "title": "Cheesy Rice Bake",
        "required": ["rice", "cheese"],
        "optional": ["vegetable", "chicken", "sauce"],
        "time": "30 mins",
        "difficulty": "Medium",
        "description": "A warm meal using rice and cheese.",
    },
    {
        "title": "Chicken Wrap",
        "required": ["chicken"],
        "optional": ["wrap", "bread", "lettuce", "sauce", "cheese"],
        "time": "15 mins",
        "difficulty": "Easy",
        "description": "A quick wrap or sandwich-style meal using chicken.",
    },
    {
        "title": "Vegetable Soup",
        "required": ["vegetable"],
        "optional": ["stock", "bread", "potato"],
        "time": "30 mins",
        "difficulty": "Medium",
        "description": "A useful way to use vegetables before they expire.",
    },
]


def normalise_text(text):
    text = text.lower()

    for character in [",", ".", ":", ";", "(", ")", "[", "]", "{", "}", "-", "_", "/"]:
        text = text.replace(character, " ")

    return " ".join(text.split())


def alias_matches(alias, product_text):
    alias = normalise_text(alias)
    product_text = normalise_text(product_text)

    alias_words = alias.split()
    product_words = product_text.split()

    if len(alias_words) == 1:
        return alias in product_words

    return alias in product_text


def detect_ingredients(product_text):
    detected = set()

    for canonical_ingredient, aliases in INGREDIENT_ALIASES.items():
        for alias in aliases:
            if alias_matches(alias, product_text):
                detected.add(canonical_ingredient)
                break

    return detected

#Generates recipe suggestions by comparing detected ingredients from the user's inventory against a rule-based recipe library.
def build_recipe_suggestions(items):
    available_ingredients = set()
    expiring_ingredients = set()

    for item in items:
        product_text = " ".join([
            item.product.name or "",
            item.product.brand or "",
            item.product.category or "",
            item.product.size or ""
        ])

        detected = detect_ingredients(product_text)
        available_ingredients.update(detected)

        if expiry_status(item.expiration_date) in ["expired", "urgent", "soon"]:
            expiring_ingredients.update(detected)

    suggestions = []

    for recipe in RECIPE_LIBRARY:
        required = set(recipe["required"])
        optional = set(recipe["optional"])

        matched_required = sorted(required.intersection(available_ingredients))
        matched_optional = sorted(optional.intersection(available_ingredients))

        missing_required = sorted(required.difference(available_ingredients))
        missing_optional = sorted(optional.difference(available_ingredients))

        required_score = len(matched_required) / len(required)
        optional_score = len(matched_optional) / max(len(optional), 1)

        match_score = int((required_score * 75) + (optional_score * 25))

        expiry_priority = bool(
            (required.union(optional)).intersection(expiring_ingredients)
        )

        if matched_required:
            suggestions.append({
                "title": recipe["title"],
                "description": recipe["description"],
                "time": recipe["time"],
                "difficulty": recipe["difficulty"],
                "matched_required": matched_required,
                "matched_optional": matched_optional,
                "missing_required": missing_required,
                "missing_optional": missing_optional[:4],
                "match_score": match_score,
                "expiry_priority": expiry_priority,
                "reason": (
                    "Prioritised because it uses items expiring soon."
                    if expiry_priority
                    else "Suggested based on your current inventory."
                )
            })

    suggestions.sort(
        key=lambda recipe: (
            recipe["expiry_priority"],
            recipe["match_score"]
        ),
        reverse=True
    )

    if not suggestions:
        suggestions.append({
            "title": "No strong recipe match yet",
            "description": "Add more items to your inventory and ExpireIQ will suggest meals from them.",
            "time": "-",
            "difficulty": "-",
            "matched_required": [],
            "matched_optional": [],
            "missing_required": [],
            "missing_optional": [],
            "match_score": 0,
            "expiry_priority": False,
            "reason": "Not enough matching ingredients were found."
        })

    return suggestions[:12]