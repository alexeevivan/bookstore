from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.deletion import CASCADE
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class LatestProductsManager:
    
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return products


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProducts:
    
    objects = LatestProductsManager()


class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'Biography': 'biography__count',
        'Economics': 'economics__count',
        'History': 'history__count',
        'Medicine': 'medicine__count',
        'Novel': 'novel__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('biography', 'economics', 'history', 'medicine', 'novel')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data

# **************
#1 Category
#2 Product
#3 CartProduct
#4 Cart
#5 Order
# **************
#6 Customer
#7 Specification (author name and etc.)


class Category(models.Model):
    
    name = models.CharField(max_length=255, verbose_name='Name of category')
    # URL will display the place to go after selecting the main category (Books / Novels)
    slug = models.SlugField(unique=True)
    # как представить категории в админке (просто по названию категории)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):

    MIN_RESOLUTION = (400,400)
    MAX_RESOLUTION = (4000,4000)
    # 3145728 = 3 MB
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract=True
    
    # категория, к которой принадлежит товар (книга)
    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)
    # название продукта
    title = models.CharField(max_length=255, verbose_name='Book Title')
    # slugfield тоже должен быть, и будет он уникальным также
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Image')
    # описание книги. null = True означает, что есть возможность не предоставлять описание книги
    description = models.TextField(verbose_name='Annotation', null = True)
    # max_digits показывает макс. кол-во цифр в стоимости продукта, а decimal_places - кол-во цифр после запятой
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise MinResolutionErrorException('Uploaded image size does not match the specified requirements!')
        if img.height > max_height or img.width > max_width:
            raise MaxResolutionErrorException('Uploaded image size does not match the specified requirements!')
        super().save(*args, **kwargs)

    def get_model_name(self):
        return self.__class__.__name__.lower()


class CartProduct(models.Model):

    # user who will own the item
    user = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)
    # cart
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    # shows all created product models in the admin area
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.PositiveIntegerField()
    # creates the relationship of the created product to the cart
    content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total cost')

    def __str(self):
        return "Product: {}".format(self.content_object.title)
    
    def save(self, *args, **kwargs):
        self.final_price = self.quantity * self.content_object.price
        super().save(*args, **kwargs)

    
class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Owner', on_delete=CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Total cost')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='User', on_delete=CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Phone number', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Address', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Customer orders', related_name='related_customer')

    def __str__(self):
        return "Customer: {} {}".format(self.user.first_name, self.user.last_name)


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    PURCHASE_TYPE_SELF = 'self'
    PURCHASE_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'New order'),
        (STATUS_IN_PROGRESS, 'Order in progress'),
        (STATUS_READY, 'Order is ready'),
        (STATUS_COMPLETED, 'Order is completed')
    )

    PURCHASE_TYPE_CHOICES = (
        (PURCHASE_TYPE_SELF, 'Self-pickup'),
        (PURCHASE_TYPE_DELIVERY, 'Delivery')
    )

    customer = models.ForeignKey(Customer, verbose_name='Customer', related_name='related_orders', on_delete=CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='First name')
    last_name = models.CharField(max_length=255, verbose_name='Last name')
    phone = models.CharField(max_length=20, verbose_name='Phone number')
    cart = models.ForeignKey(Cart, verbose_name='Cart', on_delete=CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Address', null=True, blank=True)
    status = models.CharField(
        max_length=100, 
        verbose_name='Order status', 
        choices=STATUS_CHOICES, 
        default=STATUS_NEW
    )
    purchase_type = models.CharField(
        max_length=100, 
        verbose_name='Purchase type',
        choices=PURCHASE_TYPE_CHOICES,
        default=PURCHASE_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Comment form', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Order creating date')
    order_date = models.DateField(verbose_name='Order processing date', default=timezone.now)

    def __str__(self):
        return str(self.id)


class Biography(Product):
    
    authorship = models.CharField(max_length=255, verbose_name='Author:')
    book_format = models.CharField(max_length=255, verbose_name='Format:', null=False, blank=False)
    publisher = models.CharField(max_length=255, verbose_name='Publisher:')
    the_year_of_publishing = models.CharField(max_length=10, verbose_name='Published:')
    book_dimensions = models.CharField(max_length=10, verbose_name='Quantity of pages:')
    language = models.CharField(max_length=40, verbose_name='Language:')
    appropriate_for_ages = models.CharField(max_length=10, verbose_name='Appropriate for ages:')
    ISBN_13 = models.CharField(max_length=13, verbose_name='International Standard Book Number:')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')    


class Economics(Product):

    authorship = models.CharField(max_length=255, verbose_name='Author:')
    book_format = models.CharField(max_length=255, verbose_name='Format:', null=False, blank=False)
    theme = models.CharField(max_length=255, verbose_name='Topic under consideration:')
    publisher = models.CharField(max_length=255, verbose_name='Publisher:')
    the_year_of_publishing = models.CharField(max_length=10, verbose_name='Published:')
    book_dimensions = models.CharField(max_length=10, verbose_name='Quantity of pages:')
    language = models.CharField(max_length=40, verbose_name='Language:')
    appropriate_for_ages = models.CharField(max_length=10, verbose_name='Appropriate for ages:')
    ISBN_13 = models.CharField(max_length=13, verbose_name='International Standard Book Number:')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')
    

class History(Product):

    authorship = models.CharField(max_length=255, verbose_name='Author:')
    book_format = models.CharField(max_length=255, verbose_name='Format:', null=False, blank=False)
    period = models.CharField(max_length=255, verbose_name='Сovers the period of time:')
    publisher = models.CharField(max_length=255, verbose_name='Publisher:')
    the_year_of_publishing = models.CharField(max_length=10, verbose_name='Published:')
    book_dimensions = models.CharField(max_length=10, verbose_name='Quantity of pages:')
    language = models.CharField(max_length=40, verbose_name='Language:')
    appropriate_for_ages = models.CharField(max_length=10, verbose_name='Appropriate for ages:')
    ISBN_13 = models.CharField(max_length=13, verbose_name='International Standard Book Number:')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)
    
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Medicine(Product):
    
    authorship = models.CharField(max_length=255, verbose_name='Author:')
    book_format = models.CharField(max_length=255, verbose_name='Format:', null=False, blank=False)
    theme = models.CharField(max_length=255, verbose_name='Part of science:')    
    publisher = models.CharField(max_length=255, verbose_name='Publisher:')
    the_year_of_publishing = models.CharField(max_length=10, verbose_name='Published:')
    book_dimensions = models.CharField(max_length=10, verbose_name='Quantity of pages:')
    language = models.CharField(max_length=40, verbose_name='Language:')
    appropriate_for_ages = models.CharField(max_length=10, verbose_name='Appropriate for ages:')
    ISBN_13 = models.CharField(max_length=13, verbose_name='International Standard Book Number:')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)
    
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Novel(Product):
    
    authorship = models.CharField(max_length=255, verbose_name='Author:')
    book_format = models.CharField(max_length=255, verbose_name='Format:', null=False, blank=False)
    publisher = models.CharField(max_length=255, verbose_name='Publisher:')
    the_year_of_publishing = models.CharField(max_length=10, verbose_name='Published:')
    book_dimensions = models.CharField(max_length=10, verbose_name='Quantity of pages:')
    language = models.CharField(max_length=40, verbose_name='Language:')
    appropriate_for_ages = models.CharField(max_length=10, verbose_name='Appropriate for ages:')
    ISBN_13 = models.CharField(max_length=13, verbose_name='International Standard Book Number:')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)
    
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')