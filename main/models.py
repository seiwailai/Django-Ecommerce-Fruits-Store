from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Categories(models.Model):
    category = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.category


class ProductManager(models.Manager):
    def search(self, qs, query=None):
        qs = qs
        if query is not None:
            or_lookup = (models.Q(name__icontains=query) | 
                         models.Q(description__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    categories = models.ManyToManyField(Categories, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to='product_images')
    objects = ProductManager()

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(default=timezone.now)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        return sum([item.get_total for item in orderitems])
    
    def get_cart_quantity(self):
        orderitems = self.orderitem_set.all()
        return sum([item.quantity for item in orderitems])

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.product.name + ' on ' + str(self.date_added)


    @property
    def get_total(self):
        return self.product.price * self.quantity

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address1 = models.CharField(max_length=200, null=True)
    address2 = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.IntegerField(null=True)

    def __str__(self):
        return self.address1


class CarouselSlider(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(null=True, blank=True, upload_to='carousel_slides')

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
