from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock', 'prescription_required', 'expiry_date', 'created_at')
    search_fields = ('name', 'brand', 'category')
    list_filter = ('category', 'prescription_required', 'expiry_date')

admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CustomUser, UserAdmin)
