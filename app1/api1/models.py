from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, viewsets, permissions


# Custom User Manager
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Обычный пользователь'),
        ('operator', 'Оператор'),
        ('curator', 'Куратор'),
        ('master', 'Мастер'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"


# Order Model
class Order(models.Model):
    STATUS_CHOICES = (
        ('новый', 'Новый'),
        ('в обработке', 'В обработке'),
        ('назначен', 'Назначен мастеру'),
        ('выполняется', 'Выполняется'),
        ('завершен', 'Завершен'),
    )

    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='новый')

    # Operator who processes the order
    operator = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # Prevent deletion failure
        limit_choices_to={'role': 'operator'},
        related_name='processed_orders'
    )

    # Curator who assigns the order
    curator = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # Prevent deletion failure
        limit_choices_to={'role': 'curator'},
        related_name='assigned_orders'
    )

    # Master who performs the order
    assigned_master = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # Prevent deletion failure
        limit_choices_to={'role': 'master'},
        related_name='orders'
    )

    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.client_name} ({self.status})"



class IsCurator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'curator'

class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'operator'

class IsMaster(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'master'



