from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from .models import Product, Rental, Category, Favorite, Cart
from django.db.models import Q, Sum
from .forms import RentalForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from .serializers import ProductSerializer
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'myapp/home.html')

# myapp/views.py (Update ProductListView)
class ProductListView(ListView):
    model = Product
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset().filter(stock__gt=0)  # Only show products with stock > 0
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        sort = self.request.GET.get('sort')

        # Search filter
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        # Category filter
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        # Sorting
        if sort == 'price_asc':
            queryset = queryset.order_by('monthly_rate')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-monthly_rate')
        else:
            queryset = queryset.order_by('-created_at')  # Default sort

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        # Add user's cart items to context
        if self.request.user.is_authenticated:
            context['user_cart'] = Cart.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            context['user_cart'] = []
        return context
    
# View to toggle favorite status
@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        favorite.delete()
        messages.success(request, f"{product.name} removed from favorites.")
    else:
        messages.success(request, f"{product.name} added to favorites.")
    
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

# View to display favorites
class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'myapp/favorite.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).order_by('-created_at')
    
# View to add/remove items from cart
@login_required
def toggle_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f"{product.name} added to cart.")
    else:
        cart_item.delete()
        messages.success(request, f"{product.name} removed from cart.")
    
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

# View to display cart
class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'myapp/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).order_by('-created_at')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/product_detail.html'
    context_object_name = 'product'

class RentProductView(LoginRequiredMixin, CreateView):
    model = Rental
    form_class = RentalForm
    template_name = 'myapp/rent_product.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = Product.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(stock__gt=0)
    serializer_class = ProductSerializer

class ProductRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def dashboard(request):
    total_products = Product.objects.count()
    available_products = Product.objects.filter(is_available=True).count()
    unavailable_products = total_products - available_products
    total_rentals = Rental.objects.count()
    total_revenue = Rental.objects.filter(end_date__isnull=False).aggregate(total=Sum('total_fee'))['total'] or 0.00
    recent_rentals = Rental.objects.order_by('-start_date')[:5]
    total_stock = Product.objects.aggregate(total=Sum('stock'))['total'] or 0
    category_count = Category.objects.count()

    context = {
        'total_products': total_products,
        'available_products': available_products,
        'unavailable_products': unavailable_products,
        'total_rentals': total_rentals,
        'total_revenue': total_revenue,
        'recent_rentals': recent_rentals,
        'total_stock': total_stock,
        'category_count': category_count,
    }
    return render(request, 'myapp/dashboard.html', context)