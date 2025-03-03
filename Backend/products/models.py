from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.conf import settings


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('tablet', 'Tablet'),
        ('syrup', 'Syrup'),
        ('ointment', 'Ointment'),
        ('capsule', 'Capsule'),
        ('injection', 'Injection'),
        ('device', 'Medical Device'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)  # Medicine name
    brand = models.CharField(max_length=255, blank=True, null=True)  # Brand name
    description = models.TextField(blank=True, null=True)  # Medicine description
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='tablet')  # Medicine type
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    stock = models.PositiveIntegerField(default=0)  # Available stock count
    prescription_required = models.BooleanField(default=False)  # Is a prescription required?
    expiry_date = models.DateField(blank=True, null=True)  # Expiry date of medicine
    image = models.ImageField(upload_to="product_images/", blank=True, null=True) # Optional product image
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when product is added

    def __str__(self):
        return f"{self.name} ({self.brand})"

# ✅ Cart Model: Each user has a cart, and it can contain multiple items
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Linked to the logged-in user
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for the cart

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"

# ✅ CartItem Model: Stores products added to the cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")  # Belongs to a cart
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Product being added
    quantity = models.PositiveIntegerField(default=1)  # Number of units

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"
    
# ✅ Order Model: Stores order details
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Customer who placed the order
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Order total
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Order status
    created_at = models.DateTimeField(auto_now_add=True)  # When order was placed

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

# ✅ OrderItem Model: Stores products inside an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Linked to an order
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Product being ordered
    quantity = models.PositiveIntegerField()  # Number of units
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20)
    date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    hsn_code = models.CharField(max_length=20)
    pack_size = models.CharField(max_length=50)
    quantity = models.IntegerField()
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)

