from django.contrib import admin
from .models import Product, Rental, Donation, Category, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available', 'monthly_rate', 'stock', 'category', 'image')
    list_filter = ('is_available', 'category')
    search_fields = ('name', 'description')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')

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