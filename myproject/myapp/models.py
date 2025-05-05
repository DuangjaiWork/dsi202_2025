from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    monthly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rents {self.product.name}"

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} donated {self.product_name}"
