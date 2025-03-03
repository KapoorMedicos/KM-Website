from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, status
from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from weasyprint import HTML
from django.template.loader import render_to_string
import tempfile
from datetime import date


# ✅ Anyone (including unauthenticated users) can view products
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_permissions(self):
        """Allow anyone to view, but only admins can add products"""
        if self.request.method == 'GET':
            return [AllowAny()]  # ✅ GET requests are public
        return [IsAuthenticated(), IsAdminUser()]  # ✅ Only admins can add products

# ✅ Only admins can edit or delete products
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser]  # ✅ Only admins can update/delete

# ✅ View Cart
class CartView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can view their cart
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        data = [
            {"product": item.product.name, "quantity": item.quantity, "price": item.product.price}
            for item in cart_items
        ]

        return Response({"cart_id": cart.id, "items": data})

# ✅ Add Product to Cart
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        cart, created = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": "Product added to cart", "cart_item_id": cart_item.id})

# ✅ Remove Product from Cart
class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request):
        product_id = request.data.get("product_id")

        cart = Cart.objects.get(user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()

        return Response({"message": "Product removed from cart"})

# ✅ Update Cart Item Quantity
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity"))

        cart = Cart.objects.get(user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Cart updated"})

# ✅ Place an Order
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can place orders
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            return Response({"error": "Cart is empty"}, status=400)

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # ✅ Create Order
        order = Order.objects.create(user=request.user, total_price=total_price)

        # ✅ Move cart items to order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # ✅ Deduct stock
            item.product.stock -= item.quantity
            item.product.save()

        # ✅ Clear cart after checkout
        cart_items.delete()

        return Response({"message": "Order placed successfully", "order_id": order.id})

# ✅ View Order History with Tracking Info
class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        data = [
            {
                "order_id": order.id,
                "total_price": order.total_price,
                "status": order.status,
                "created_at": order.created_at,
                "items": [
                    {"product": item.product.name, "quantity": item.quantity, "price": item.price}
                    for item in order.items.all()
                ],
                "tracking": self.get_tracking_status(order.status)  # ✅ Tracking info
            }
            for order in orders
        ]
        return Response(data)

    def get_tracking_status(self, status):
        tracking_messages = {
            "pending": "Your order has been received and is awaiting processing.",
            "processing": "Your order is being prepared.",
            "shipped": "Your order has been shipped and is on the way.",
            "delivered": "Your order has been delivered!",
            "cancelled": "Your order has been cancelled.",
        }
        return tracking_messages.get(status, "Unknown status")

# ✅ Admin: Update Order Status (Processing → Shipped → Delivered)
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get("status")

        valid_statuses = ['processing', 'shipped', 'delivered']
        
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status update."}, status=400)

        # ✅ Prevent reversing order status (e.g., from 'shipped' back to 'pending')
        if order.status in ['shipped', 'delivered'] and new_status == 'processing':
            return Response({"error": "You cannot move an order back to processing after shipping."}, status=400)

        order.status = new_status
        order.save()
        return Response({"message": f"Order {order.id} status updated to {new_status}."})

# ✅ Cancel an Order (Only if it's still pending)
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != 'pending':
            return Response({"error": "You can only cancel pending orders."}, status=400)

        # ✅ Refund stock before cancelling
        for item in order.items.all():
            item.product.stock += item.quantity  # Restore stock
            item.product.save()

        order.status = 'cancelled'
        order.save()
        return Response({"message": f"Order {order.id} has been cancelled."})

