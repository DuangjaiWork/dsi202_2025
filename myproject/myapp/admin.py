from django.contrib import admin
from .models import Product, Rental, Donation

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available', 'monthly_rate', 'image', 'created_at')
    list_filter = ('is_available',)
    search_fields = ('name', 'description')

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'start_date', 'end_date', 'total_fee', 'returned', 'created_at')
    list_filter = ('returned', 'start_date', 'end_date')
    search_fields = ('user__username', 'product__name')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'product_name', 'accepted', 'created_at')
    list_filter = ('accepted',)
    search_fields = ('donor__username', 'product_name', 'description')