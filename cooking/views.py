import spacy
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from cooking.forms import ContactForm
from cooking.models import CuisineCategory, DishCategory, RecipeStep, Contact

# Load the NLP model
nlp = spacy.load('en_core_web_sm')


# Create your views here.
def home(request):
    # Get the top 3 cuisine categories with the most dishes
    top_cuisines = CuisineCategory.objects.annotate(num_dishes=Count('dishcategory__dish')).order_by('-num_dishes')[:3]

    # Fetch the last 4 added dishes for each cuisine category
    dishes_by_category = {}
    for cuisine in top_cuisines:
        last_dishes = Dish.objects.filter(dishcategory__category=cuisine).order_by('-created_at')[:4]
        dishes_by_category[cuisine.id] = last_dishes

    # Fetch the last 12 dishes across all top cuisines for the "All Foods" tab
    all_dishes = Dish.objects.filter(dishcategory__category__in=top_cuisines).order_by('-created_at')[:12]

    context = {
        'top_cuisines': top_cuisines,
        'dishes_by_category': dishes_by_category,
        'all_dishes': all_dishes,
    }

    return render(request, 'cooking/home.html', context)


import requests
from django.conf import settings
from .models import Dish, Ingredient, DishIngredient


def extract_food_keywords(user_input):
    # Process user input using SpaCy NLP pipeline
    doc = nlp(user_input)
    food_keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]  # Extract nouns
    return food_keywords


def get_recipes_from_api(query):
    api_key = settings.SPOONACULAR_API_KEY  # Store your API key in settings for security
    url = f'https://api.spoonacular.com/recipes/complexSearch?query={query}&apiKey={api_key}&number=10'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    return []


def suggestion(request):
    dishes = []
    api_recipes = []  # To store recipes from Spoonacular API
    user_input = ""
    error_message = ""

    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        # Extract relevant food-related entities using SpaCy
        food_keywords = extract_food_keywords(user_input)

        # If food-related keywords are found, query the database for matching dishes or ingredients
        if food_keywords:
            # Start with dish name filter
            dishes = Dish.objects.filter(name__icontains=food_keywords[0])  # Start with the first keyword

            for keyword in food_keywords[1:]:
                dishes = dishes | Dish.objects.filter(name__icontains=keyword)

            # Now, filter dishes based on ingredients matching the keywords
            ingredients = Ingredient.objects.filter(name__icontains=food_keywords[0])
            for ingredient in ingredients:
                dish_ingredient_matches = DishIngredient.objects.filter(ingredient=ingredient)

                # Preload related dishes and ingredients to avoid multiple queries (N+1 issue)
                dish_ingredient_matches = dish_ingredient_matches.select_related('dish', 'ingredient')

                for match in dish_ingredient_matches:
                    dishes = dishes | Dish.objects.filter(id=match.dish.id)

            # Preload related data for dishes to avoid querying related objects in loops
            dishes = dishes.prefetch_related(
                'dishingredient_set__ingredient',
                'dishcategory_set__category'  # Preload dish categories (to avoid duplicate queries)
            )

            # Fetch matching recipes from Spoonacular API using the first keyword
            api_recipes = get_recipes_from_api(food_keywords[0])
            for keyword in food_keywords[1:]:
                api_recipes += get_recipes_from_api(keyword)

        # No matches found
        if not dishes and not api_recipes:
            error_message = "No matching recipes found. Try adjusting your input or using different keywords."

    context = {
        'dishes': dishes,
        'api_recipes': api_recipes,  # Send API recipes to the template
        'user_input': user_input,
        'error_message': error_message,
    }
    return render(request, 'cooking/suggestion.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            message = form.cleaned_data['message']
            contact = Contact(full_name=full_name, email=email, phone_number=phone_number, message=message)
            contact.save()

            # Redirect to a success page or return a success message
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    context = {
        'form': form
    }

    return render(request, 'cooking/contact.html', context)


def shop(request):
    # Get the cooking time filter parameter from the GET request
    cooking_time_filter = request.GET.get('cooking_time_filter', '')
    category_filter = request.GET.get('category_filter', '')

    # Build the filter condition based on the selected cooking time range
    if cooking_time_filter == '0-30':
        cooking_time_condition = Q(cooking_time__gte=0, cooking_time__lte=30)
    elif cooking_time_filter == '30-60':
        cooking_time_condition = Q(cooking_time__gt=30, cooking_time__lte=60)
    elif cooking_time_filter == '60-120':
        cooking_time_condition = Q(cooking_time__gt=60, cooking_time__lte=120)
    elif cooking_time_filter == '120+':
        cooking_time_condition = Q(cooking_time__gt=120)
    else:
        cooking_time_condition = Q()  # No filter applied

    # Build the filter condition based on the selected category
    if category_filter:
        category_condition = Q(dishcategory__category__id=category_filter)
    else:
        category_condition = Q()  # No filter applied

    # Annotate each dish with the number of related RecipeStep objects
    dishes_list = Dish.objects.annotate(num_steps=Count('recipesteps')) \
        .filter(cooking_time_condition) \
        .filter(category_condition) \
        .prefetch_related('dishcategory_set__category') \
        .only('id', 'name', 'description', 'cuisine_type', 'image', 'cooking_time') \
        .order_by('-created_at')  # Default sorting by creation date

    paginator = Paginator(dishes_list, 12)  # Show 12 dishes per page
    page_number = request.GET.get('page')
    dishes = paginator.get_page(page_number)

    # Get categories for the filter dropdown
    categories = CuisineCategory.objects.all()

    context = {
        'dishes': dishes,
        'paginator': paginator,
        'categories': categories,  # Pass categories to the template
    }
    return render(request, 'cooking/recipes.html', context)


def recipes_details(request, pk):
    # Fetch the dish, or raise a 404 if it doesn't exist
    dish = get_object_or_404(Dish, pk=pk)

    # Get the related category (or categories if there are multiple)
    categories = DishCategory.objects.filter(dish=dish).select_related('category')

    # Get the related recipe steps
    recipe_steps = RecipeStep.objects.filter(dish=dish).order_by('step_number')

    # Get related dishes based on cuisine_type, excluding the current dish
    related_dishes = Dish.objects.filter(cuisine_type=dish.cuisine_type).exclude(pk=dish.pk)[:10]

    context = {
        'dish': dish,
        'categories': categories,
        'recipe_steps': recipe_steps,
        'related_dishes': related_dishes  # Pass related dishes to the template
    }
    return render(request, 'cooking/recipes-details.html', context)


# def do_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#
#         # Authenticate using email as username
#         user = authenticate(request, username=email, password=password)
#
#         if user is not None and user.role == 'AD':
#             if not user.is_active:
#                 messages.error(request, 'Your account is not validate.')
#                 return redirect('login')
#             auth_login(request, user)
#             messages.success(request, 'You have successfully logged in!')
#             return redirect('admin')  # Redirect to a dashboard or home page
#         else:
#             messages.error(request, 'Invalid email or password.')
#             return redirect('login')
#     else:
#         messages.error(request, 'Method not allowed.')
#         return redirect('dash/login')
def login(request):
    return render(request, 'cooking/login.html')
