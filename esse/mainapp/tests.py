from decimal import Decimal
from unittest import mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Category, Biography, CartProduct, Cart, Customer
from .views import recalc_cart, AddToCartView, test_view

User = get_user_model()

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)

class StoreTestCases(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser', password='password')
        self.category = Category.objects.create(name='Biography', slug='biographys')
        image = SimpleUploadedFile("small.gif", small_gif, content_type='img/gif')
        self.biography = Biography.objects.create(
            category=self.category,
            title="Test Biography",
            slug="test-slug",
            image=image,
            price=Decimal('50000.00'),
            authorship = ('I.A. Alexeev'),
            book_format = ('Hardcover'),
            publisher = ('Test Publishing House'),
            the_year_of_publishing = ('2021'),
            book_dimensions = ('777'),
            language = ('English'),
            appropriate_for_ages = ('All ages'),
            ISBN_13 = ('1234567897777')
        )
        self.customer = Customer.objects.create(user=self.user, phone="1111111", address="Address")
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer,
            cart=self.cart,
            content_object=self.biography
        )
    
    def test_add_to_cart(self):
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('50000.00'))
    
    def test_response_from_add_to_cart_view(self):
        factory = RequestFactory()
        request = factory.get('')
        request.user = self.user
        response = AddToCartView.as_view()(request, ct_model='biography', slug='test-slug')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cart/')
    