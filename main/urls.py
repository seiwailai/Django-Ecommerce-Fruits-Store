from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='main-home'),
    path('categories/<str:category>/', views.CategoryView.as_view(), name='main-category'),
    path('about/', views.about, name='main-about'),
    path('login/', views.loginpage, name='main-login'),
    path('logout/', views.logoutUser, name='main-logout'),
    path('signup/', views.signup, name='main-signup'),
    path('cart/', views.cart, name='main-cart'),
    path('checkout/', views.checkout, name='main-checkout'),
    path('item_updated/', views.updateItem, name='main-updateitem'),
    path('process_order/', views.processOrder, name='main-process_order'),
]
