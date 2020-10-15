from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image

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


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    categories = models.ManyToManyField(Categories, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    image = models.ImageField(default='strawberry.jpg', null=True, blank=True, upload_to='product_images')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image)
            print(self.image.width, self.image.height)
            scale = img.width/img.height
            if img.height > img.width:
                ratio = img.height/200
                height = img.height/ratio
                width = img.width/ratio
            elif img.width > img.height:
                if scale < 1.7:
                    ratio = img.height/200
                else:
                    ratio = img.width/340
                height = img.height/ratio
                width = img.width/ratio
            else:
                ratio = img.height/200
                height = img.height/ratio
                width = img.width/ratio
            output_size = (width, height)
            img.thumbnail(output_size)
            img.save(self.image.path)
            
    
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
    
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            ratio = img.height/400
            height = img.height/ratio
            width = img.width/ratio
            output_size = (width, height)
            img.thumbnail(output_size)
            img.save(self.image)
            super(CarouselSlider, self).save(*args, **kwargs)
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
