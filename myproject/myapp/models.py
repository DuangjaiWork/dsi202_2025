from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    monthly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_fee(self):
        if not self.start_date or not self.end_date:
            return self.product.monthly_rate  # Minimum 1 month if no end_date

        # Calculate the number of days between start_date and end_date
        days_diff = (self.end_date - self.start_date).days + 1  # Inclusive of end date
        # Calculate daily rate from monthly_rate (assuming 30 days per month)
        daily_rate = self.product.monthly_rate / Decimal('30')
        # Calculate total_fee based on number of days
        total_fee = daily_rate * Decimal(str(days_diff))

        return total_fee.quantize(Decimal('0.01'))  # Round to 2 decimal places

    def save(self, *args, **kwargs):
        self.total_fee = self.calculate_total_fee()
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