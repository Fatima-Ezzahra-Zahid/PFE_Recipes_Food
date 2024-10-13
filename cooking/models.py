from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # Set default username to email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    AD = 'AD'
    CU = 'CU'
    ROLES = [
        (AD, 'Admin'),
        (CU, 'Customer'),
    ]
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    role = models.CharField(max_length=2, choices=ROLES, default=CU)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Dish(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    cuisine_type = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='dish_pics/', blank=True, null=True)
    cooking_time = models.PositiveIntegerField(blank=True, null=True)  # Time in minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CuisineCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class DishCategory(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    category = models.ForeignKey(CuisineCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.dish.name} - {self.category.name}"


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ingredient_pics/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DishIngredient(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.dish.name} - {self.ingredient.name} ({self.quantity})"


class RecipeStep(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='recipesteps')
    step_number = models.IntegerField()
    instruction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number} for {self.dish.name}"


class DishReview(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Add validation in forms to limit rating 1-5
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.username} for {self.dish.name}"


class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255, null=True, blank=True)  # Optional field
    message = models.TextField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
