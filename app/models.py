from django.db import models
# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Hub(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    pin_code = models.CharField(max_length=10)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name
# Create your models here.
from django.contrib.auth.models import AbstractUser
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    is_dealer = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    hub = models.ForeignKey(Hub, null=True, blank=True, on_delete=models.SET_NULL)
    is_hub = models.BooleanField(default=False)  # <-- Add this line
    is_branch = models.BooleanField(default=False)
    is_delivery_agent = models.BooleanField(default=False)  # ✅ ADD THIS LINE
    
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# -------------------------------
# CATEGORY MODEL
# -------------------------------
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # Optional category description

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


# -------------------------------
# PRODUCT MODEL
# -------------------------------
class Product(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', '2XL'),
    ]

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    is_taxable = models.BooleanField(default=False)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    brand = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name

    def gst_amount(self):
        if self.is_taxable and self.gst_percentage:
            return (self.price * self.gst_percentage) / 100
        return 0

    def total_price_with_gst(self):
        return self.price + self.gst_amount()


# -------------------------------
# WISHLIST MODEL
# -------------------------------
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.name}"


from django.db import models
from django.conf import settings  # Use settings.AUTH_USER_MODEL for user
from .models import Product  # Adjust if needed

class Purchase(models.Model):
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
    )

    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('shipping', 'Shipping'),
        ('delivered', 'Delivered'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_bought = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField(blank=True, null=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    admin_notes = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    coupon_used = models.CharField(max_length=50, blank=True, null=True, help_text="Coupon code used for this purchase")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Discount amount applied")
    
    parcel = models.OneToOneField('Parcel', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_delivery_agent = models.ForeignKey('DeliveryAgent', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Update STATUS_CHOICES to include more tracking statuses
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('at_hub', 'At Hub'),
        ('assigned_to_branch', 'Assigned to Branch'),
        ('assigned_to_agent', 'Assigned to Delivery Agent'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    )
    # Add to your Purchase model
    current_location = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)

    # GST-related fields
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price_with_gst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} bought {self.product.name} on {self.date_bought.strftime('%Y-%m-%d %H:%M')}"

    def get_total_price(self):
        return self.product.price * self.quantity

    def get_total_gst(self):
        return self.gst_amount or 0

    def get_total_price_with_gst(self):
        return self.total_price_with_gst or (self.get_total_price() + self.get_total_gst())

# -------------------------------
# CART MODEL
# -------------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'session_key')  # Prevent duplicate carts

    def __str__(self):
        return f"Cart ({self.user.username if self.user else f'Session {self.session_key}'})"


# -------------------------------
# CART ITEM MODEL
# -------------------------------
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def subtotal(self):
        return self.quantity * self.product.price





class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 to 5
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Prevent duplicate ratings

    def __str__(self):
        return f"{self.user.username} rated {self.product.name} - {self.rating} Stars"
    
# Add this to your models.py file

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}'s address in {self.city}"
    
    def save(self, *args, **kwargs):
        # If this address is being set as default, unset all other defaults for this user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        
        # If this is the first address for the user, make it default
        if not self.pk and not Address.objects.filter(user=self.user).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)    
    
    
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    search_query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username if self.user else f'Session {self.session_key}'} - {self.search_query}"
    
    class Meta:
        verbose_name_plural = "Search Histories"
        # Order by most recent searches first
        ordering = ['-timestamp']
        
        
        
# 21 may tuesday
from django.db import models

class Coupon(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percent = models.PositiveIntegerField(default=0)  # Add this field
    
    def __str__(self):
        return self.name

    def is_valid(self):
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date

    def __str__(self):
        return f"{self.name} ({self.code})"
        
class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'coupon')
    def __str__(self):
        return f"{self.user} - {self.coupon.code}"
    
    
    
    
    
# models.py
from django.db import models

class EmailSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
from django.db import models

class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    reason = models.TextField()
    proof_image = models.ImageField(upload_to='return_proofs/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.product_name} ({self.status})"







from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"









class Branch(models.Model):
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    pin_code = models.CharField(max_length=10)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.hub.name}"



# models.py
from django.db import models

class DeliveryAgent(models.Model):
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name='delivery_agents', null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    address = models.TextField()
    vehicle_number = models.CharField(max_length=50)
    license = models.CharField(max_length=50)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # If you create a user account for delivery agents

    def __str__(self):
        return self.name



#tuesday  27/05/25





class Parcel(models.Model):
    tracking_number = models.CharField(max_length=50, unique=True)
    sender = models.CharField(max_length=100)
    recipient = models.CharField(max_length=100)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    assigned_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='At Hub')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Parcel {self.tracking_number} - {self.status}"