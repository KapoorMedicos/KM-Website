from django.urls import path
from .views import ProductListCreateView, ProductDetailView, CartView, AddToCartView, RemoveFromCartView, UpdateCartItemView, CheckoutView, OrderHistoryView, UpdateOrderStatusView, CancelOrderView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from users.views import LoginView, RegisterView


urlpatterns = [
    path('auth/login/', obtain_auth_token, name='api_token_auth'),  # 🔥 Adds login endpoint
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', CartView.as_view(), name='cart-view'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/update/', UpdateCartItemView.as_view(), name='update-cart-item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderHistoryView.as_view(), name='order-history'),
    path('orders/update/<int:order_id>/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('orders/cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),
    path('login/', LoginView.as_view(), name='login'),  # Use as_view()
    path('register/', RegisterView.as_view(), name='register'),  # Use as_view()
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

