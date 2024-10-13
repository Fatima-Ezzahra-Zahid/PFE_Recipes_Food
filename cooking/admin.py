from django.contrib import admin

from .models import User, Dish, CuisineCategory, DishCategory, Ingredient, DishIngredient, RecipeStep, DishReview

# Register your models here.
admin.site.register(User)
admin.site.register(Dish)
admin.site.register(CuisineCategory)
admin.site.register(DishCategory)
admin.site.register(Ingredient)
admin.site.register(DishIngredient)
admin.site.register(RecipeStep)
admin.site.register(DishReview)