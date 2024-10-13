from django.urls import path

from cooking import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('suggestion/', views.suggestion, name='suggestion'),
    path('recipes/', views.shop, name='recipes'),
    path('recipes/<int:pk>/', views.recipes_details, name='recipes-details'),
    path('login/', views.login, name='login'),
]