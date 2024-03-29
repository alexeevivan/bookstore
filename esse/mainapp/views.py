from django.db import transaction
from django.db import reset_queries
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic import DetailView, View, ListView
from django.http import HttpResponseRedirect

from itertools import chain


from .models import Biography, Economics, History, Medicine, Novel, Category, LatestProducts, Customer, Cart, CartProduct, Order, Product
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm, LoginForm, RegistrationForm
from .utils import recalc_cart



def test_view(request):
    return render(request, 'base.html', {})

def info_about(request):
    return render(request,'about.html', {})

def info_pricing(request):
    return render(request, 'pricing.html', {})

def info_library(request):
    return render(request, 'library.html', {})

def info_books_list(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    products = LatestProducts.objects.get_products_for_main_page(
        'biography', 'economics', 'history', 'medicine', 'novel', with_respect_to = 'biography'
    )
    return render(request, 'books_list.html', {'categories': categories, 'products': products})
    
def info_biography(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    products = LatestProducts.objects.get_products_for_main_page(
        'biography'
    )
    return render(request, 'biography.html', {'categories': categories, 'products': products})

def info_economics(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    products = LatestProducts.objects.get_products_for_main_page(
        'economics'
    )
    return render(request, 'economics.html', {'categories': categories, 'products': products})

def info_history(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    products = LatestProducts.objects.get_products_for_main_page(
        'history'
    )
    return render(request, 'history.html', {'categories': categories, 'products': products})

def info_medicine(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    products = LatestProducts.objects.get_products_for_main_page(
        'medicine'
    )
    return render(request, 'medicine.html', {'categories': categories, 'products': products})

def info_novel(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    products = LatestProducts.objects.get_products_for_main_page(
        'novel'
    )
    return render(request, 'novel.html', {'categories': categories, 'products': products})

# building a scheme, thats can help to show the url-address of each product
class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'biography': Biography,
        'economics': Economics,
        'history': History,
        'medicine': Medicine,
        'novel': Novel
    }

    def dispatch(self, request, *args, **kwargs):

        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        if created:
            self.cart.products.add(cart_product)
        #self.cart.save()
        recalc_cart(self.cart)
        #messages.add_message(request, messages.INFO, "Product added successfully")
        return HttpResponseRedirect('/cart/')


class RemoveFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Product removed successfully")
        return HttpResponseRedirect('/cart/')


class ChangeQuantityView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        quantity = int(request.POST.get('quantity'))
        cart_product.quantity = quantity
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Quantity changed successfully")
        return HttpResponseRedirect('/cart')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render (request, 'cart.html', context)


class ConfirmationView(CartMixin, View):
    
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render (request, 'confirmation.html', context)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.purchase_type = form.cleaned_data['purchase_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Thanks for order! Our Manager will call you in 10 minutes approximately.')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('confirmation')


class LoginView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        categories = Category.objects.all()
        context = {
            'form': form,
            'categories': categories,
            'cart': self.cart
        }
        return render(request, 'login.html', context)
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form,
            'cart': self.cart
        }
        return render(request, 'login.html', context)


class RegistrationView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        context = {
            'form': form,
            'categories': categories,
            'cart': self.cart
        }
        return render(request, 'registration.html', context)
    
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            'form': form,
            'cart': self.cart
            }
        return render(request, 'registration.html', context)


class ProfileView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
        categories = Category.objects.all()
        return render(
            request,
            'profile.html',
            {
                'orders': orders,
                'cart': self.cart,
                'categories':categories
            }
        )


class SearchResultsView(ListView):
    model = Biography, Economics, History,Medicine, Novel
    template_name = 'search_results.html'
    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list_1 = Biography.objects.filter(
            Q(title__icontains=query) | Q(ISBN_13__icontains=query) | Q(authorship__icontains=query) | Q(publisher__icontains=query)
        )
        object_list_2 = Economics.objects.filter(
            Q(title__icontains=query) | Q(ISBN_13__icontains=query) | Q(theme__icontains=query) | Q(publisher__icontains=query)
        )
        object_list_3 = History.objects.filter(
            Q(title__icontains=query) | Q(ISBN_13__icontains=query) | Q(period__icontains=query) | Q(publisher__icontains=query)
        )
        object_list_4 = Medicine.objects.filter(
            Q(title__icontains=query) | Q(ISBN_13__icontains=query) | Q(theme__icontains=query) | Q(publisher__icontains=query)
        )
        object_list_5 = Novel.objects.filter(
            Q(title__icontains=query) | Q(ISBN_13__icontains=query) | Q(publisher__icontains=query)
        )
        object_list = object_list_1, object_list_2, object_list_3, object_list_4, object_list_5
        return object_list_1 or object_list_2 or object_list_3 or object_list_4 or object_list_5