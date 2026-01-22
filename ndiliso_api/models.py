from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class Village(models.Model):
    
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.name})"




class User(AbstractUser):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=128)
    imageURL = models.URLField(max_length=200, blank=True, null=True)
    village = models.ForeignKey(
        Village,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



class Dependent(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dependents'
    )

    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    dob = models.DateField()
    imageURL = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"




class Funeral(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='funerals'
    )

    dependent = models.ForeignKey(
        Dependent,
        on_delete=models.CASCADE,
        related_name='funerals'
    )

    name = models.CharField(max_length=255)
    title = models.CharField(max_length=5)
    date = models.DateField()
    time = models.CharField(max_length=10)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Funeral for {self.name} on {self.date}"
