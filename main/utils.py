from .models import *
import json
from django.db.models.query import QuerySet
from django.db.models import Model
import logging
import boto3
from botocore.exceptions import ClientError

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def getCookieItem(request, productID):
    try:
        cart = json.loads(request.COOKIES['cart'])
        itemQuantity = cart[productID]['quantity']
        itemTotal = Product.objects.get(id=productID).price * itemQuantity
        cartTotal = 0
        cartItems = 0
        for i in cart:
            product = Product.objects.get(id=i)
            cartTotal += cart[i]['quantity'] * product.price
            cartItems += cart[i]['quantity']
        return {'itemQuantity': itemQuantity, 'itemTotal': itemTotal, 'cartTotal': cartTotal, 'cartItems': cartItems}
    except:
        cart = {}
        return {'itemQuantity': 0, 'itemTotal': 0, 'cartTotal': 0, 'cartItems': 0}


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    order = {
        'get_cart_total': 0,
        'get_cart_quantity': 0,
    }
    cartItems = order['get_cart_quantity']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']

            order['get_cart_total'] += total
            order['get_cart_quantity'] += cart[i]['quantity']

            item = {
                'product': product,
                'quantity': cart[i]['quantity'],
                'get_total': total
                }

            items.append(item)
        except:
            pass
    return {
        'cartItems': cartItems,
        'items': items,
        'order': order
    }

def cartData(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(email=request.user.email)
        if created:
            customer.user = request.user
            customer.name = request.user.get_full_name()
        customer.save()
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_quantity()
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {
        'cartItems': cartItems,
        'items': items,
        'order': order
    }

def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(email=email)
    if created:
        customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)
    for item in items:
        product = Product.objects.get(id=item['product'].id)
        orderItem = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])
    return customer, order

def serializePageObj(pageObj):
    page_obj = {}
    page_obj['number'] = pageObj.number
    page_obj['has_previous'] = pageObj.has_previous()
    if pageObj.has_previous():
        page_obj['previous_page_number'] = pageObj.previous_page_number()
    page_obj['has_next'] = pageObj.has_next()
    if pageObj.has_next():
        page_obj['next_page_number'] = pageObj.next_page_number()
    page_obj['paginator'] = {}
    page_range = [i for i in pageObj.paginator.page_range]
    page_obj['paginator'].setdefault('page_range', page_range)
    page_obj['paginator'].setdefault('num_pages', pageObj.paginator.num_pages)
    return page_obj

def serializeProducts(pageProducts):
    products = {'object_list':[]}
    for index, product in enumerate(pageProducts.object_list):
        products['object_list'].append(product.name)
        products['object_list'][index] = {}
        products['object_list'][index]['id'] = product.id
        products['object_list'][index]['name'] = product.name
        products['object_list'][index]['description'] = product.description
        products['object_list'][index]['price'] = product.price
        products['object_list'][index]['imageURL'] = product.imageURL
    return products

def serializeCategories(pageCategories):
    categories = []
    for index, category in enumerate(pageCategories):
        categories.append(category)
        categories[index] = {}
        categories[index]['category'] = category.category
    return categories

def serializeCarousels(pageCarousels):
    carousels = []
    for index, carousel in enumerate(pageCarousels):
        carousels.append(carousel)
        carousels[index] = {}
        carousels[index]['name'] = carousel.name
        carousels[index]['description'] = carousel.description
        carousels[index]['date_posted'] = carousel.date_posted
        carousels[index]['imageURL'] = carousel.imageURL
    return carousels

def serializeContext(context):
    serializedContext = {}
    serializedContext['title'] = context['title']
    serializedContext['cartItems'] = context['cartItems']
    serializedContext['is_paginated'] = context['is_paginated']
    serializedContext['page_obj'] = serializePageObj(context['page_obj'])
    serializedContext['products'] = serializeProducts(context['products'])
    serializedContext['categories'] = serializeCategories(context['categories'])
    serializedContext['carousels'] = serializeCarousels(context['carousels'])
    return serializedContext


def serializeItems(items):
    serializedItems = []
    if isinstance(items, QuerySet):
        for item in items:
            itemDict = {}
            itemDict.setdefault('product', {'id': item.product.id, 'name': item.product.name, 'price': item.product.price, 'imageURL': item.product.imageURL})
            itemDict.setdefault('get_total', item.get_total)
            itemDict.setdefault('quantity', item.quantity)
            serializedItems.append(itemDict)
    else:
        for item in items:
            itemDict = {}
            itemDict.setdefault('product', {'id': item['product'].id, 'name': item['product'].name, 'price': item['product'].price, 'imageURL': item['product'].imageURL})
            itemDict.setdefault('get_total', item['get_total'])
            itemDict.setdefault('quantity', item['quantity'])
            serializedItems.append(itemDict)
    return serializedItems


def serializeOrder(order):
    if isinstance(order, Model):
        serializedOrder = {'get_cart_total': order.get_cart_total}
    else:
        serializedOrder = {'get_cart_total': order['get_cart_total']}
    return serializedOrder