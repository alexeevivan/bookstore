from django.urls import path
from . import views
from .views import test_view, ProductDetailView, CategoryDetailView, CartView

# include base.html as a instrument to render the main.html file
urlpatterns = [
    path('', test_view, name='base'),
    path('<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),   
    path('about', views.info_about, name='about'),
    path('pricing', views.info_pricing, name='pricing'),
    path('library', views.info_library, name='library'),
    path('library/books_list', views.info_books_list, name='books_list'),
    path('cart/', CartView.as_view(), name='cart')
]

