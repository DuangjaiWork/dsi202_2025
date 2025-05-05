from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Product, Rental
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# Home Page (FBV)
def home(request):
    return render(request, 'myapp/home.html')

#  (CBV)
class ProductListView(ListView):
    model = Product
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'  # Name of the variable in the template
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-monthly_rate')  # Get the default queryset (all bikes)
        query = self.request.GET.get('q')  # Get the search term from the URL (e.g., ?q=mountain)
        if query:
            # Filter bikes where name or description contains the query (case-insensitive)
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset

# Product Detail (CBV: DetailView)
class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/product_detail.html'
    context_object_name = 'product'  # Name of the variable in the template

class RentProductView(LoginRequiredMixin, CreateView):
    model = Rental
    template_name = 'myapp/rent_product.html'
    success_url = reverse_lazy('product_list')  # Redirect after successful rental