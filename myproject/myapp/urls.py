# /myproject/myapp/urls.py
from django.urls import path
from .views import (
    home, ProductListView, ProductDetailView, RentProductView
)

urlpatterns = [
    # Existing frontend URLs
    path('', home, name='home'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/rent/', RentProductView.as_view(), name='rent_product'),
]