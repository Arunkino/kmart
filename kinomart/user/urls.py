"""
URL configuration for kinomart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views



urlpatterns = [
    path('', views.index,name='home'),
    path('signup/', views.signup,name='signup'),
    path('login/', views.login_user,name='login_user'),
    path('profile/', views.user_page,name='user_page'),
    path('edit_profile/', views.edit_profile,name='edit_profile'),
    path('change_password/', views.change_password,name='change_password'),
    path('logout/', views.logout_user,name='logout_user'),
    path('verify_your_account/', views.otp_user,name='otp_user'),
    path('product/<int:id>', views.view_product,name='view_product'),
    path('user_address/', views.user_address,name='user_address'),
    path('add_address/', views.add_address,name='add_address'),
    path('update_address/', views.update_address,name='update_address'),
    path('delete_address/', views.delete_address, name='delete_address'),
    path('default_address/', views.default_address, name='default_address'),
    path('order_history/', views.order_history, name='order_history'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wallet/', views.wallet, name='wallet'),




    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),



    

    
]


