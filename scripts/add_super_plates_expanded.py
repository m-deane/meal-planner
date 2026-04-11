"""
Add expanded Super Plates-style recipes from competitors and food blogs.
Sources: Leon, Itsu, Farmer J, and popular food blogs.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.database.connection import get_engine, get_session_factory
from src.database.models import (
    Recipe, RecipeIngredient, Ingredient, Unit,
    CookingInstruction, NutritionalInfo, Image,
    Category, Allergen, DietaryTag,
)


SUPER_PLATE_RECIPES = [
    # ─── LEON ───
    {
        "gousto_id": "leon-paprika-chicken",
        "slug": "leon-paprika-chicken-super-salad",
        "name": "Leon Paprika Chicken Super Salad",
        "description": (
            "A Leon super salad with smoky paprika-marinated chargrilled chicken "
            "on Middle Eastern spiced roasted vegetables, green lentils, quinoa, "
            "chickpeas, and a firecracker dressing. 28 plant varieties."
        ),
        "cooking_time_minutes": 25,
        "prep_time_minutes": 15,
        "difficulty": "medium",
        "servings": 1,
        "source_url": "https://leon.co/menu/paprika-chicken-super-salad/",
        "categories": ["Salad", "Lunch"],
        "dietary_tags": ["high-protein", "gluten-free"],
        "allergens": [],
        "ingredients": [
            {"name": "Chicken Thigh", "quantity": 150, "unit": "g", "category": "protein"},
            {"name": "Smoked Paprika", "quantity": 1, "unit": "tsp", "category": "spice"},
            {"name": "Red Onion", "quantity": 50, "unit": "g", "category": "vegetable"},
            {"name": "Cauliflower", "quantity": 60, "unit": "g", "category": "vegetable"},
            {"name": "Red Pepper", "quantity": 40, "unit": "g", "category": "vegetable"},
            {"name": "Sweet Potato", "quantity": 50, "unit": "g", "category": "vegetable"},
            {"name": "Green Lentils", "quantity": 40, "unit": "g", "category": "legume"},
            {"name": "Quinoa", "quantity": 30, "unit": "g", "category": "grain"},
            {"name": "Chickpeas", "quantity": 30, "unit": "g", "category": "legume"},
            {"name": "Spinach", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Cos Lettuce", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Mixed Seeds", "quantity": 10, "unit": "g", "category": "nuts"},
            {"name": "Parsley", "quantity": None, "unit": None, "category": "herb"},
            {"name": "Mint", "quantity": None, "unit": None, "category": "herb"},
        ],
        "nutrition": {
            "serving_size_g": 305,
            "calories": 418,
            "protein_g": 25.0,
            "carbohydrates_g": 19.0,
            "fat_g": 27.0,
            "saturated_fat_g": 4.2,
            "fiber_g": 8.0,
            "sugar_g": 8.0,
            "sodium_mg": 860,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Marinate chicken thighs in smoked paprika, cumin, coriander, olive oil, lemon juice, salt, and pepper for at least 30 minutes."},
            {"step": 2, "text": "Toss cauliflower, sweet potato, red onion, red pepper, and carrot with sumac, paprika, thyme, cumin, and olive oil. Roast at 200°C for 25 minutes."},
            {"step": 3, "text": "Cook the green lentils and quinoa according to package instructions. Drain and cool slightly."},
            {"step": 4, "text": "Chargrill or pan-fry the marinated chicken for 5-6 minutes per side until cooked through. Slice."},
            {"step": 5, "text": "Make the firecracker dressing by blending coriander, cumin, cardamom, chilli, olive oil, and lemon juice."},
            {"step": 6, "text": "Assemble: layer spinach and cos lettuce, top with grains, roasted veg, chickpeas, sliced chicken, seeds, and herbs. Drizzle with firecracker dressing."},
        ],
    },
    # ─── ITSU ───
    {
        "gousto_id": "itsu-teriyaki-chicken",
        "slug": "itsu-chicken-teriyaki-rice-bowl",
        "name": "Itsu Chicken Teriyaki Rice Bowl",
        "description": (
            "A Japanese-inspired rice bowl from Itsu with miso-marinated chicken, "
            "wholegrain brown rice, vitamin-packed greens, ginger, teriyaki sauce, "
            "and sesame seeds. High protein, 51g per serving."
        ),
        "cooking_time_minutes": 15,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 1,
        "source_url": "https://www.itsu.com/menu/rice-bowls/",
        "categories": ["Lunch"],
        "dietary_tags": ["high-protein"],
        "allergens": ["gluten", "sesame", "soy"],
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 180, "unit": "g", "category": "protein"},
            {"name": "White Miso Paste", "quantity": 1, "unit": "tbsp", "category": "condiment"},
            {"name": "Brown Rice", "quantity": 150, "unit": "g", "category": "grain"},
            {"name": "Teriyaki Sauce", "quantity": 2, "unit": "tbsp", "category": "condiment"},
            {"name": "Ginger", "quantity": 5, "unit": "g", "category": "spice"},
            {"name": "Edamame Beans", "quantity": 40, "unit": "g", "category": "legume"},
            {"name": "Pak Choi", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Spring Onion", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Sesame Seeds", "quantity": 5, "unit": "g", "category": "nuts"},
        ],
        "nutrition": {
            "serving_size_g": 450,
            "calories": 619,
            "protein_g": 51.0,
            "carbohydrates_g": 65.0,
            "fat_g": 20.0,
            "saturated_fat_g": 4.4,
            "fiber_g": 10.0,
            "sugar_g": 12.0,
            "sodium_mg": 900,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Marinate chicken breast in miso paste, a splash of mirin, and ginger for at least 20 minutes."},
            {"step": 2, "text": "Cook brown rice according to package instructions."},
            {"step": 3, "text": "Pan-fry or grill the miso chicken for 6-7 minutes per side until cooked through. Slice."},
            {"step": 4, "text": "Blanch pak choi and edamame beans in boiling water for 2 minutes."},
            {"step": 5, "text": "Assemble bowl with rice, sliced chicken, pak choi, edamame, and spring onion. Drizzle with teriyaki sauce and sprinkle with sesame seeds."},
        ],
    },
    # ─── FARMER J ───
    {
        "gousto_id": "farmerj-harissa-chicken",
        "slug": "farmer-j-harissa-chicken-bowl",
        "name": "Farmer J Harissa Chicken Bowl",
        "description": (
            "A Farmer J fieldbowl with harissa-spiced chicken thighs, farmer's "
            "grains, spiced date sweet potatoes, sesame cabbage, green tahini, "
            "and pickled red onion. Bold North African flavours."
        ),
        "cooking_time_minutes": 30,
        "prep_time_minutes": 15,
        "difficulty": "medium",
        "servings": 4,
        "source_url": "https://www.farmerj.com/harissa-chicken/",
        "categories": ["Lunch", "Dinner"],
        "dietary_tags": ["high-protein"],
        "allergens": ["sesame"],
        "ingredients": [
            {"name": "Chicken Thigh", "quantity": 500, "unit": "g", "category": "protein"},
            {"name": "Harissa Paste", "quantity": 3, "unit": "tbsp", "category": "condiment"},
            {"name": "Sweet Potato", "quantity": 300, "unit": "g", "category": "vegetable"},
            {"name": "Medjool Dates", "quantity": 4, "unit": "whole", "category": "fruit"},
            {"name": "Brown Rice", "quantity": 200, "unit": "g", "category": "grain"},
            {"name": "Red Cabbage", "quantity": 100, "unit": "g", "category": "vegetable"},
            {"name": "Tahini", "quantity": 3, "unit": "tbsp", "category": "condiment"},
            {"name": "Lemon", "quantity": 1, "unit": "whole", "category": "fruit"},
            {"name": "Pickled Red Onion", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Parsley", "quantity": None, "unit": None, "category": "herb"},
            {"name": "Cumin Seeds", "quantity": 1, "unit": "tsp", "category": "spice"},
            {"name": "Coriander Seeds", "quantity": 1, "unit": "tsp", "category": "spice"},
            {"name": "Olive Oil", "quantity": 2, "unit": "tbsp", "category": "oil"},
        ],
        "nutrition": {
            "serving_size_g": 480,
            "calories": 620,
            "protein_g": 38.0,
            "carbohydrates_g": 55.0,
            "fat_g": 26.0,
            "saturated_fat_g": 5.0,
            "fiber_g": 9.0,
            "sugar_g": 14.0,
            "sodium_mg": 800,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Make harissa paste: toast coriander seeds, cumin seeds, caraway seeds, and black pepper in a dry pan. Grind with soaked dried chillies, garlic, olive oil, and chilli flakes."},
            {"step": 2, "text": "Rub harissa generously over chicken thighs. Marinate for at least 30 minutes (or overnight)."},
            {"step": 3, "text": "Roast sweet potatoes tossed with chopped dates, cinnamon, and olive oil at 200°C for 25 minutes."},
            {"step": 4, "text": "Cook brown rice. Meanwhile, shred red cabbage and toss with sesame oil, rice vinegar, and salt."},
            {"step": 5, "text": "Grill or roast harissa chicken at 200°C for 25-30 minutes until charred and cooked through. Rest and slice."},
            {"step": 6, "text": "Make green tahini by blending tahini, lemon juice, parsley, water, garlic, and salt."},
            {"step": 7, "text": "Assemble bowls with rice, sweet potato, sesame cabbage, sliced chicken, pickled onion, and a generous drizzle of green tahini."},
        ],
    },
    {
        "gousto_id": "farmerj-gochujang-salmon",
        "slug": "farmer-j-gochujang-salmon-bowl",
        "name": "Farmer J Gochujang Salmon Bowl",
        "description": (
            "A Farmer J fieldbowl with gochujang-glazed salmon, sesame cabbage, "
            "kale miso slaw, sesame cucumber, and smashed avocado. Korean-Japanese "
            "fusion flavours with omega-3 rich salmon."
        ),
        "cooking_time_minutes": 20,
        "prep_time_minutes": 15,
        "difficulty": "medium",
        "servings": 2,
        "source_url": "https://www.farmerj.com/fieldbowls/",
        "categories": ["Lunch", "Dinner"],
        "dietary_tags": ["high-protein", "dairy-free"],
        "allergens": ["fish", "soy", "sesame"],
        "ingredients": [
            {"name": "Salmon", "quantity": 300, "unit": "g", "category": "protein"},
            {"name": "Gochujang Paste", "quantity": 2, "unit": "tbsp", "category": "condiment"},
            {"name": "Brown Rice", "quantity": 150, "unit": "g", "category": "grain"},
            {"name": "Red Cabbage", "quantity": 100, "unit": "g", "category": "vegetable"},
            {"name": "Kale", "quantity": 50, "unit": "g", "category": "vegetable"},
            {"name": "Cucumber", "quantity": 1, "unit": "whole", "category": "vegetable"},
            {"name": "Avocado", "quantity": 1, "unit": "whole", "category": "vegetable"},
            {"name": "White Miso Paste", "quantity": 1, "unit": "tbsp", "category": "condiment"},
            {"name": "Sesame Oil", "quantity": 1, "unit": "tbsp", "category": "oil"},
            {"name": "Rice Vinegar", "quantity": 1, "unit": "tbsp", "category": "condiment"},
            {"name": "Sesame Seeds", "quantity": 10, "unit": "g", "category": "nuts"},
            {"name": "Lime", "quantity": 1, "unit": "whole", "category": "fruit"},
        ],
        "nutrition": {
            "serving_size_g": 500,
            "calories": 680,
            "protein_g": 40.0,
            "carbohydrates_g": 48.0,
            "fat_g": 36.0,
            "saturated_fat_g": 6.5,
            "fiber_g": 10.0,
            "sugar_g": 8.0,
            "sodium_mg": 950,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Mix gochujang paste with a splash of soy sauce, honey, and sesame oil. Coat salmon fillets and marinate for 15 minutes."},
            {"step": 2, "text": "Cook brown rice according to package instructions."},
            {"step": 3, "text": "Make kale miso slaw: massage kale with miso paste, rice vinegar, and sesame oil until softened."},
            {"step": 4, "text": "Slice cucumber into ribbons, toss with rice vinegar, sesame seeds, and a pinch of salt."},
            {"step": 5, "text": "Bake salmon at 200°C for 12-15 minutes until glazed and cooked through."},
            {"step": 6, "text": "Shred red cabbage and toss with sesame oil and rice vinegar."},
            {"step": 7, "text": "Assemble bowls with rice, smashed avocado, sesame cabbage, kale miso slaw, cucumber, and flaked salmon. Squeeze over lime."},
        ],
    },
    {
        "gousto_id": "farmerj-lime-leaf-tofu",
        "slug": "farmer-j-lime-leaf-tofu-bowl",
        "name": "Farmer J Lime Leaf Tofu Bowl",
        "description": (
            "A vegan Farmer J fieldbowl with crispy lime leaf tofu, brown rice, "
            "charred greens, mushrooms with nori crunch, and sesame cucumber. "
            "Light, fresh, and packed with umami."
        ),
        "cooking_time_minutes": 25,
        "prep_time_minutes": 15,
        "difficulty": "medium",
        "servings": 2,
        "source_url": "https://www.farmerj.com/fieldbowls/",
        "categories": ["Salad", "Lunch"],
        "dietary_tags": ["vegan", "dairy-free"],
        "allergens": ["soy", "sesame"],
        "ingredients": [
            {"name": "Firm Tofu", "quantity": 300, "unit": "g", "category": "protein"},
            {"name": "Kaffir Lime Leaves", "quantity": 4, "unit": "whole", "category": "herb"},
            {"name": "Brown Rice", "quantity": 150, "unit": "g", "category": "grain"},
            {"name": "Shiitake Mushrooms", "quantity": 100, "unit": "g", "category": "vegetable"},
            {"name": "Tenderstem Broccoli", "quantity": 100, "unit": "g", "category": "vegetable"},
            {"name": "Cucumber", "quantity": 1, "unit": "whole", "category": "vegetable"},
            {"name": "Nori Sheets", "quantity": 2, "unit": "whole", "category": "condiment"},
            {"name": "Sesame Seeds", "quantity": 10, "unit": "g", "category": "nuts"},
            {"name": "Soy Sauce", "quantity": 2, "unit": "tbsp", "category": "condiment"},
            {"name": "Sesame Oil", "quantity": 1, "unit": "tbsp", "category": "oil"},
            {"name": "Lime", "quantity": 1, "unit": "whole", "category": "fruit"},
            {"name": "Cornflour", "quantity": 2, "unit": "tbsp", "category": "grain"},
        ],
        "nutrition": {
            "serving_size_g": 460,
            "calories": 520,
            "protein_g": 28.0,
            "carbohydrates_g": 52.0,
            "fat_g": 22.0,
            "saturated_fat_g": 3.5,
            "fiber_g": 8.0,
            "sugar_g": 5.0,
            "sodium_mg": 880,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Press tofu for 15 minutes, then cut into cubes. Toss with cornflour, finely sliced lime leaves, salt, and pepper."},
            {"step": 2, "text": "Cook brown rice according to package instructions."},
            {"step": 3, "text": "Pan-fry tofu in vegetable oil over high heat until golden and crispy on all sides, about 8 minutes."},
            {"step": 4, "text": "Char tenderstem broccoli in a hot pan with a splash of sesame oil for 3-4 minutes."},
            {"step": 5, "text": "Sauté shiitake mushrooms with soy sauce until golden. Tear nori sheets into small pieces for crunch."},
            {"step": 6, "text": "Slice cucumber and toss with rice vinegar and sesame seeds."},
            {"step": 7, "text": "Assemble bowls with rice, crispy tofu, charred broccoli, mushrooms, sesame cucumber, and nori crunch. Squeeze over lime."},
        ],
    },
    # ─── FOOD BLOG RECIPES ───
    {
        "gousto_id": "blog-korean-bbq-chicken",
        "slug": "korean-bbq-chicken-super-bowl",
        "name": "Korean BBQ Chicken Super Bowl",
        "description": (
            "A high-protein rice bowl with juicy Korean BBQ chicken thighs, "
            "crunchy shredded vegetables, purple cabbage, and sesame seeds. "
            "Ready in 20 minutes, perfect for meal prep."
        ),
        "cooking_time_minutes": 15,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 4,
        "source_url": "https://www.fitmamarealfood.com/korean-bbq-chicken-bowl/",
        "categories": ["Lunch", "Dinner"],
        "dietary_tags": ["high-protein", "dairy-free"],
        "allergens": ["soy", "sesame"],
        "ingredients": [
            {"name": "Chicken Thigh", "quantity": 680, "unit": "g", "category": "protein"},
            {"name": "Korean BBQ Sauce", "quantity": 120, "unit": "ml", "category": "condiment"},
            {"name": "Brown Rice", "quantity": 300, "unit": "g", "category": "grain"},
            {"name": "Carrot", "quantity": 200, "unit": "g", "category": "vegetable"},
            {"name": "Cucumber", "quantity": 200, "unit": "g", "category": "vegetable"},
            {"name": "Red Cabbage", "quantity": 200, "unit": "g", "category": "vegetable"},
            {"name": "Spring Onion", "quantity": 4, "unit": "whole", "category": "vegetable"},
            {"name": "Sesame Seeds", "quantity": 15, "unit": "g", "category": "nuts"},
            {"name": "Lime", "quantity": 1, "unit": "whole", "category": "fruit"},
            {"name": "Chilli Flakes", "quantity": None, "unit": None, "category": "spice"},
        ],
        "nutrition": {
            "serving_size_g": 450,
            "calories": 544,
            "protein_g": 35.0,
            "carbohydrates_g": 37.0,
            "fat_g": 29.0,
            "saturated_fat_g": 7.0,
            "fiber_g": 8.0,
            "sugar_g": 12.0,
            "sodium_mg": 780,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Dice chicken thighs into bite-sized pieces. Cook in a large pan over medium-high heat for 5-6 minutes until browned."},
            {"step": 2, "text": "Add Korean BBQ sauce to the chicken and cook for another 2-3 minutes until caramelised and sticky."},
            {"step": 3, "text": "Cook brown rice according to package instructions (or use pre-cooked for speed)."},
            {"step": 4, "text": "Shred carrot, slice cucumber into ribbons, and finely shred red cabbage."},
            {"step": 5, "text": "Assemble bowls with rice, BBQ chicken, shredded vegetables, sliced spring onion, sesame seeds, and lime wedges. Add chilli flakes to taste."},
        ],
    },
    {
        "gousto_id": "blog-salmon-tahini-power",
        "slug": "salmon-power-bowl-lemon-tahini",
        "name": "Salmon Power Bowl with Lemon Tahini",
        "description": (
            "Roasted salmon with quinoa, roasted root vegetables (parsnips, "
            "brussels sprouts, sweet potato), and a creamy lemon tahini sauce. "
            "Paleo-friendly and packed with omega-3."
        ),
        "cooking_time_minutes": 25,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 2,
        "source_url": "https://www.fitmittenkitchen.com/salmon-grain-bowl/",
        "categories": ["Lunch", "Dinner"],
        "dietary_tags": ["high-protein", "gluten-free", "dairy-free"],
        "allergens": ["fish", "sesame"],
        "ingredients": [
            {"name": "Salmon", "quantity": 200, "unit": "g", "category": "protein"},
            {"name": "Quinoa", "quantity": 80, "unit": "g", "category": "grain"},
            {"name": "Parsnip", "quantity": 150, "unit": "g", "category": "vegetable"},
            {"name": "Brussels Sprouts", "quantity": 100, "unit": "g", "category": "vegetable"},
            {"name": "Sweet Potato", "quantity": 150, "unit": "g", "category": "vegetable"},
            {"name": "Tahini", "quantity": 3, "unit": "tbsp", "category": "condiment"},
            {"name": "Lemon", "quantity": 1, "unit": "whole", "category": "fruit"},
            {"name": "Dijon Mustard", "quantity": 1, "unit": "tsp", "category": "condiment"},
            {"name": "Garlic", "quantity": 1, "unit": "clove", "category": "vegetable"},
            {"name": "Olive Oil", "quantity": 1, "unit": "tbsp", "category": "oil"},
        ],
        "nutrition": {
            "serving_size_g": 480,
            "calories": 609,
            "protein_g": 35.0,
            "carbohydrates_g": 74.0,
            "fat_g": 20.0,
            "saturated_fat_g": 4.0,
            "fiber_g": 18.0,
            "sugar_g": 10.0,
            "sodium_mg": 450,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Preheat oven to 200°C. Peel and chop parsnips and sweet potato into cubes. Halve brussels sprouts."},
            {"step": 2, "text": "Toss vegetables with olive oil, salt, and pepper. Spread on a baking tray and roast for 20 minutes."},
            {"step": 3, "text": "Season salmon with mustard, garlic, lemon juice, salt, and pepper. Add to the tray for the last 12-15 minutes."},
            {"step": 4, "text": "Cook quinoa in water according to package instructions. Fluff with a fork."},
            {"step": 5, "text": "Make lemon tahini sauce: whisk tahini, lemon juice, rice vinegar, a splash of plant milk, and salt until smooth and pourable."},
            {"step": 6, "text": "Assemble bowls with quinoa, roasted vegetables, flaked salmon, and a generous drizzle of lemon tahini sauce."},
        ],
    },
    {
        "gousto_id": "blog-med-chicken-quinoa",
        "slug": "mediterranean-chicken-quinoa-tahini-bowl",
        "name": "Mediterranean Chicken Quinoa Bowl",
        "description": (
            "An anti-inflammatory bowl with roasted chicken, fluffy quinoa cooked "
            "in broth, fresh herbs, cucumber, kalamata olives, crumbled feta, and "
            "a simple tahini-lemon dressing. Light but filling."
        ),
        "cooking_time_minutes": 20,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 3,
        "source_url": "https://www.purewow.com/recipes/mediterranean-chicken-quinoa-bowls-recipe",
        "categories": ["Salad", "Lunch"],
        "dietary_tags": ["high-protein", "gluten-free"],
        "allergens": ["dairy", "sesame"],
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 400, "unit": "g", "category": "protein"},
            {"name": "Quinoa", "quantity": 180, "unit": "g", "category": "grain"},
            {"name": "Chicken Broth", "quantity": 400, "unit": "ml", "category": "condiment"},
            {"name": "Cucumber", "quantity": 100, "unit": "g", "category": "vegetable"},
            {"name": "Kalamata Olives", "quantity": 50, "unit": "g", "category": "vegetable"},
            {"name": "Feta Cheese", "quantity": 40, "unit": "g", "category": "dairy"},
            {"name": "Parsley", "quantity": None, "unit": None, "category": "herb"},
            {"name": "Tahini", "quantity": 2, "unit": "tbsp", "category": "condiment"},
            {"name": "Lemon", "quantity": 1, "unit": "whole", "category": "fruit"},
            {"name": "Olive Oil", "quantity": 2, "unit": "tbsp", "category": "oil"},
        ],
        "nutrition": {
            "serving_size_g": 420,
            "calories": 580,
            "protein_g": 45.0,
            "carbohydrates_g": 42.0,
            "fat_g": 24.0,
            "saturated_fat_g": 5.0,
            "fiber_g": 6.0,
            "sugar_g": 3.0,
            "sodium_mg": 650,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Cook quinoa in chicken broth for extra flavour. Bring to a boil, reduce heat, cover, and simmer for 15 minutes."},
            {"step": 2, "text": "Season chicken breasts with salt, pepper, and a drizzle of olive oil. Roast at 200°C for 18-20 minutes until cooked through. Rest and chop."},
            {"step": 3, "text": "Dice cucumber, halve olives, and roughly chop parsley."},
            {"step": 4, "text": "Fluff quinoa and fold in chopped parsley, diced cucumber, and a squeeze of lemon."},
            {"step": 5, "text": "Make dressing: whisk tahini, olive oil, lemon juice, and a splash of water until smooth."},
            {"step": 6, "text": "Divide quinoa between bowls, top with chicken, olives, crumbled feta, and drizzle with tahini dressing."},
        ],
    },
    {
        "gousto_id": "blog-bulgur-halloumi",
        "slug": "mediterranean-bulgur-halloumi-bowl",
        "name": "Mediterranean Bulgur & Halloumi Bowl",
        "description": (
            "A vegetarian Mediterranean bowl with seasoned bulgur wheat, golden "
            "pan-seared halloumi, chickpeas, cherry tomatoes, cucumber, kalamata "
            "olives, and a creamy lemon-garlic yogurt dressing."
        ),
        "cooking_time_minutes": 20,
        "prep_time_minutes": 15,
        "difficulty": "easy",
        "servings": 4,
        "source_url": "https://www.kitchenfairy.ca/mediterranean-bulgur-and-halloumi-bowl/",
        "categories": ["Salad", "Lunch", "Dinner"],
        "dietary_tags": ["vegetarian"],
        "allergens": ["dairy", "gluten"],
        "ingredients": [
            {"name": "Halloumi", "quantity": 400, "unit": "g", "category": "dairy"},
            {"name": "Bulgur Wheat", "quantity": 200, "unit": "g", "category": "grain"},
            {"name": "Chickpeas", "quantity": 400, "unit": "g", "category": "legume"},
            {"name": "Cherry Tomatoes", "quantity": 200, "unit": "g", "category": "vegetable"},
            {"name": "Cucumber", "quantity": 150, "unit": "g", "category": "vegetable"},
            {"name": "Kalamata Olives", "quantity": 80, "unit": "g", "category": "vegetable"},
            {"name": "Red Onion", "quantity": 50, "unit": "g", "category": "vegetable"},
            {"name": "Greek Yogurt", "quantity": 120, "unit": "g", "category": "dairy"},
            {"name": "Lemon", "quantity": 1, "unit": "whole", "category": "fruit"},
            {"name": "Garlic", "quantity": 2, "unit": "clove", "category": "vegetable"},
            {"name": "Dried Oregano", "quantity": 2, "unit": "tsp", "category": "spice"},
            {"name": "Cumin", "quantity": 1, "unit": "tsp", "category": "spice"},
            {"name": "Olive Oil", "quantity": 3, "unit": "tbsp", "category": "oil"},
            {"name": "Parsley", "quantity": None, "unit": None, "category": "herb"},
        ],
        "nutrition": {
            "serving_size_g": 470,
            "calories": 620,
            "protein_g": 30.0,
            "carbohydrates_g": 52.0,
            "fat_g": 32.0,
            "saturated_fat_g": 14.0,
            "fiber_g": 10.0,
            "sugar_g": 6.0,
            "sodium_mg": 900,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Cook bulgur wheat in vegetable broth with cumin, salt, and pepper. Cover and simmer for 12 minutes. Fluff and stir in chopped parsley."},
            {"step": 2, "text": "Slice halloumi into 1cm slices. Pan-fry in olive oil for 2 minutes per side until golden."},
            {"step": 3, "text": "Drain and rinse chickpeas. Halve cherry tomatoes, dice cucumber, slice red onion, and halve olives."},
            {"step": 4, "text": "Make dressing: whisk Greek yogurt, olive oil, lemon juice, red wine vinegar, minced garlic, oregano, salt, and pepper."},
            {"step": 5, "text": "Assemble bowls with seasoned bulgur, chickpeas, tomatoes, cucumber, olives, onion, golden halloumi, and a generous spoonful of lemon-garlic yogurt dressing."},
        ],
    },
    {
        "gousto_id": "blog-miso-salmon-bowls",
        "slug": "miso-salmon-rice-bowls-homemade",
        "name": "Miso Salmon Rice Bowls",
        "description": (
            "Clean, simple salmon bites with roasted shiitake mushrooms, edamame, "
            "avocado, red cabbage, and a punchy miso-ginger dressing. Japanese "
            "comfort food, ready in 40 minutes."
        ),
        "cooking_time_minutes": 25,
        "prep_time_minutes": 15,
        "difficulty": "medium",
        "servings": 4,
        "source_url": "https://www.feastingathome.com/miso-salmon-bowls/",
        "categories": ["Lunch", "Dinner"],
        "dietary_tags": ["high-protein", "dairy-free"],
        "allergens": ["fish", "soy", "sesame"],
        "ingredients": [
            {"name": "Salmon", "quantity": 450, "unit": "g", "category": "protein"},
            {"name": "Brown Rice", "quantity": 300, "unit": "g", "category": "grain"},
            {"name": "Shiitake Mushrooms", "quantity": 200, "unit": "g", "category": "vegetable"},
            {"name": "Edamame Beans", "quantity": 200, "unit": "g", "category": "legume"},
            {"name": "Avocado", "quantity": 1, "unit": "whole", "category": "vegetable"},
            {"name": "Red Cabbage", "quantity": 150, "unit": "g", "category": "vegetable"},
            {"name": "White Miso Paste", "quantity": 2, "unit": "tbsp", "category": "condiment"},
            {"name": "Sesame Oil", "quantity": 3, "unit": "tbsp", "category": "oil"},
            {"name": "Rice Vinegar", "quantity": 3, "unit": "tbsp", "category": "condiment"},
            {"name": "Maple Syrup", "quantity": 3, "unit": "tbsp", "category": "condiment"},
            {"name": "Soy Sauce", "quantity": 2, "unit": "tbsp", "category": "condiment"},
            {"name": "Ginger", "quantity": 10, "unit": "g", "category": "spice"},
            {"name": "Garlic", "quantity": 2, "unit": "clove", "category": "vegetable"},
        ],
        "nutrition": {
            "serving_size_g": 480,
            "calories": 620,
            "protein_g": 39.0,
            "carbohydrates_g": 58.8,
            "fat_g": 28.0,
            "saturated_fat_g": 5.0,
            "fiber_g": 9.0,
            "sugar_g": 12.0,
            "sodium_mg": 850,
        },
        "images": [],
        "instructions": [
            {"step": 1, "text": "Season salmon with five-spice, salt, garlic powder, onion powder, ginger, pepper, and a pinch of sugar. Bake at 200°C for 12-15 minutes."},
            {"step": 2, "text": "Cook brown rice according to package instructions."},
            {"step": 3, "text": "Sauté shiitake mushrooms in sesame oil until golden and crispy, about 5 minutes."},
            {"step": 4, "text": "Cook edamame in boiling water for 3 minutes. Drain."},
            {"step": 5, "text": "Make miso dressing: whisk olive oil, sesame oil, rice vinegar, maple syrup, miso paste, soy sauce, minced garlic, grated ginger, and water until smooth."},
            {"step": 6, "text": "Shred red cabbage and slice avocado."},
            {"step": 7, "text": "Assemble bowls with rice, flaked salmon, mushrooms, edamame, avocado, red cabbage, and a generous pour of miso dressing."},
        ],
    },
]


def get_or_create_ingredient(session: Session, name: str, category: str = None) -> Ingredient:
    ingredient = session.query(Ingredient).filter_by(name=name).first()
    if not ingredient:
        ingredient = Ingredient(name=name, category=category)
        session.add(ingredient)
        session.flush()
    return ingredient


def get_or_create_category(session: Session, name: str) -> Category:
    category = session.query(Category).filter_by(name=name).first()
    if not category:
        slug = name.lower().replace(" ", "-")
        category = Category(name=name, slug=slug, category_type="meal_type")
        session.add(category)
        session.flush()
    return category


def insert_recipe(session: Session, data: dict) -> Recipe:
    existing = session.query(Recipe).filter_by(slug=data["slug"]).first()
    if existing:
        print(f"  Skipping '{data['name']}' - already exists (id={existing.id})")
        return existing

    recipe = Recipe(
        gousto_id=data["gousto_id"],
        slug=data["slug"],
        name=data["name"],
        description=data["description"],
        cooking_time_minutes=data["cooking_time_minutes"],
        prep_time_minutes=data["prep_time_minutes"],
        difficulty=data["difficulty"],
        servings=data["servings"],
        source_url=data["source_url"],
    )

    # Ingredients
    unit_cache = {}
    for i, ing_data in enumerate(data["ingredients"]):
        ingredient = get_or_create_ingredient(
            session, ing_data["name"], ing_data.get("category")
        )
        unit = None
        if ing_data.get("unit"):
            abbrev = ing_data["unit"]
            if abbrev not in unit_cache:
                unit_cache[abbrev] = session.query(Unit).filter_by(abbreviation=abbrev).first()
            unit = unit_cache[abbrev]

        recipe_ingredient = RecipeIngredient(
            ingredient=ingredient,
            quantity=ing_data.get("quantity"),
            unit=unit,
            is_optional=False,
            display_order=i,
        )
        recipe.ingredients_association.append(recipe_ingredient)

    # Nutrition
    nut = data["nutrition"]
    recipe.nutritional_info = NutritionalInfo(
        serving_size_g=nut.get("serving_size_g"),
        calories=nut["calories"],
        protein_g=nut["protein_g"],
        carbohydrates_g=nut["carbohydrates_g"],
        fat_g=nut["fat_g"],
        saturated_fat_g=nut.get("saturated_fat_g"),
        fiber_g=nut.get("fiber_g"),
        sugar_g=nut.get("sugar_g"),
        sodium_mg=nut.get("sodium_mg"),
    )

    # Images
    for j, img_data in enumerate(data.get("images", [])):
        image = Image(
            url=img_data["url"],
            image_type=img_data.get("type", "main"),
            alt_text=img_data.get("alt_text"),
            display_order=j,
        )
        recipe.images.append(image)

    # Instructions
    for inst in data.get("instructions", []):
        instruction = CookingInstruction(
            step_number=inst["step"],
            instruction=inst["text"],
        )
        recipe.cooking_instructions.append(instruction)

    # Categories
    for cat_name in data.get("categories", []):
        category = get_or_create_category(session, cat_name)
        recipe.categories.append(category)

    # Dietary tags
    for tag_slug in data.get("dietary_tags", []):
        tag = session.query(DietaryTag).filter_by(slug=tag_slug).first()
        if tag:
            recipe.dietary_tags.append(tag)

    # Allergens
    for allergen_name in data.get("allergens", []):
        allergen = session.query(Allergen).filter_by(name=allergen_name).first()
        if allergen:
            recipe.allergens.append(allergen)

    session.add(recipe)
    return recipe


def main():
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "recipes.db",
    )
    db_url = f"sqlite:///{db_path}"
    print(f"Connecting to: {db_url}")

    engine = get_engine(db_url)
    SessionFactory = get_session_factory(engine)

    with SessionFactory() as session:
        print(f"\nAdding {len(SUPER_PLATE_RECIPES)} Super Plate-style recipes...\n")
        for data in SUPER_PLATE_RECIPES:
            print(f"  + {data['name']}")
            recipe = insert_recipe(session, data)
            print(f"    id={recipe.id}, slug={recipe.slug}")
        session.commit()
        print("\nAll recipes committed!")

        # Summary
        total = session.query(Recipe).count()
        super_plates = session.query(Recipe).filter(
            Recipe.slug.like("pret-%") |
            Recipe.slug.like("leon-%") |
            Recipe.slug.like("itsu-%") |
            Recipe.slug.like("farmer-j-%") |
            Recipe.slug.like("korean-%") |
            Recipe.slug.like("salmon-%") |
            Recipe.slug.like("mediterranean-%") |
            Recipe.slug.like("miso-salmon-%")
        ).count()
        print(f"\nTotal recipes in DB: {total}")
        print(f"Super Plate-style recipes: {super_plates}")


if __name__ == "__main__":
    main()
