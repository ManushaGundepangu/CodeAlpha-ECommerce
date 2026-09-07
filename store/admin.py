from django.contrib import admin
from .models import (
    Product,
    CartItem,
    Order,
    OrderItem,
    Category,
    Wishlist,
    Review
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'created_at'
    )

    list_filter = ('category',)
    search_fields = ('name', 'description')

    


admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'rating',
        'created_at'
    )

    list_filter = (
        'rating',
        'created_at'
    )

    search_fields = (
        'product__name',
        'user__username',
        'comment'
    )