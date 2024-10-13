from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.utils.timezone import now
from django.contrib.auth import authenticate, login as auth_login


from cooking.forms import UserUpdateForm
from cooking.models import Dish, User, Ingredient, CuisineCategory, Contact, RecipeStep, DishIngredient, DishCategory


# Create your views here.

def login(request):
    return render(request, 'dashboard/login.html')


@login_required(login_url='login')
def index(request):
    total_dishes = Dish.objects.count()
    total_users = User.objects.count()
    total_ingredients = Ingredient.objects.count()

    one_week_ago = now() - timedelta(days=7)
    recent_dishes = Dish.objects.filter(created_at__gte=one_week_ago).count()

    last_dishes = Dish.objects.all().order_by('-created_at')[:5]
    last_users = User.objects.all().order_by('-date_joined')[:5]

    context = {
        'total_dishes': total_dishes,
        'total_users': total_users,
        'total_ingredients': total_ingredients,
        'recent_dishes': recent_dishes,
        'last_dishes': last_dishes,
        'last_users': last_users,
    }

    return render(request, 'dashboard/index.html', context)


@login_required(login_url='login')
def log_out(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def users(request):
    users = User.objects.all().order_by('-date_joined')

    context = {
        'users': users
    }

    return render(request, 'dashboard/manage/users.html', context)


@login_required(login_url='login')
def add_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_repeat = request.POST.get('password_repeat')
        role = request.POST.get('role')

        # Validation
        if password != password_repeat:
            messages.error(request, "Passwords do not match.")
            return redirect('add_user')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('add_user')

        if username != '' and User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('add_user')

        # Create a new user
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=make_password(password),
            role=role
        )

        messages.success(request, f'{user.get_full_name()} added successfully.')
        return redirect('users')  # Replace with the URL for the user list page
    messages.error(request, 'Method is not allowed')
    return redirect('users')


def update_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)

        # Bind form with POST data
        form = UserUpdateForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.get_full_name()} updated successfully.')
        else:
            # If form is invalid, show error messages
            for error in form.errors.values():
                messages.error(request, error)

        return redirect('users')

    return redirect('users')


@login_required
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, "User deleted successfully!")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
    return redirect('users')


# Activate User
@login_required(login_url='login')
def activate_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, "User account activated successfully!")
        else:
            messages.warning(request, "User is already active.")
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")

    return redirect('users')  # Replace with your actual URL name


# Deactivate User
@login_required(login_url='login')
def deactivate_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if user.is_active:
            user.is_active = False
            user.save()
            messages.success(request, "User account deactivated successfully!")
        else:
            messages.warning(request, "User is already inactive.")
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")

    return redirect('users')  # Replace with your actual URL name


@login_required(login_url='login')
def dishes(request):
    dishes = Dish.objects.all().prefetch_related('dishcategory_set__category').order_by('-id')
    cuisine_categories = CuisineCategory.objects.all()  # Get all categories

    context = {
        'dishes': dishes,
        'cuisine_categories': cuisine_categories,  # Pass categories to the context
    }
    return render(request, 'dashboard/manage/dish/dishes.html', context)


@login_required(login_url='login')
@transaction.atomic  # Ensure that all operations are atomic
def add_dish(request):
    if request.method == 'POST':
        # Extracting form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        cuisine_type = request.POST.get('cuisine_type')
        cooking_time = request.POST.get('cooking_time')
        image = request.FILES.get('image')

        categories = request.POST.getlist('categories')  # List of category names
        ingredients = request.POST.getlist('ingredients')  # List of ingredient names
        steps = {key: value for key, value in request.POST.items() if key.startswith('new_step_instruction_')}

        try:
            # Wrap all operations in a transaction block
            with transaction.atomic():
                # Create the dish first
                dish = Dish.objects.create(
                    name=name,
                    description=description,
                    cuisine_type=cuisine_type,
                    cooking_time=cooking_time,
                    image=image
                )

                # Add categories
                for category_name in categories:
                    print(f"Processing category: {category_name}")  # Debug output
                    try:
                        category = CuisineCategory.objects.get(name=category_name)
                        DishCategory.objects.create(dish=dish, category=category)
                    except CuisineCategory.DoesNotExist:
                        messages.error(request, f"Category '{category_name}' does not exist.")
                        return redirect('add_dish')  # Reload the form if a category is missing

                # Add ingredients
                for ingredient_name in ingredients:
                    try:
                        ingredient = Ingredient.objects.get(name=ingredient_name)
                        DishIngredient.objects.create(dish=dish, ingredient=ingredient, quantity="to be added")  # Add actual quantity as needed
                    except Ingredient.DoesNotExist:
                        messages.error(request, f"Ingredient '{ingredient_name}' does not exist.")
                        return redirect('add_dish')  # Reload the form if an ingredient is missing

                # Add recipe steps
                for index, instruction in enumerate(steps.values(), start=1):
                    RecipeStep.objects.create(dish=dish, step_number=index, instruction=instruction)

            # If everything is successful, show success message and redirect
            messages.success(request, f'Dish "{dish.name}" added successfully!')
            return redirect('dishes')  # Redirect to the dish listing page

        except Exception as e:
            # If any error occurs, the transaction will be rolled back
            messages.error(request, f"Error adding dish: {str(e)}")
            return redirect('add_dish')  # Reload the form if something goes wrong

    # If it's a GET request or a form reload, load categories and ingredients
    categories = CuisineCategory.objects.all()
    ingredients = Ingredient.objects.all()

    context = {
        'ingredients': ingredients,
        'categories': categories,
    }
    return render(request, 'dashboard/manage/dish/add_dish.html', context)  # Ensure the template name is correct



@login_required(login_url='login')
def dish_details(request, dish_id):
    dish = get_object_or_404(Dish, pk=dish_id)
    steps = RecipeStep.objects.filter(dish_id=dish_id)
    categories = CuisineCategory.objects.filter(dishcategory__dish_id=dish_id)
    ingredients = Ingredient.objects.filter(dishingredient__dish_id=dish_id)

    context = {
        'dish': dish,
        'ingredients': ingredients,
        'categories': categories,
        'steps': steps,
    }
    return render(request, 'dashboard/manage/dish/dish-details.html', context)


@login_required(login_url='login')
def update_dish(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        description = request.POST.get('description')
        cuisine_type = request.POST.get('cuisine_type')
        cooking_time = request.POST.get('cooking_time')
        image = request.FILES.get('image')  # Handle image upload

        # Update the dish instance
        dish.name = name
        dish.description = description
        dish.cuisine_type = cuisine_type
        dish.cooking_time = cooking_time

        if image:  # Only update image if a new one is provided
            dish.image = image

        # Save the updated dish to the database
        dish.save()

        messages.success(request, "Dish updated successfully.")
        return redirect('update_dish', dish_id=dish.id)

    # If GET request, render the form with existing data
    ingredients = Ingredient.objects.all()
    categories = CuisineCategory.objects.all()
    dish_ingredients = DishIngredient.objects.filter(dish=dish)
    dish_categories = DishCategory.objects.filter(dish=dish)

    # Get current ingredient and category IDs
    dish_ingredient_ids = dish_ingredients.values_list('ingredient__id', flat=True)
    dish_category_ids = dish_categories.values_list('category__id', flat=True)

    context = {
        'dish': dish,
        'ingredients': ingredients,
        'categories': categories,
        'dish_ingredient_ids': dish_ingredient_ids,
        'dish_category_ids': dish_category_ids,
    }

    return render(request, 'dashboard/manage/dish/update_dish.html', context)


@login_required(login_url='login')
def update_dish_steps(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == 'POST':
        step_ids_to_keep = []

        # Process existing steps
        for key in request.POST.keys():
            if key.startswith('step_id_'):
                step_id = key.split('_')[2]  # Get step ID
                instruction = request.POST.get(f'step_instruction_{step_id}')

                if instruction:
                    step = RecipeStep.objects.get(id=step_id, dish=dish)
                    step.instruction = instruction
                    step.save()
                    step_ids_to_keep.append(step.id)

        # Remove steps that are not included in the form
        RecipeStep.objects.filter(dish=dish).exclude(id__in=step_ids_to_keep).delete()

        # Process new steps
        for key in request.POST.keys():
            if key.startswith('new_step_instruction_'):
                new_instruction = request.POST.get(key)
                if new_instruction:
                    RecipeStep.objects.create(dish=dish, step_number=dish.recipesteps.count() + 1,
                                              instruction=new_instruction)

        # **Renumber all steps**
        all_steps = RecipeStep.objects.filter(dish=dish).order_by('id')  # Order by ID to maintain creation order
        for idx, step in enumerate(all_steps, start=1):
            step.step_number = idx
            step.save()
        messages.success(request, "Steps updated successfully.")
        return redirect('update_dish', dish_id=dish.id)

    messages.error(request, "Invalid request method.")
    return redirect('update_dish', dish_id=dish.id)


@login_required(login_url='login')
def update_dish_categories(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == 'POST':
        # Get the selected category IDs from the form
        category_ids = request.POST.getlist('categories')

        if not category_ids:
            messages.error(request, "You must select at least one category.")
        else:
            # Clear the current categories for this dish
            DishCategory.objects.filter(dish=dish).delete()

            # Assign the new categories to the dish
            for category_id in category_ids:
                category = get_object_or_404(CuisineCategory, id=category_id)
                DishCategory.objects.create(dish=dish, category=category)

            messages.success(request, "Categories updated successfully.")

        return redirect('update_dish', dish_id=dish.id)

    return redirect('update_dish', dish_id=dish.id)


@login_required(login_url='login')
def update_dish_ingredients(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == 'POST':
        # Get the selected ingredient IDs from the form
        ingredient_ids = request.POST.getlist('ingredients')

        if len(ingredient_ids) == 0:
            # Validation error: no ingredients selected
            messages.error(request, "You must select at least one ingredient.")
            return redirect('update_dish', dish_id=dish.id)

        # Clear existing ingredients for the dish
        DishIngredient.objects.filter(dish=dish).delete()

        # Add the new ingredients
        for ingredient_id in ingredient_ids:
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            DishIngredient.objects.create(dish=dish, ingredient=ingredient, quantity="")  # Quantity not needed

        # Success message
        messages.success(request, "Ingredients updated successfully.")
        return redirect('update_dish', dish_id=dish.id)

    # Redirect if not POST
    messages.error(request, "Invalid request method.")
    return redirect('update_dish', dish_id=dish.id)


@login_required(login_url='login')
def delete_dish(request):
    if request.method == 'POST':
        dish_id = request.POST.get('id')
        dish = Dish.objects.get(id=dish_id)
        dish.delete()

        messages.success(request, f'{dish.name} deleted successfully.')
        return redirect('dishes')  # Redirect to the dishes page


@login_required(login_url='login')
def contact_messages(request):
    contact_messages = Contact.objects.all().order_by('-message')
    context = {
        'contact_messages': contact_messages
    }
    return render(request, 'dashboard/contact.html', context)


@login_required(login_url='login')
def mark_message_as_seen(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(Contact, id=message_id)
        message.seen = True
        message.save(update_fields=['seen'])  # Only update the 'seen' field
        messages.success(request, 'The messages has been viewed')
        return redirect('contact_messages')  # Redirect back to the message list


@login_required(login_url='login')
def categories(request):
    categories = CuisineCategory.objects.all().order_by('-id')
    context = {
        'categories': categories
    }
    return render(request, 'dashboard/manage/categories.html', context)


@login_required(login_url='login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category, created = CuisineCategory.objects.get_or_create(name=name)
            if created:
                messages.success(request, 'Category added successfully.')
            else:
                messages.error(request, 'Category already exists.')
        else:
            messages.error(request, 'Category name is required.')
    return redirect('categories')


@login_required(login_url='login')
def update_category(request, category_id):
    if request.method == 'POST':
        category = CuisineCategory.objects.get(id=category_id)
        new_name = request.POST.get('name')
        if new_name:
            category.name = new_name
            category.save()
            messages.success(request, 'Category updated successfully.')
        else:
            messages.error(request, 'Category name is required.')
    return redirect('categories')


@login_required(login_url='login')
def delete_category(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        print(category_id)  # Debugging: Print the category ID being received

        # Ensure that the ID is not empty
        if not category_id:
            return HttpResponseBadRequest("Invalid category ID")

        try:
            category = CuisineCategory.objects.get(id=category_id)
            category.delete()
            messages.success(request, 'Category Deleted successfully.')
            return redirect('categories')  # Redirect to the categories page after deletion
        except DishCategory.DoesNotExist:
            return HttpResponseNotFound("No DishCategory matches the given query.")


def ingredient_list(request):
    ingredients = Ingredient.objects.all().order_by('-id')
    return render(request, 'dashboard/manage/ingredients.html', {'ingredients': ingredients})


def add_ingredient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Handle image upload
        image = request.FILES.get('image')

        ingredient = Ingredient.objects.create(
            name=name,
            description=description,
            image=image
        )
        messages.success(request, 'Ingredient added successfully!')
        return redirect('ingredient_list')


def update_ingredient(request):
    if request.method == 'POST':
        ingredient_id = request.POST.get('ingredient_id')
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        ingredient.name = request.POST.get('name')
        ingredient.description = request.POST.get('description')

        # Handle image upload
        if 'image' in request.FILES:
            ingredient.image = request.FILES['image']

        ingredient.save()

        messages.success(request, 'Ingredient updated successfully!')
        return redirect('ingredient_list')


def delete_ingredient(request):
    if request.method == 'POST':
        ingredient_id = request.POST.get('ingredient_id')
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        ingredient.delete()
        messages.success(request, 'Ingredient deleted successfully!')
        return redirect('ingredient_list')

def do_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None and user.role == 'AD':
            if not user.is_active:
                messages.error(request, 'Your account is not validate.')
                return redirect('login')
            auth_login(request, user)
            messages.success(request, 'You have successfully logged in!')
            return redirect('admin')  # Redirect to a dashboard or home page
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('dashLogin')
    else:
        messages.error(request, 'Method not allowed.')
        return redirect('dashLogin')