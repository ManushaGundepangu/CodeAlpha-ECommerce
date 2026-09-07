from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from store.views import (
    home,
    product_detail,
    add_to_cart,
    cart,
    remove_from_cart,
    update_cart,
    register,
    user_login,
    user_logout,
    checkout,
    order_success,
    my_orders,
    add_to_wishlist,
    remove_from_wishlist,
    wishlist,
    category_products,
    add_review,
    delete_review,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', home, name='home'),

    path('product/<int:id>/', product_detail, name='product_detail'),

    path('cart/', cart, name='cart'),

    path('add-to-cart/<int:id>/', add_to_cart, name='add_to_cart'),

    path('remove-from-cart/<int:id>/', remove_from_cart, name='remove_from_cart'),

    path('update-cart/<int:id>/', update_cart, name='update_cart'),

    path('register/', register, name='register'),

    path('login/', user_login, name='login'),

    path('logout/', user_logout, name='logout'),

    path('checkout/', checkout, name='checkout'),

    path('order-success/<int:order_id>/', order_success, name='order_success'),
    path('my-orders/', my_orders, name='my_orders'),
    path(
    'wishlist/',
    wishlist,
    name='wishlist'
    ),

    path(
        'add-to-wishlist/<int:id>/',
        add_to_wishlist,
        name='add_to_wishlist'
    ),

    path(
        'remove-from-wishlist/<int:id>/',
        remove_from_wishlist,
        name='remove_from_wishlist'
    ),
    path(
        'category/<int:id>/',
        category_products,
        name='category_products'
    ),
    path(
        'product/<int:id>/',
        product_detail,
        name='product_detail'
    ),
    path(
        'product/<int:id>/review/',
        add_review,
        name='add_review'
    ),

    path(
        'review/<int:id>/delete/',
        delete_review,
        name='delete_review'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )