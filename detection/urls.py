from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload'),
    path('result/', views.result_view, name='result'),
    path('shop/', views.shop_view, name='shop'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
]

