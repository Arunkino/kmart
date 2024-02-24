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
    path('', views.login,name='admin_login'),
    path('logout/', views.logout,name='logout'),
    path('users/', views.user_list,name='admin_userlist'),
    path('add_product/', views.add_product,name='add_product'),
    path('list_product/', views.list_product,name='list_product'),
    path('edit_product/<int:id>', views.edit_product, name='edit_product'),
    path('hold_product/<int:id>', views.hold_product, name='hold_product'),
    path('admin_orders/', views.admin_orders,name='admin_orders'),
    path('index', views.index,name='index'),
    path('block/<int:id>/', views.block_user,name='block_user'), 
    path('users/unblock/<int:id>/', views.unblock_user,name='unblock_user'), 
    path('edit_categories/', views.edit_categories,name='edit_categories'),
    path('edit_categories/delete_subcategory/<int:id>/', views.delete_subcategory,name='delete_subcategory'), 
    path('edit_categories/delete_category/<int:id>/', views.delete_category,name='delete_category'), 

    path('add_category/', views.add_category,name='add_category'), 
    path('update_category/', views.update_category,name='update_category'), 
    path('update_subcategory/', views.update_subcategory,name='update_subcategory'), 
    path('add_subcategory/', views.add_subcategory,name='add_subcategory'), 
    path('ajax_load_subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('coupon_management/', views.coupon_management, name='coupon_management'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('edit_coupon/', views.edit_coupon, name='edit_coupon'),

    
    path('sales_report/', views.sales_report, name='sales_report'),
    path('sales_report_all/', views.sales_report_all, name='sales_report_all'),


    
    path('offer/', include('offer.urls'),),


    
]
