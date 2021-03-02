from django.urls import path
from . import views
from .views import (
    test_view, 
    ProductDetailView, CategoryDetailView, 
    CartView, AddToCartView, RemoveFromCartView, ChangeQuantityView, ConfirmationView,
    info_about, info_pricing, info_library, info_books_list, 
    info_biography
)

# include base.html as a instrument to render the main.html file
urlpatterns = [
    path('', test_view, name='base'),
    path('<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('library/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),   
    path('about', views.info_about, name='about'),
    path('pricing', views.info_pricing, name='pricing'),
    path('library', views.info_library, name='library'),
    path('library/books_list', views.info_books_list, name='books_list'),
    path('library/biography', views.info_biography, name='biography'),
    path('library/economics', views.info_economics, name='economics'),
    path('library/history', views.info_history, name='history'),
    path('library/medicine', views.info_medicine, name='medicine'),
    path('library/novel', views.info_novel, name='novel'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add_to_cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove_from_cart/<str:ct_model>/<str:slug>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('change_quantity/<str:ct_model>/<str:slug>/', ChangeQuantityView.as_view(), name='change_quantity'),
    path('confirmation/', ConfirmationView.as_view(), name='confirmation')
]

