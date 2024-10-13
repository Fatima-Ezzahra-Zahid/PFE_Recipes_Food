import random

from django.contrib.auth.hashers import make_password
from django.db import migrations
from faker import Faker


def populate_users(apps, schema_editor):
    # random user data
    User = apps.get_model('cooking', 'User')
    fake = Faker()

    for _ in range(10):
        email = fake.email()
        password = make_password('password')  # Use a fixed password for simplicity
        role = random.choice(['AD', 'CU'])  # Randomly choose between Admin and Customer

        User.objects.create(
            email=email,
            role=role,
            is_superuser=(role == 'AD'),  # Set is_superuser for Admins
            is_staff=(role == 'AD'),  # Set is_staff for Admins
            password=password
        )


def populate_dishes(apps, schema_editor):
    Dish = apps.get_model('cooking', 'Dish')
    fake = Faker()

    # List of example cuisine types (countries)
    cuisine_types = ['Italian', 'Chinese', 'Mexican', 'Indian', 'French', 'Japanese', 'Thai', 'Greek', 'Spanish',
                     'American', 'Moroccan']

    for _ in range(10):
        name = fake.word().capitalize()
        description = fake.text(max_nb_chars=200)
        cuisine_type = random.choice(cuisine_types)  # Choose a random cuisine type from the list
        image_url = fake.image_url()

        Dish.objects.create(
            name=name,
            description=description,
            cuisine_type=cuisine_type,
            image_url=image_url
        )


def populate_cuisine_categories(apps, schema_editor):
    CuisineCategory = apps.get_model('cooking', 'CuisineCategory')

    # List of example cuisine categories (types of food)
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Side Dish', 'Salad', 'Soup', 'Drink']

    for category_name in categories:
        CuisineCategory.objects.get_or_create(name=category_name)


def populate_dish_categories(apps, schema_editor):
    Dish = apps.get_model('cooking', 'Dish')
    CuisineCategory = apps.get_model('cooking', 'CuisineCategory')
    DishCategory = apps.get_model('cooking', 'DishCategory')

    # Retrieve all dishes and cuisine categories
    dishes = Dish.objects.all()
    categories = CuisineCategory.objects.all()

    # Example mapping of dishes to categories
    for dish in dishes:
        # Ensure that the number of categories is not zero to avoid IndexError
        if categories:
            # Choose a random category for the dish
            for category in categories:
                DishCategory.objects.get_or_create(
                    dish=dish,
                    category=category
                )


def populate_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('cooking', 'Ingredient')

    # List of example ingredients
    ingredients = [
        'Tomato', 'Onion', 'Garlic', 'Chicken', 'Beef', 'Carrot', 'Potato', 'Pepper', 'Salt', 'Olive Oil',
        'Butter', 'Cheese', 'Milk', 'Egg', 'Lettuce', 'Spinach', 'Garlic Powder', 'Cumin', 'Paprika', 'Soy Sauce'
    ]

    for ingredient_name in ingredients:
        Ingredient.objects.get_or_create(
            name=ingredient_name,
            description=''  # You can add default descriptions here if needed
        )


def populate_dish_ingredients(apps, schema_editor):
    Dish = apps.get_model('cooking', 'Dish')
    Ingredient = apps.get_model('cooking', 'Ingredient')
    DishIngredient = apps.get_model('cooking', 'DishIngredient')

    # Retrieve all dishes and ingredients
    dishes = Dish.objects.all()
    ingredients = Ingredient.objects.all()

    # Example mapping of dishes to ingredients with quantities
    for dish in dishes:
        for ingredient in ingredients:
            # Example quantities; adjust as needed
            quantity = '100g'  # Default quantity; adjust or generate as needed
            DishIngredient.objects.get_or_create(
                dish=dish,
                ingredient=ingredient,
                quantity=quantity
            )


# def populate_recipe_steps(apps, schema_editor):
#     Dish = apps.get_model('cooking', 'Dish')
#     RecipeStep = apps.get_model('cooking', 'RecipeStep')
#
#     # Example steps for each dish
#     steps = [
#         {
#             'dish_name': 'Spaghetti Bolognese',
#             'steps': [
#                 'Heat oil in a pan.',
#                 'Add chopped onions and garlic, and cook until softened.',
#                 'Add minced beef and cook until browned.',
#                 'Stir in tomato sauce and simmer for 20 minutes.',
#                 'Cook spaghetti according to package instructions.',
#                 'Serve the sauce over the spaghetti.'
#             ]
#         },
#         {
#             'dish_name': 'Chicken Curry',
#             'steps': [
#                 'Heat oil in a pan.',
#                 'Add chopped onions and cook until golden brown.',
#                 'Add chicken pieces and cook until no longer pink.',
#                 'Stir in curry powder and cook for a few minutes.',
#                 'Add coconut milk and simmer until the chicken is cooked through.',
#                 'Serve with rice.'
#             ]
#         },
#         # Add more dishes and steps as needed
#     ]
#
#     for dish_data in steps:
#         dish = Dish.objects.get(name=dish_data['dish_name'])
#         for i, instruction in enumerate(dish_data['steps'], start=1):
#             RecipeStep.objects.get_or_create(
#                 dish=dish,
#                 step_number=i,
#                 instruction=instruction
#             )


# def populate_dish_reviews(apps, schema_editor):
#     User = apps.get_model('cooking', 'User')
#     Dish = apps.get_model('cooking', 'Dish')
#     DishReview = apps.get_model('cooking', 'DishReview')
#
#     # Example reviews
#     reviews = [
#         {
#             'customer_email': 'user1@example.com',
#             'dish_name': 'Spaghetti Bolognese',
#             'rating': 5,
#             'review_text': 'Absolutely delicious! Will make it again.',
#         },
#         {
#             'customer_email': 'user2@example.com',
#             'dish_name': 'Chicken Curry',
#             'rating': 4,
#             'review_text': 'Great flavor, but a bit too spicy for my taste.',
#         },
#         # Add more reviews as needed
#     ]
#
#     for review_data in reviews:
#         user = User.objects.get(email=review_data['customer_email'])
#         dish = Dish.objects.get(name=review_data['dish_name'])
#         DishReview.objects.get_or_create(
#             customer=user,
#             dish=dish,
#             rating=review_data['rating'],
#             review_text=review_data['review_text']
#         )


class Migration(migrations.Migration):
    dependencies = [
        ('cooking', '0003_alter_user_managers_remove_dish_price'),
    ]
    operations = [
        migrations.RunPython(populate_users),
        migrations.RunPython(populate_dishes),
        migrations.RunPython(populate_cuisine_categories),
        migrations.RunPython(populate_dish_categories),
        migrations.RunPython(populate_ingredients),
        migrations.RunPython(populate_dish_ingredients),
        # migrations.RunPython(populate_recipe_steps),
        # migrations.RunPython(populate_dish_reviews),
    ]
