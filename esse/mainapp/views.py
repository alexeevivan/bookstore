from django.db import reset_queries
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.views.generic import DetailView, View
from django.http import HttpResponseRedirect

from .models import Biography, Economics, History, Medicine, Novel, Category, LatestProducts, Customer, Cart, CartProduct
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm



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
        self.cart.save()
        messages.add_message(request, messages.INFO, "Product added successfully")
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
        self.cart.save()
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
        self.cart.save()
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