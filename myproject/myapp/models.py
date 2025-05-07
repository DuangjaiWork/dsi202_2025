from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    monthly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Update is_available based on stock
        self.is_available = self.stock > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField(default=now, null=True)
    end_date = models.DateField(null=True, blank=True)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_fee(self):
        if not self.start_date or not self.end_date:
            return self.product.monthly_rate
        days_diff = (self.end_date - self.start_date).days + 1
        daily_rate = self.product.monthly_rate / Decimal('30')
        total_fee = daily_rate * Decimal(str(days_diff))
        return total_fee.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        self.total_fee = self.calculate_total_fee()
        # Decrease stock when a rental is created
        if not self.pk and self.product.stock > 0:  # Only for new rentals
            self.product.stock -= 1
            self.product.save()  # Calls Product.save() to update is_available
        # Increase stock when rental is marked as returned
        if self.pk and self.returned and not Rental.objects.get(pk=self.pk).returned:
            self.product.stock += 1
            self.product.save()  # Calls Product.save() to update is_available
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} donated {self.product_name}"