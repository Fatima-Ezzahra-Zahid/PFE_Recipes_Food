from django.urls import path

from . import views

urlpatterns = [
    path('dash/login', views.login, name='dashLogin'),
    path('dash/do_login', views.do_login, name='do_login'),
    path('admin/', views.index, name='admin'),

    # users paths
    path('users/', views.users, name='users'),
    path('add-user/', views.add_user, name='add_user'),
    path('update-user/', views.update_user, name='update_user'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),

    # dishes
    path('dishes/', views.dishes, name="dishes"),
    path('dishes/new/', views.add_dish, name="add_dish"),
    path('dishes/<int:dish_id>/', views.dish_details, name="dish_details"),
    path('dishes/update/<int:dish_id>/', views.update_dish, name="update_dish"),
    path('dish/<int:dish_id>/update-ingredients/', views.update_dish_ingredients, name='update_dish_ingredients'),
    path('dish/<int:dish_id>/update_categories/', views.update_dish_categories, name='update_dish_categories'),
    path('dish/<int:dish_id>/update-steps/', views.update_dish_steps, name='update_dish_steps'),
    path('delete-dish/', views.delete_dish, name="delete_dish"),

    path('categories/', views.categories, name="categories"),
    path('add-category/', views.add_category, name='add_category'),
    path('delete-category/', views.delete_category, name='delete_category'),
    path('update-category/<int:category_id>/', views.update_category, name='update_category'),

    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('add-ingredient/', views.add_ingredient, name='add_ingredient'),
    path('update-ingredient/', views.update_ingredient, name='update_ingredient'),
    path('delete-ingredient/', views.delete_ingredient, name='delete_ingredient'),

    path('contact-messages/', views.contact_messages, name='contact_messages'),
    path('mark-message-as-seen/<int:message_id>/', views.mark_message_as_seen, name='mark_message_as_seen'),

    path('log_out/', views.log_out, name='log_out'),
]
