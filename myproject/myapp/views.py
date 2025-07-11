from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from .models import Product, Rental, Category, Favorite, Cart, UserProfile, Donation, Review, ReviewLike
from django.db.models import Q, Sum
from .forms import RentalForm, UserProfileForm, DonationForm, ReviewForm, ReportForm, TransferSlipForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from .serializers import ProductSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

def home(request):
    return render(request, 'myapp/home.html')

class ProductListView(ListView):
    model = Product
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset().filter(stock__gt=0)
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        sort = self.request.GET.get('sort')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if sort == 'price_asc':
            queryset = queryset.order_by('monthly_rate')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-monthly_rate')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        if self.request.user.is_authenticated:
            context['user_cart'] = Cart.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            context['user_favorites'] = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            context['user_cart'] = []
            context['user_favorites'] = []
        return context

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

class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'myapp/favorite.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).order_by('-created_at')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_favorites'] = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            context['user_cart'] = Cart.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            context['review_form'] = ReviewForm()
            context['user_likes'] = ReviewLike.objects.filter(user=self.request.user, review__product=self.object).values_list('review_id', flat=True)
        else:
            context['user_favorites'] = []
            context['user_cart'] = []
            context['review_form'] = None
            context['user_likes'] = []
        context['reviews'] = self.object.reviews.all()
        return context

class RentProductView(LoginRequiredMixin, CreateView):
    model = Rental
    form_class = RentalForm
    template_name = 'myapp/rent_product.html'
    success_url = reverse_lazy('user_profile')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = Product.objects.get(pk=self.kwargs['pk'])
        form.instance.rental_months = int(self.request.POST.get('rental_months'))
        messages.success(self.request, f"Rental for {form.instance.product.name} confirmed!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context

@login_required
def mark_payment(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if rental.status == 'ongoing':
        rental.last_payment_reminder = timezone.now()
        rental.save()
        messages.success(request, "Payment recorded. Reminder reset.")
    return redirect('user_profile')

@login_required
def payment(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if rental.status not in ['preparing', 'ongoing']:
        messages.error(request, "Payment is not available for this rental status.")
        return redirect('user_profile')

    if request.method == 'POST':
        form = TransferSlipForm(request.POST, request.FILES, instance=rental)
        if form.is_valid():
            form.save()
            rental.last_payment_reminder = timezone.now()
            messages.success(request, "Transfer slip uploaded successfully. Awaiting admin verification.")
            return redirect('user_profile')
    else:
        form = TransferSlipForm(instance=rental)

    return render(request, 'myapp/payment.html', {
        'rental': rental,
        'form': form,
        'one_month_fee': rental.get_one_month_fee(),
    })

@login_required
def post_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Review posted successfully!")
            return redirect('product_detail', pk=product_id)
    return redirect('product_detail', pk=product_id)

@login_required
def toggle_review_like(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    like, created = ReviewLike.objects.get_or_create(user=request.user, review=review)
    
    if not created:
        like.delete()
        messages.success(request, "Like removed.")
    else:
        messages.success(request, "Like added!")
    
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(stock__gt=0)
    serializer_class = ProductSerializer

class ProductRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@login_required
def user_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('user_profile')

        if user_profile.user_type == 'donater':
            donation_form = DonationForm(request.POST, request.FILES)
            if donation_form.is_valid():
                donation = donation_form.save(commit=False)
                donation.user = request.user
                donation.save()
                messages.success(request, "Donation submitted successfully.")
                return redirect('user_profile')
        else:
            donation_form = DonationForm()
    else:
        profile_form = UserProfileForm(instance=user_profile)
        donation_form = DonationForm() if user_profile.user_type == 'donater' else None

    context = {
        'profile_form': profile_form,
        'donation_form': donation_form,
        'user_profile': user_profile,
        'rentals': Rental.objects.filter(user=request.user, status__in=['preparing', 'ongoing', 'returning']) if user_profile.user_type == 'renter' else [],
        'donations': Donation.objects.filter(user=request.user).order_by('-created_at') if user_profile.user_type == 'donater' else [],
    }
    return render(request, 'myapp/user.html', context)

@login_required
def submit_review(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    product = rental.product

    if Review.objects.filter(user=request.user, product=product).exists():
        messages.error(request, "You have already reviewed this product.")
        return redirect('product_detail', pk=product.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Review posted successfully!")
            return redirect('product_detail', pk=product.id)
    else:
        form = ReviewForm()

    return render(request, 'myapp/submit_review.html', {
        'form': form,
        'product': product,
    })

@login_required
def submit_report(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.rental = rental
            report.save()
            messages.success(request, "Issue reported successfully!")
            return redirect('user_profile')
    else:
        form = ReportForm()

    return render(request, 'myapp/report.html', {
        'form': form,
        'rental': rental,
    })