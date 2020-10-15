from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder, searchItem, serializeContext, serializeItems, serializeOrder
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import (
    ListView
)


# Create your views here.
class Home(ListView):
    model = Product
    template_name = 'main/home.html'
    paginate_by = 9
    search = None
    ordering = 'price'
    content_type = 'application/json'

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        return render(self.request, self.template_name, {'context': context})

    def get_context_data(self, *args, **kwargs):
        context = super(Home, self).get_context_data(*args, **kwargs)
        data = cartData(self.request)
        self.search, searchURL = searchItem(self.request, self.search)
        if self.search:
            p = Paginator(Product.objects.filter(name__icontains=self.search).all().order_by(self.ordering), self.paginate_by)
        else:
            p = Paginator(Product.objects.all().order_by(self.ordering), self.paginate_by)
        context['title'] = 'Home'
        context['products'] = p.page(context['page_obj'].number)
        context['categories'] = Categories.objects.all()
        context['cartItems'] = data['cartItems']
        context['carousels'] = CarouselSlider.objects.all()
        context = serializeContext(context)
        json_context = json.dumps(context, cls=DjangoJSONEncoder)
        return json_context


class CategoryView(ListView):
    model = Product
    template_name = 'main/category.html'
    paginate_by = 9
    search = None
    ordering = 'price'

    def get_ordering(self):
        if self.request.method == 'GET':
            if self.request.GET.get('sort_options'):
                self.ordering = self.request.GET.get('sort_options')
        return self.ordering

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryView, self).get_context_data(*args, **kwargs)
        category = get_object_or_404(Categories, category=self.kwargs.get('category'))
        filtered = Product.objects.filter(categories=category).order_by(self.ordering)
        self.search, searchURL = searchItem(self.request, self.search)
        if self.search:
            p = Paginator(filtered.filter(name__icontains=self.search).all().order_by(self.ordering), self.paginate_by)
        else:
            p = Paginator(filtered.order_by(self.ordering), self.paginate_by)
        data = cartData(self.request)
        context['title'] = category.category
        context['products'] = p.page(context['page_obj'].number)
        context['categories'] = Categories.objects.all()
        context['cartItems'] = data['cartItems']
        context['carousels'] = CarouselSlider.objects.all()
        context = serializeContext(context)
        return context


# def home(request):
#     data = cartData(request)
#     cartItems = data['cartItems']
#     products = Product.objects.all()
#     carousels = CarouselSlider.objects.all()
#     context = {'title': 'Home',
#     'products': products,
#     'cartItems': cartItems,
#     'carousels': carousels
#     }
#     return render(request, 'main/home.html', context)

def cart(request):
    search = None
    search, searchURL = searchItem(request, search)
    if search:
        return redirect(reverse('main-home') + searchURL)
    else:
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
    search = None
    search, searchURL = searchItem(request, search)
    if search:
        return redirect(reverse('main-home') + searchURL)
    else:
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
    search = None
    search, searchURL = searchItem(request, search)
    if search:
        return redirect(reverse('main-home') + searchURL)
    else:
        return render(request, 'main/about.html', {'title': 'About Us'})

def loginpage(request):
    search = None
    search, searchURL = searchItem(request, search)
    if search:
        return redirect(reverse('main-home') + searchURL)
    elif request.method == 'POST':
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
    search = None
    search, searchURL = searchItem(request, search)
    if search:
        return redirect(reverse('main-home') + searchURL)
    else:
        logout(request)
        return redirect('main-login')

def signup(request):
    search, searchURL = searchItem(request, search)
    if search:
        return redirect(reverse('main-home') + searchURL)
    else:
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

def updateItem(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        productID = data['productID']
        action = data['action']

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

        if orderItem.quantity <= 0:
            orderItem.delete()

    cartdata = cartData(request)
    cartItems = cartdata['cartItems']
    order = serializeOrder(cartdata['order'])
    items = json.dumps(serializeItems(cartdata['items']), cls=DjangoJSONEncoder)
    return JsonResponse({'result': 'Item was added', 'cartItems': cartItems, 'items': items, 'order': order}, safe=False)

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
