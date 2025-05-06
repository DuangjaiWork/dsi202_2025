# /myproject/myapp/urls.py
from django.urls import path
from .views import (
    home, ProductListView, ProductDetailView, RentProductView, ProductListCreateAPIView, ProductRetrieveUpdateAPIView, dashboard
)

urlpatterns = [
    # Existing frontend URLs
    path('', home, name='home'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/rent/', RentProductView.as_view(), name='rent_product'),
    path('dashboard/', dashboard, name='dashboard'),
    path('api/products/', ProductListCreateAPIView.as_view(), name='product_api_list_create'),
    path('api/products/<int:pk>/', ProductRetrieveUpdateAPIView.as_view(), name='product_api_retrieve_update'),
]