from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder, serializeContext, serializeItems, serializeOrder, getCookieItem
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import (
    ListView
)


# Create your views here.
class Home(ListView):
    model = Product
    template_name = 'main/home.html'
    ordering = 'price'

    def get_ordering(self):
        self.ordering = self.request.GET.get('ordering', self.ordering)
        return self.ordering

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        
        query = self.request.GET.get('q', None)
        if query is not None:
            queryset = Product.objects.search(queryset, query)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(Home, self).get_context_data(*args, **kwargs)
        data = cartData(self.request)
        context['title'] = 'Home'
        context['products'] = context['object_list']
        context['categories'] = Categories.objects.all()
        context['cartItems'] = data['cartItems']
        context['carousels'] = CarouselSlider.objects.all()
        context['orderings'] = {'price': 'Price: Low to High', '-price': 'Price: High to Low', 'name': 'Alphabetically: A to Z', '-name': 'Alphabetically: Z to A'}
        return context


class CategoryView(ListView):
    model = Product
    template_name = 'main/home.html'
    paginate_by = 9
    ordering = 'price'

    def get_ordering(self):
        self.ordering = self.request.GET.get('ordering', self.ordering)
        return self.ordering

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        category = self.kwargs.get('category', None)
        query = self.request.GET.get('q', None)
        if category is not None:
            queryset = queryset.filter(categories__category=category)
        if query is not None:
            queryset = Product.objects.search(queryset, query)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryView, self).get_context_data(*args, **kwargs)
        data = cartData(self.request)
        context['title'] = self.kwargs.get('category')
        context['products'] = context['paginator'].page(context['page_obj'].number)
        context['categories'] = Categories.objects.all()
        context['cartItems'] = data['cartItems']
        context['carousels'] = CarouselSlider.objects.all()
        context['orderings'] = {'price': 'Price: Low to High', '-price': 'Price: High to Low', 'name': 'Alphabetically: A to Z', '-name': 'Alphabetically: Z to A'}
        return context

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'title': 'Cart',
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
    return render(request, 'main/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {
        'title': 'Checkout',
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
    return render(request, 'main/checkout.html', context)

def about(request):
    return render(request, 'main/about.html', {'title': 'About Us'})

def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main-home')
        else:
            messages.info(request, 'Username or password is incorrect')
    data = cartData(request)
    cartItems = data['cartItems']
    context = {
        'title': 'Log In',
        'cartItems': cartItems
    }
    return render(request, 'main/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('main-login')

def signup(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm (request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {user}')
            return redirect('main-login')

    data = cartData(request)
    cartItems = data['cartItems']
    context = {
        'title': 'Sign Up',
        'form': form,
        'cartItems': cartItems
        }
    return render(request, 'main/signup.html', context)

@ensure_csrf_cookie
def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']
    if request.user.is_authenticated:
        customer = request.user.customer
        product = Product.objects.get(id=productID)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        
        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1
        elif action == 'update-item':
            datavalue = data['datavalue']
            orderItem.quantity = int(datavalue)
        
        orderItem.save()
        orderItem

        if orderItem.quantity <= 0:
            orderItem.delete()
        cartTotal = order.get_cart_total
        itemTotal = orderItem.get_total
        itemQuantity = orderItem.quantity
        cartItems = order.get_cart_quantity()
    else:
        cookieData = getCookieItem(request, productID)
        cartTotal = cookieData['cartTotal']
        itemTotal = cookieData['itemTotal']
        itemQuantity = cookieData['itemQuantity']
        cartItems = cookieData['cartItems']
    return JsonResponse({'result': 'Item was added', 'cartTotal': cartTotal, 'itemTotal': itemTotal, 'itemQuantity': itemQuantity, 'cartItems': cartItems}, safe=False)

def processOrder(request):
    transaction_id = int(datetime.datetime.now().timestamp())
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address1=data['shipping']['address1'],
        address2=data['shipping']['address2'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse('Payment completed', safe=False)
