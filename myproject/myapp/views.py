from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Product, Rental
from django.db.models import Q, Sum
from .forms import RentalForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import generics
from .serializers import ProductSerializer

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
    form_class = RentalForm
    template_name = 'myapp/rent_product.html'
    success_url = reverse_lazy('product_list')  # Redirect after successful rental

    def form_valid(self, form):
        # Set the user and bike before saving
        form.instance.user = self.request.user
        form.instance.product = Product.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context
    
# New API Views
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def dashboard(request):
    # Product statistics
    total_products = Product.objects.count()
    available_products = Product.objects.filter(is_available=True).count()
    unavailable_products = total_products - available_products

    # Rental statistics
    total_rentals = Rental.objects.count()
    total_revenue = Rental.objects.filter(end_date__isnull=False).aggregate(total=Sum('total_fee'))['total'] or 0.00
    recent_rentals = Rental.objects.order_by('-start_date')[:5]

    context = {
        'total_products': total_products,
        'available_products': available_products,
        'unavailable_products': unavailable_products,
        'total_rentals': total_rentals,
        'total_revenue': total_revenue,
        'recent_rentals': recent_rentals,
    }
    return render(request, 'myapp/dashboard.html', context)