"""
Food taxonomy utilities: allergen detection and ingredient categorisation.

This module is the single source of truth for mapping free-text ingredient
names to (a) the 14 UK FIC allergens and (b) coarse cost/price categories. It is
used both by the scraper (to populate ``Ingredient.category``,
``Ingredient.is_allergen`` and ``RecipeAllergen``) and at query time by the
allergen filter and cost estimator.

Matching uses whole-word boundaries (so "eggplant" does not match "egg" and
"butternut" does not match "butter") plus an explicit exclusion list per
allergen to avoid the most common false positives. It is deliberately
conservative: when in doubt it prefers flagging an allergen (a false positive
merely over-restricts) over missing one (a false negative is a safety risk).
"""

import re
from typing import Dict, List, Set

# Allergen name -> (include phrases, exclude phrases). Allergen names match the
# 14 entries seeded in src/database/seed.py.
_ALLERGEN_DEFS: Dict[str, Dict[str, List[str]]] = {
    'gluten': {
        'include': [
            'wheat', 'flour', 'bread', 'breadcrumb', 'breadcrumbs', 'pasta',
            'spaghetti', 'macaroni', 'penne', 'tagliatelle', 'noodle', 'noodles',
            'barley', 'rye', 'seitan', 'couscous', 'bulgur', 'semolina', 'spelt',
            'farro', 'panko', 'cracker', 'crackers', 'pastry', 'pizza', 'tortilla',
            'wrap', 'gnocchi', 'orzo', 'udon', 'soy sauce', 'malt', 'pita', 'naan',
            'brioche', 'croissant', 'bun', 'pancake', 'batter', 'dough', 'pearl barley',
            'ciabatta', 'focaccia', 'baguette', 'linguine', 'farfalle', 'fusilli',
            'rigatoni', 'tortiglioni', 'lasagne', 'lasagna', 'ravioli', 'tortellini',
            'freekeh', 'sourdough', 'bagel', 'crumpet',
        ],
        'exclude': [
            'gluten-free', 'gluten free', 'rice noodle', 'rice noodles',
            'almond flour', 'coconut flour', 'rice flour', 'chickpea flour',
            'gram flour', 'corn tortilla', 'corn flour', 'cornflour', 'buckwheat',
            'tamari', 'rice paper',
        ],
    },
    'dairy': {
        'include': [
            'milk', 'buttermilk', 'cheese', 'butter', 'cream', 'yogurt', 'yoghurt',
            'whey', 'casein', 'lactose', 'ghee', 'paneer', 'custard', 'kefir',
            'ricotta', 'mascarpone', 'parmesan', 'mozzarella', 'cheddar', 'feta',
            'halloumi', 'creme fraiche', 'crème fraîche', 'clotted cream',
            'camembert', 'brie', 'burrata', 'gruyere', 'gruyère', 'gorgonzola',
            'stilton', 'quark', 'skyr', 'gouda', 'emmental', 'manchego', 'pecorino',
            'comte', 'comté', 'taleggio', 'provolone', 'soft cheese', 'goats cheese',
            'cheesecake',
        ],
        'exclude': [
            'coconut milk', 'almond milk', 'oat milk', 'soy milk', 'soya milk',
            'rice milk', 'peanut butter', 'nut butter', 'almond butter',
            'cashew butter', 'cocoa butter', 'shea butter', 'apple butter',
            'butternut', 'butter bean', 'butter beans', 'butterhead',
            'non-dairy', 'dairy-free', 'dairy free', 'coconut cream',
            'coconut yogurt', 'soy yogurt', 'vegan cheese', 'plant milk',
        ],
    },
    'eggs': {
        'include': ['egg', 'eggs', 'mayonnaise', 'mayo', 'meringue', 'aioli', 'frittata', 'quiche', 'custard'],
        'exclude': ['eggplant', 'egg-free', 'vegan mayo', 'vegan mayonnaise'],
    },
    'tree nuts': {
        'include': [
            'almond', 'almonds', 'walnut', 'walnuts', 'cashew', 'cashews', 'pecan',
            'pecans', 'pistachio', 'pistachios', 'hazelnut', 'hazelnuts', 'macadamia',
            'brazil nut', 'pine nut', 'pine nuts', 'marzipan', 'praline', 'nutella',
            'pesto', 'chestnut', 'flaked almonds', 'ground almonds',
            'pine kernel', 'pine kernels', 'cobnut', 'frangipane', 'gianduja',
            'amaretti',
        ],
        'exclude': ['nutmeg', 'coconut', 'water chestnut', 'butternut', 'peanut', 'peanuts', 'doughnut', 'donut'],
    },
    'peanuts': {
        'include': ['peanut', 'peanuts', 'groundnut', 'groundnuts', 'peanut butter', 'satay'],
        'exclude': [],
    },
    'soy': {
        'include': ['soy', 'soya', 'soybean', 'soybeans', 'tofu', 'tempeh', 'edamame', 'miso', 'soy sauce', 'tamari'],
        'exclude': [],
    },
    'fish': {
        'include': [
            'fish', 'salmon', 'tuna', 'cod', 'haddock', 'pollock', 'tilapia',
            'sea bass', 'seabass', 'trout', 'mackerel', 'sardine', 'sardines',
            'anchovy', 'anchovies', 'halibut', 'herring', 'plaice', 'fish sauce',
            'worcestershire', 'basa', 'pollack',
            'monkfish', 'swordfish', 'eel', 'whitebait', 'kipper', 'caviar', 'roe',
            'surimi', 'sea bream', 'seabream', 'snapper', 'sole', 'sprat',
        ],
        'exclude': [],
    },
    'shellfish': {
        'include': [
            'shrimp', 'prawn', 'prawns', 'crab', 'lobster', 'crayfish', 'langoustine',
            'scallop', 'scallops', 'mussel', 'mussels', 'clam', 'clams', 'oyster',
            'oysters', 'squid', 'calamari', 'octopus', 'cuttlefish', 'crustacean',
            'mollusc', 'mollusk', 'oyster sauce',
        ],
        'exclude': [],
    },
    'sesame': {
        'include': ['sesame', 'tahini', 'hummus', 'houmous'],
        'exclude': [],
    },
    'mustard': {
        'include': ['mustard'],
        'exclude': [],
    },
    'celery': {
        'include': ['celery', 'celeriac'],
        'exclude': [],
    },
    'lupin': {
        'include': ['lupin', 'lupini'],
        'exclude': [],
    },
    'sulfites': {
        'include': ['sulfite', 'sulphite', 'sulfur dioxide', 'sulphur dioxide', 'wine', 'dried apricot', 'dried apricots'],
        'exclude': [],
    },
}

# Cost/price categories (keys align with CostEstimator.DEFAULT_PRICES).
_CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    'protein': [
        'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'bacon', 'sausage',
        'mince', 'steak', 'ham', 'salmon', 'tuna', 'cod', 'haddock', 'basa',
        'fish', 'prawn', 'prawns', 'shrimp', 'tofu', 'tempeh', 'egg', 'eggs',
        'halloumi', 'chorizo', 'gammon',
    ],
    'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'yoghurt', 'paneer', 'mozzarella', 'cheddar', 'feta', 'mascarpone'],
    'grain': [
        'rice', 'pasta', 'spaghetti', 'noodle', 'noodles', 'bread', 'flour',
        'oats', 'oat', 'couscous', 'quinoa', 'bulgur', 'barley', 'tortilla',
        'wrap', 'lentil', 'lentils', 'bean', 'beans', 'chickpea', 'chickpeas',
        'potato', 'potatoes',
    ],
    'fruit': ['apple', 'banana', 'orange', 'lemon', 'lime', 'berry', 'berries', 'strawberry', 'mango', 'pineapple', 'grape', 'peach', 'pear', 'avocado'],
    'oil': ['oil', 'olive oil', 'vegetable oil', 'sunflower oil', 'sesame oil', 'coconut oil'],
    'herb': ['basil', 'parsley', 'coriander', 'cilantro', 'mint', 'thyme', 'rosemary', 'dill', 'oregano', 'chive', 'chives', 'sage'],
    'spice': ['pepper', 'salt', 'cumin', 'paprika', 'turmeric', 'cinnamon', 'chilli', 'chili', 'curry powder', 'garam masala', 'nutmeg', 'cardamom', 'coriander seed'],
    'condiment': ['sauce', 'ketchup', 'mayonnaise', 'mustard', 'vinegar', 'soy sauce', 'honey', 'syrup', 'paste', 'stock', 'jam'],
    'vegetable': [
        'onion', 'garlic', 'tomato', 'carrot', 'pepper', 'broccoli', 'cauliflower',
        'spinach', 'kale', 'courgette', 'zucchini', 'mushroom', 'cucumber',
        'lettuce', 'cabbage', 'leek', 'celery', 'aubergine', 'eggplant', 'pea',
        'peas', 'sweetcorn', 'corn', 'green bean', 'asparagus', 'beetroot',
        'squash', 'pumpkin', 'shallot', 'ginger', 'spring onion',
    ],
}


def _normalize(name: str) -> str:
    """Lowercase and collapse whitespace for matching."""
    return re.sub(r'\s+', ' ', (name or '').lower()).strip()


def _phrase_in(haystack: str, phrase: str) -> bool:
    """
    Whole-word/phrase containment. Multi-word or hyphenated phrases use plain
    substring matching; single tokens require word boundaries so "egg" does not
    match "eggplant".
    """
    if ' ' in phrase or '-' in phrase:
        return phrase in haystack
    return re.search(rf'\b{re.escape(phrase)}\b', haystack) is not None


def ingredient_contains_allergen(ingredient_name: str, allergen_name: str) -> bool:
    """
    Return True if the ingredient name indicates the given allergen.

    Exclusions take precedence over inclusions (e.g. "peanut butter" is not
    flagged as dairy even though it contains the word "butter").
    """
    defs = _ALLERGEN_DEFS.get((allergen_name or '').lower())
    if not defs:
        return False

    name = _normalize(ingredient_name)
    if any(_phrase_in(name, ex) for ex in defs['exclude']):
        return False
    return any(_phrase_in(name, inc) for inc in defs['include'])


def detect_allergens(ingredient_name: str) -> Set[str]:
    """Return the set of allergen names present in an ingredient name."""
    return {
        allergen
        for allergen in _ALLERGEN_DEFS
        if ingredient_contains_allergen(ingredient_name, allergen)
    }


def categorize_ingredient(ingredient_name: str) -> str:
    """
    Classify an ingredient into a coarse cost category.

    Returns one of: protein, dairy, grain, fruit, oil, herb, spice, condiment,
    vegetable, other. Order matters — more specific/expensive categories are
    checked first so e.g. "chicken stock" is treated as protein rather than a
    generic condiment.
    """
    name = _normalize(ingredient_name)
    if not name:
        return 'other'

    # Most specific first.
    for category in ('protein', 'dairy', 'oil', 'herb', 'spice', 'fruit', 'grain', 'condiment', 'vegetable'):
        if any(_phrase_in(name, kw) for kw in _CATEGORY_KEYWORDS[category]):
            return category
    return 'other'


def known_allergens() -> List[str]:
    """Return the list of allergen names this module can detect."""
    return list(_ALLERGEN_DEFS.keys())
