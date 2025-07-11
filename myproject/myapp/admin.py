from django.contrib import admin
from .models import Product, Rental, Donation, Category, Favorite, Cart, UserProfile, Review, ReviewLike, Report

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'last_name', 'phone_number', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'name', 'last_name', 'phone_number')

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

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'start_date', 'rental_months', 'total_fee', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'start_date')
    search_fields = ('user__username', 'product__name')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('transfer_slip',)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_name', 'accepted', 'created_at', 'image')
    list_filter = ('accepted',)
    search_fields = ('user__username', 'product_name', 'description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'content')

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'review__content')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'rental', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'subject', 'description', 'rental__product__name')
    list_editable = ('status',)