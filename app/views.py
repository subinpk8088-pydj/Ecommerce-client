from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def news(request):
    return render(request, 'news.html')
def blog(request):
    return render(request, 'blog.html')
def logout_view(request):
    logout(request)
    return redirect('login')  # Or 'home' or 'landing_page'




from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_dealer:
                if not user.is_approved:
                    messages.error(request, "Your dealer account is not yet approved.")
                    return redirect('login')
                else:
                    auth_login(request, user)
                    return redirect('dealer_dashboard')
            elif user.is_superuser:
                auth_login(request, user)
                return redirect('admin_dashboard')
            elif user.is_hub:
                auth_login(request, user)
                return redirect('hub_dashboard')
            elif user.is_branch:
                auth_login(request, user)
                return redirect('branch_dashboard')
            elif user.is_delivery_agent:  # ✅ DELIVERY AGENT LOGIN
                auth_login(request, user)
                return redirect('delivery_agent_dashboard')
            else:
                auth_login(request, user)
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def branch_dashboard(request):
    return render(request, 'branch/branch_dashboard.html')


from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

import random
import string

User = get_user_model()

def generate_random_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def register(request):
    if request.method == 'POST':
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone_number')
        address = request.POST.get('address')
        profile_image = request.FILES.get('profile_image')
        is_dealer = request.POST.get('is_dealer') == 'on'  # Check if dealer checkbox is checked
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'register.html')
        
        password = generate_random_password()
        
        user = User(
            first_name=fname,
            last_name=lname,
            username=username,
            email=email,
            phone_number=phone,
            address=address,
            profile_image=profile_image,
            password=make_password(password),
            is_dealer=is_dealer,
            is_approved=not is_dealer  # Regular users are approved by default, dealers need approval
        )
        user.save()
        
        # Send email with login credentials
        if not is_dealer:
            # Regular user registration email
            send_mail(
                subject='Welcome to Our eCommerce Platform',
                message=f'Hi {fname},\n\nYour account has been created.\nUsername: {username}\nPassword: {password}',
                from_email='noreply@ecommerce.com',
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, "Registration successful. Check your email for login details.")
        else:
            # Dealer registration email
            send_mail(
                subject='Dealer Registration - Pending Approval',
                message=f'Hi {fname},\n\nThank you for registering as a dealer on our eCommerce platform. '
                        f'Your application is pending approval from our administrators. '
                        f'You will receive your login credentials once your account is approved.',
                from_email='noreply@ecommerce.com',
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, "Dealer registration submitted. Pending admin approval.")
        
        return redirect('login')
    return render(request, 'register.html')


@staff_member_required
def pending_dealers(request):
    """View to list all pending dealer approvals"""
    pending_dealers = User.objects.filter(is_dealer=True, is_approved=False)
    return render(request, 'admin/pending_dealers.html', {'pending_dealers': pending_dealers})

@staff_member_required
def approve_dealer(request, user_id):
    """View to approve a dealer"""
    try:
        dealer = User.objects.get(id=user_id, is_dealer=True, is_approved=False)
        dealer.is_approved = True
        dealer.save()
        
        # Generate new password for security
        password = generate_random_password()
        dealer.password = make_password(password)
        dealer.save()
        
        # Send approval email with credentials
        send_mail(
            subject='Dealer Account Approved',
            message=f'Hi {dealer.first_name},\n\n'
                    f'Your dealer account has been approved!\n\n'
                    f'You can now log in to your dealer dashboard using the following credentials:\n'
                    f'Username: {dealer.username}\n'
                    f'Password: {password}\n\n'
                    f'Please change your password after your first login.',
            from_email='noreply@ecommerce.com',
            recipient_list=[dealer.email],
            fail_silently=False,
        )
        
        messages.success(request, f"Dealer {dealer.username} has been approved. Login credentials sent.")
    except User.DoesNotExist:
        messages.error(request, "Dealer not found.")
    
    return redirect('pending_dealers')

@login_required
def dealer_dashboard(request):
    """Dealer dashboard view"""
    if not request.user.is_dealer or not request.user.is_approved:
        messages.error(request, "You do not have access to the dealer dashboard.")
        return redirect('home')
    
    return render(request, 'dealer/dealer_dashboard.html')

from django.http import JsonResponse
import re

def validate_field(request):
    field = request.GET.get('field')
    value = request.GET.get('value')

    if field == 'username':
        if User.objects.filter(username=value).exists():
            return JsonResponse({'valid': False, 'message': 'Username already exists.'})
        return JsonResponse({'valid': True})

    if field == 'email':
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value) or not value.endswith(".com"):
            return JsonResponse({'valid': False, 'message': 'Enter a valid .com email.'})
        if User.objects.filter(email=value).exists():
            return JsonResponse({'valid': False, 'message': 'Email already registered.'})
        return JsonResponse({'valid': True})

    if field == 'phone_number':
        if not value.isdigit() or len(value) != 10:
            return JsonResponse({'valid': False, 'message': 'Phone number must be 10 digits.'})
        if User.objects.filter(phone_number=value).exists():
            return JsonResponse({'valid': False, 'message': 'Phone number already in use.'})
        return JsonResponse({'valid': True})

    return JsonResponse({'valid': False, 'message': 'Invalid field'})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product


from django.contrib.auth.decorators import login_required, user_passes_test

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@superuser_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category
from django.contrib import messages

@login_required
def add_category(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')  # Get the category ID for editing (if exists)
        
        # If category_id is present, we're editing an existing category
        if category_id:
            category = Category.objects.get(id=category_id)
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.save()
            messages.success(request, "Category updated successfully!")
        else:
            # Add a new category
            name = request.POST.get('name')
            description = request.POST.get('description')
            Category.objects.create(name=name, description=description)
            messages.success(request, "Category added successfully!")
    
    categories = Category.objects.all()
    return render(request, 'admin/add_category.html', {'categories': categories})

@login_required
def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, "Category deleted successfully!")
    except Category.DoesNotExist:
        messages.error(request, "Category not found!")
    
    return redirect('add_category')



from django.contrib.auth.decorators import login_required
from .models import CustomUser  # Import CustomUser

@login_required
def admin_users(request):
    # Exclude users who are admin (is_staff or is_superuser)
    users = CustomUser.objects.exclude(is_staff=True).exclude(is_superuser=True)
    return render(request, 'admin/admin_users.html', {'users': users})

# Delete User
@login_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('admin_users')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Category, Product, EmailSubscriber  # Make sure EmailSubscriber is defined in models

@login_required
def add_product(request, product_id=None):
    categories = Category.objects.all()
    gst_options = [3, 5, 11, 18, 25]
    size_options = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', '2XL')
    ]

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description', '')
        quantity = request.POST.get('quantity') or 0
        image = request.FILES.get('image')
        is_taxable = request.POST.get('is_taxable') == 'True'
        gst_percentage = request.POST.get('gst_percentage')
        brand = request.POST.get('brand')
        size = request.POST.get('size')

        # Validate GST percentage choice
        if is_taxable and gst_percentage:
            try:
                gst_percentage = float(gst_percentage)
                if gst_percentage not in gst_options:
                    messages.error(request, "Invalid GST percentage selected.")
                    return redirect('add_product')
            except (ValueError, TypeError):
                gst_percentage = None
        else:
            gst_percentage = None

        if 'product_id' in request.POST and request.POST.get('product_id'):
            product = get_object_or_404(Product, id=request.POST.get('product_id'))
            product.name = name
            product.category_id = category_id
            product.price = price
            product.description = description
            product.quantity = quantity
            product.is_taxable = is_taxable
            product.gst_percentage = gst_percentage
            product.brand = brand
            product.size = size

            if image:
                product.image = image
            product.save()
            messages.success(request, "Product updated successfully!")
            return redirect('add_product')

        else:
            category = get_object_or_404(Category, id=category_id)
            product = Product(
                name=name,
                category=category,
                price=price,
                description=description,
                quantity=quantity,
                image=image,
                is_taxable=is_taxable,
                gst_percentage=gst_percentage,
                brand=brand,
                size=size
            )
            product.save()

            # Send email notifications to subscribers with modern professional template
            subscribers = EmailSubscriber.objects.all()
            emails = [sub.email for sub in subscribers]

            if emails:
                # Create modern HTML email template
                html_message = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>New Product Launch</title>
                    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap" rel="stylesheet">
                    <style>
                        * {{
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                        }}
                        
                        body {{
                            font-family: 'Nunito', Arial, sans-serif;
                            background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
                            padding: 40px 20px;
                            line-height: 1.6;
                            color: #4a4a4a;
                        }}
                        
                        .email-container {{
                            max-width: 600px;
                            margin: 0 auto;
                            background: white;
                            border-radius: 24px;
                            box-shadow: 0 20px 40px rgba(124, 82, 149, 0.15);
                            overflow: hidden;
                            animation: slideUp 0.8s ease-out;
                        }}
                        
                        @keyframes slideUp {{
                            from {{
                                opacity: 0;
                                transform: translateY(30px);
                            }}
                            to {{
                                opacity: 1;
                                transform: translateY(0);
                            }}
                        }}
                        
                        .header {{
                            background: linear-gradient(135deg, #7c5295 0%, #9d72b8 100%);
                            padding: 40px 30px;
                            text-align: center;
                            position: relative;
                            overflow: hidden;
                        }}
                        
                        .header::before {{
                            content: '';
                            position: absolute;
                            top: -50%;
                            left: -50%;
                            width: 200%;
                            height: 200%;
                            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                            animation: pulse 4s ease-in-out infinite;
                        }}
                        
                        @keyframes pulse {{
                            0%, 100% {{ transform: scale(1); opacity: 0.3; }}
                            50% {{ transform: scale(1.05); opacity: 0.1; }}
                        }}
                        
                        .header h1 {{
                            color: white;
                            font-size: 32px;
                            font-weight: 800;
                            margin-bottom: 8px;
                            position: relative;
                            z-index: 2;
                        }}
                        
                        .header p {{
                            color: rgba(255, 255, 255, 0.9);
                            font-size: 18px;
                            font-weight: 400;
                            position: relative;
                            z-index: 2;
                        }}
                        
                        .content {{
                            padding: 40px 30px;
                        }}
                        
                        .greeting {{
                            font-size: 20px;
                            font-weight: 600;
                            color: #7c5295;
                            margin-bottom: 20px;
                            animation: fadeIn 1s ease-out 0.3s both;
                        }}
                        
                        @keyframes fadeIn {{
                            from {{ opacity: 0; transform: translateY(20px); }}
                            to {{ opacity: 1; transform: translateY(0); }}
                        }}
                        
                        .product-card {{
                            background: linear-gradient(135deg, #f8f7ff 0%, #f3f1ff 100%);
                            border-radius: 20px;
                            padding: 30px;
                            margin: 30px 0;
                            border: 2px solid rgba(124, 82, 149, 0.1);
                            position: relative;
                            overflow: hidden;
                            animation: slideIn 0.8s ease-out 0.5s both;
                        }}
                        
                        @keyframes slideIn {{
                            from {{ opacity: 0; transform: translateX(-30px); }}
                            to {{ opacity: 1; transform: translateX(0); }}
                        }}
                        
                        .product-card::before {{
                            content: '';
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 4px;
                            height: 100%;
                            background: linear-gradient(to bottom, #7c5295, #9d72b8);
                        }}
                        
                        .product-name {{
                            font-size: 24px;
                            font-weight: 700;
                            color: #7c5295;
                            margin-bottom: 15px;
                        }}
                        
                        .product-details {{
                            display: grid;
                            gap: 12px;
                        }}
                        
                        .product-detail {{
                            display: flex;
                            align-items: center;
                            font-size: 16px;
                        }}
                        
                        .detail-label {{
                            font-weight: 600;
                            color: #7c5295;
                            min-width: 80px;
                            margin-right: 10px;
                        }}
                        
                        .detail-value {{
                            color: #666;
                            font-weight: 400;
                        }}
                        
                        .price {{
                            font-size: 28px;
                            font-weight: 800;
                            color: #7c5295;
                            margin: 20px 0;
                        }}
                        
                        .description {{
                            background: white;
                            padding: 20px;
                            border-radius: 16px;
                            margin: 20px 0;
                            border-left: 4px solid #7c5295;
                            font-style: italic;
                            color: #666;
                        }}
                        
                        .cta-button {{
                            display: inline-block;
                            background: linear-gradient(135deg, #7c5295 0%, #9d72b8 100%);
                            color: white;
                            text-decoration: none;
                            padding: 16px 32px;
                            border-radius: 50px;
                            font-weight: 700;
                            font-size: 18px;
                            text-align: center;
                            margin: 30px 0;
                            box-shadow: 0 10px 30px rgba(124, 82, 149, 0.3);
                            transition: all 0.3s ease;
                            animation: fadeIn 1s ease-out 0.8s both;
                        }}
                        
                        .cta-button:hover {{
                            transform: translateY(-2px);
                            box-shadow: 0 15px 40px rgba(124, 82, 149, 0.4);
                        }}
                        
                        .footer {{
                            background: #fafafa;
                            padding: 30px;
                            text-align: center;
                            border-top: 1px solid #eee;
                        }}
                        
                        .footer p {{
                            color: #888;
                            font-size: 14px;
                            margin-bottom: 10px;
                        }}
                        
                        .social-links {{
                            margin: 20px 0;
                        }}
                        
                        .social-links a {{
                            display: inline-block;
                            width: 40px;
                            height: 40px;
                            background: #7c5295;
                            color: white;
                            border-radius: 50%;
                            line-height: 40px;
                            text-decoration: none;
                            margin: 0 5px;
                            transition: all 0.3s ease;
                        }}
                        
                        .social-links a:hover {{
                            background: #9d72b8;
                            transform: translateY(-2px);
                        }}
                        
                        .highlight {{
                            background: linear-gradient(120deg, transparent 0%, rgba(124, 82, 149, 0.1) 50%, transparent 100%);
                            padding: 3px 8px;
                            border-radius: 8px;
                            font-weight: 600;
                        }}
                        
                        @media (max-width: 600px) {{
                            .email-container {{
                                margin: 0 10px;
                                border-radius: 16px;
                            }}
                            
                            .header, .content, .footer {{
                                padding: 20px;
                            }}
                            
                            .header h1 {{
                                font-size: 24px;
                            }}
                            
                            .product-card {{
                                padding: 20px;
                            }}
                            
                            .cta-button {{
                                display: block;
                                padding: 14px 24px;
                                font-size: 16px;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="header">
                            <h1>🎉 New Arrival!</h1>
                            <p>Something amazing just landed in our store</p>
                        </div>
                        
                        <div class="content">
                            <div class="greeting">Hey there, fashion lover! 👋</div>
                            
                            <p>We're absolutely <span class="highlight">thrilled</span> to introduce our latest addition that we know you're going to love!</p>
                            
                            <div class="product-card">
                                <div class="product-name">✨ {product.name}</div>
                                
                                <div class="product-details">
                                    <div class="product-detail">
                                        <span class="detail-label">Category:</span>
                                        <span class="detail-value">{product.category.name}</span>
                                    </div>
                                    {f'<div class="product-detail"><span class="detail-label">Brand:</span><span class="detail-value">{product.brand}</span></div>' if product.brand else ''}
                                    {f'<div class="product-detail"><span class="detail-label">Size:</span><span class="detail-value">{product.get_size_display() if hasattr(product, "get_size_display") else product.size}</span></div>' if product.size else ''}
                                </div>
                                
                                <div class="price">💰 ${product.price}</div>
                                
                                {f'<div class="description">"{product.description}"</div>' if product.description else ''}
                            </div>
                            
                            <p>This exclusive piece is now available and ready to elevate your style. Don't wait too long – our best items tend to fly off the shelves! 🏃‍♀️💨</p>
                            
                            <div style="text-align: center;">
                                <a href="#" class="cta-button">🛍️ Shop Now</a>
                            </div>
                            
                            <p style="margin-top: 30px; font-size: 16px; color: #666;">
                                <strong>Why you'll love it:</strong><br>
                                🌟 Premium quality materials<br>
                                🚚 Fast & free shipping<br>
                                💯 100% satisfaction guarantee<br>
                                🔄 Easy returns within 30 days
                            </p>
                        </div>
                        
                        <div class="footer">
                            <p><strong>Thank you for being part of our fashion family!</strong></p>
                            <p>Follow us for the latest updates and exclusive offers:</p>
                            
                            <div class="social-links">
                                <a href="#">📘</a>
                                <a href="#">📷</a>
                                <a href="#">🐦</a>
                                <a href="#">📌</a>
                            </div>
                            
                            <p style="font-size: 12px; color: #aaa; margin-top: 20px;">
                                You're receiving this because you subscribed to our newsletter.<br>
                                <a href="#" style="color: #7c5295;">Unsubscribe</a> | 
                                <a href="#" style="color: #7c5295;">Update Preferences</a>
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """

                # Create plain text version for email clients that don't support HTML
                plain_message = f"""
                🎉 NEW PRODUCT LAUNCH! 🎉
                
                Hey there!
                
                We're excited to introduce our latest addition: {product.name}
                
                Product Details:
                • Category: {product.category.name}
                • Price: ${product.price}
                {f'• Brand: {product.brand}' if product.brand else ''}
                {f'• Size: {product.size}' if product.size else ''}
                {f'• Description: {product.description}' if product.description else ''}
                
                This exclusive piece is now available in our store. Don't miss out!
                
                Visit our store now to check it out!
                
                Thank you for being part of our fashion family!
                
                ---
                You're receiving this because you subscribed to our newsletter.
                """

                send_mail(
                    subject=f"🎉 New Arrival: {product.name} - Don't Miss Out!",
                    message=plain_message,
                    html_message=html_message,
                    from_email='yourshop@example.com',  # Replace with your email
                    recipient_list=emails,
                    fail_silently=False,
                )

            messages.success(request, "Product added successfully!")
            return redirect('add_product')

    else:
        product = None
        if product_id:
            product = get_object_or_404(Product, id=product_id)

    products = Product.objects.all()
    return render(request, 'admin/add_product.html', {
        'categories': categories,
        'products': products,
        'product': product,
        'gst_options': gst_options,
        'size_options': size_options,
    })

@login_required
def delete_product(request, product_id):
    if request.method == 'POST':
        # Fetch the product by its ID and delete it
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, "Product deleted successfully!")
    else:
        messages.error(request, "Invalid request.")
    
    # Redirect back to the product listing page
    return redirect('add_product')
def admin_help(request):
    return render(request, 'admin/admin_help.html')






from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, Wishlist, Purchase, Cart, CartItem, Category
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

User = get_user_model()

from django.db.models import Avg, Count
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from .models import Product, Category, Wishlist, CartItem, SearchHistory

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
from .models import Category, Product, Wishlist, SearchHistory

def view_products(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Base queryset
    products = Product.objects.all()
    
    # Apply search filter if search query exists
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
        
        # Save search query to history if it has results
        if products.exists() and search_query.strip():
            if request.user.is_authenticated:
                SearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query
                )
            else:
                if not request.session.session_key:
                    request.session.create()
                SearchHistory.objects.create(
                    session_key=request.session.session_key,
                    search_query=search_query
                )
    
    # Get distinct brands for the brand filter
    brands = Product.objects.exclude(brand__isnull=True).exclude(brand='').values_list('brand', flat=True).distinct()
    
    # Get available product sizes
    sizes = [size[0] for size in Product.SIZE_CHOICES]
    
    # Annotate with average rating
    products = products.annotate(
        avg_rating=Avg('ratings__rating'),
        review_count=Count('ratings')
    )
    
    # Get all categories for the category filter
    categories = Category.objects.all()
    
    # Get recommended products from our helper function
    recommended_products = get_recommended_products(request)
    
    # If no recommendations from search history, fall back to top-rated products
    if not recommended_products:
        recommended_products = Product.objects.annotate(
            avg_rating=Avg('ratings__rating')
        ).filter(avg_rating__gte=4).order_by('-avg_rating')[:6]
    
    # Get user's wishlist if authenticated
    wishlist = []
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).values_list('product', flat=True)
        wishlist = Product.objects.filter(id__in=wishlist_items)
    
    # Get cart count for displaying in the header
    cart_count = 0
    if request.user.is_authenticated and 'cart' in request.session:
        cart = request.session['cart']
        cart_count = sum(item['quantity'] for item in cart.values())
    
    # Calculate delivery dates (6-7 days from today)
    today = datetime.now().date()
    min_delivery_date = today + timedelta(days=6)
    max_delivery_date = today + timedelta(days=7)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'recommended_products': recommended_products,
        'wishlist': wishlist,
        'cart_count': cart_count,
        'brands': brands,
        'sizes': sizes,
        'min_delivery_date': min_delivery_date,
        'max_delivery_date': max_delivery_date,
    }
    
    return render(request, 'view_products.html', context)
def get_recommended_products(request):
    """
    Get recommended products based on user's search history
    """
    # Get user's search history
    if request.user.is_authenticated:
        search_history = SearchHistory.objects.filter(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        search_history = SearchHistory.objects.filter(session_key=request.session.session_key)
    
    # If no search history, return empty list
    if not search_history.exists():
        return []
    
    # Get last 5 searches
    recent_searches = search_history.order_by('-timestamp')[:5]
    
    # Create Q objects for each search term
    q_objects = Q()
    for search in recent_searches:
        q_objects |= Q(name__icontains=search.search_query)
        q_objects |= Q(category__name__icontains=search.search_query)
    
    # Get products matching search terms
    recommended = Product.objects.filter(q_objects).annotate(
        avg_rating=Avg('ratings__rating'),
        review_count=Count('ratings')
    ).distinct()
    
    # Limit to 10 products
    return recommended[:10]
# Utility function to get or create a cart
def get_user_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Product, CartItem

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_user_cart(request)
    
    # Check if product has enough quantity
    if product.quantity <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect('view_products')
        
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Add success message
    messages.success(request, f"✅ {product.name} has been added to your cart.")
    
    return redirect('view_products')


from decimal import Decimal
from django.shortcuts import render
from .models import CartItem

# Define GST percentage here or in settings.py
GST_PERCENTAGE = Decimal('18.00')  # 18% GST

def view_cart(request):
    cart = get_user_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)

    total_price = Decimal('0.00')
    cart_count = 0

    for item in cart_items:
        item.subtotal = item.quantity * item.product.price
        total_price += item.subtotal
        cart_count += item.quantity

    gst_amount = (total_price * GST_PERCENTAGE) / Decimal('100')
    grand_total = total_price + gst_amount

    request.session['cart_count'] = cart_count

    return render(request, 'cart.html', {
        'items': cart_items,
        'total_price': total_price,
        'gst_percentage': GST_PERCENTAGE,
        'gst_amount': gst_amount,
        'grand_total': grand_total,
        'cart_count': cart_count
    })



from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem

@login_required
def update_cart(request):
    if request.method == 'POST':
        cart = get_user_cart(request)
        for item in CartItem.objects.filter(cart=cart):
            quantity = request.POST.get(f'quantity_{item.id}')
            if quantity and quantity.isdigit():
                item.quantity = max(1, int(quantity))  # Ensure at least 1
                item.save()
        
        # ✅ Add success message
        messages.success(request, "✅ Your cart has been updated successfully.")
    
    return redirect('view_cart')


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import CartItem,Address

@login_required
def remove_from_cart(request, item_id):
    cart = get_user_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    # ✅ Add success message
    messages.success(request, "🛒 Item removed from your cart.")

    return redirect('view_cart')
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Product, Wishlist

@require_POST
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        status = "removed"
        message = "💔 Removed from wishlist"
    else:
        status = "added"
        message = "💖 Added to wishlist"
    
    # Include message in JSON (to show via JS)
    return JsonResponse({"status": status, "message": message})

   

from django.contrib.auth.decorators import login_required
from .models import Wishlist, CartItem

@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    
    # ✅ Add cart count logic
    cart = get_user_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = sum(item.quantity for item in cart_items)
    request.session['cart_count'] = cart_count

    return render(request, 'wishlist.html', {
        'wishlist': wishlist,
        'cart_count': cart_count,  # Optional: pass to template if needed
    })


# New view for the buy page (replaces the modal)
@login_required
def buy_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.quantity <= 0:
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.error(request, "This product is out of stock")
        return redirect('view_products')
    
    return render(request, 'buy_page.html', {'product': product})


@login_required
@require_POST
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.quantity <= 0:
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.error(request, "This product is out of stock")
        return redirect('view_products')
    
    # Process purchase if POST data is valid
    address = request.POST.get('address')
    payment_mode = request.POST.get('payment_mode')
    
    if address and payment_mode:
        # Create purchase record
        purchase = Purchase.objects.create(
            user=request.user,
            product=product,
            date_bought=timezone.now(),
            delivery_address=address,
            payment_mode=payment_mode
        )
        
        # Update product quantity
        product.quantity -= 1
        product.save()
        
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.success(request, f"Successfully purchased {product.name}!")
        
        return redirect('bought_items')
    
    return redirect('view_products')



# Add these views to your views.py file

@login_required
def manage_addresses(request):
    """View to manage user addresses"""
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission for new address
        name = request.POST.get('name')
        phone = request.POST.get('phone') 
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        is_default = request.POST.get('is_default') == 'on'
        
        if name and phone and address_line and city and state and pincode:
            # Create new address
            Address.objects.create(
                user=request.user,
                name=name,
                phone_number=phone,
                address_line=address_line,
                city=city,
                state=state,
                pincode=pincode,
                is_default=is_default
            )
            
            if hasattr(request, 'messages'):
                from django.contrib import messages
                messages.success(request, "Address added successfully")
            
            # Redirect to addresses page or checkout
            next_url = request.POST.get('next', 'manage_addresses')
            return redirect(next_url)
        else:
            if hasattr(request, 'messages'):
                from django.contrib import messages
                messages.error(request, "Please fill all required fields")
    
    return render(request, 'manage_addresses.html', {
        'addresses': addresses
    })

@login_required
def delete_address(request, address_id):
    """Delete a user address"""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        was_default = address.is_default
        address.delete()
        
        # If we deleted a default address, set a new default if any addresses remain
        if was_default:
            remaining = Address.objects.filter(user=request.user).first()
            if remaining:
                remaining.is_default = True
                remaining.save()
        
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.success(request, "Address deleted successfully")
    except Address.DoesNotExist:
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.error(request, "Address not found")
    
    # Get the next URL or default to addresses page
    next_url = request.GET.get('next', 'manage_addresses')
    return redirect(next_url)

@login_required
def set_default_address(request, address_id):
    """Set an address as default"""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        
        # Set all addresses as not default
        Address.objects.filter(user=request.user).update(is_default=False)
        
        # Set the selected address as default
        address.is_default = True
        address.save()
        
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.success(request, "Default address updated")
    except Address.DoesNotExist:
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.error(request, "Address not found")
    
    # Get the next URL or default to addresses page
    next_url = request.GET.get('next', 'manage_addresses')
    return redirect(next_url)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import CartItem, Address, UserCoupon, Coupon
from django.utils import timezone
import json

@login_required
def checkout(request):
    cart = get_user_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items:
        from django.contrib import messages
        messages.error(request, "Your cart is empty")
        return redirect('view_cart')
    
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()
    
    # Get ALL available coupons (not just user's)
    now = timezone.now()
    all_coupons = Coupon.objects.filter(
        start_date__lte=now.date(),
        end_date__gte=now.date()
    )
    
    # Get user's available coupons (unused and valid)
    user_coupons = UserCoupon.objects.filter(
        user=request.user,
        is_used=False,
        coupon__start_date__lte=now.date(),
        coupon__end_date__gte=now.date()
    ).select_related('coupon')
    
    subtotal = 0
    total_gst = 0
    
    for item in cart_items:
        product = item.product
        item.subtotal = item.quantity * product.price
        item.gst = item.quantity * product.gst_amount()  # from model method
        item.total_with_gst = item.subtotal + item.gst
        
        subtotal += item.subtotal
        total_gst += item.gst
    
    grand_total = subtotal + total_gst
    
    return render(request, 'checkout.html', {
        'items': cart_items,
        'subtotal': subtotal,
        'total_gst': total_gst,
        'grand_total': grand_total,
        'addresses': addresses,
        'default_address': default_address,
        'user_coupons': user_coupons,
        'all_coupons': all_coupons
    })

@csrf_exempt
@require_POST
def validate_coupon(request):
    """AJAX endpoint to validate coupon codes"""
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code', '').strip().upper()
        
        if not coupon_code:
            return JsonResponse({'valid': False, 'message': 'Please enter a coupon code'})
        
        now = timezone.now()
        
        # Check if coupon exists and is valid
        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                start_date__lte=now.date(),
                end_date__gte=now.date()
            )
            
            # Check if user already has this coupon and it's not used
            user_coupon, created = UserCoupon.objects.get_or_create(
                user=request.user,
                coupon=coupon,
                defaults={'is_used': False}
            )
            
            if user_coupon.is_used:
                return JsonResponse({
                    'valid': False, 
                    'message': 'This coupon has already been used'
                })
            
            return JsonResponse({
                'valid': True,
                'coupon': {
                    'id': user_coupon.id,
                    'name': coupon.name,
                    'code': coupon.code,
                    'discount_percent': 10  # All coupons have 10% discount
                },
                'message': f'Coupon "{coupon.code}" applied successfully!'
            })
            
        except Coupon.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'message': 'Invalid coupon code'
            })
            
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'message': 'An error occurred while validating the coupon'
        })

@require_POST
def process_checkout(request):
    """Process the checkout for all items in the cart and send invoice emails"""
    cart = get_user_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items:
        messages.error(request, "Your cart is empty")
        return redirect('view_cart')
    
    # Get address, payment mode, and coupon
    address_id = request.POST.get('address_id')
    payment_mode = request.POST.get('payment_mode')
    coupon_id = request.POST.get('coupon_id')
    
    try:
        # Get or construct delivery address
        if address_id:
            delivery_address = Address.objects.get(id=address_id, user=request.user)
            address_text = f"{delivery_address.name}, {delivery_address.phone_number}, {delivery_address.address_line}, {delivery_address.city}, {delivery_address.state} - {delivery_address.pincode}"
        else:
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')
            
            if all([name, phone, address, city, state, pincode]):
                address_text = f"{name}, {phone}, {address}, {city}, {state} - {pincode}"
            else:
                raise ValueError("Missing address information")
        
        if not payment_mode:
            raise ValueError("Payment mode is required")
        
        # Handle coupon validation and discount
        used_coupon = None
        discount_amount = Decimal('0')
        
        if coupon_id:
            try:
                user_coupon = UserCoupon.objects.get(
                    id=coupon_id,
                    user=request.user,
                    is_used=False,
                    coupon__start_date__lte=timezone.now().date(),
                    coupon__end_date__gte=timezone.now().date()
                )
                used_coupon = user_coupon
                # Mark coupon as used
                user_coupon.is_used = True
                user_coupon.used_date = timezone.now()
                user_coupon.save()
                
            except UserCoupon.DoesNotExist:
                messages.error(request, "Invalid or expired coupon selected")
                return redirect('checkout')
        
        stock_issue = False
        total_order_amount = Decimal('0')
        
        # First pass: calculate total order amount and check stock
        for item in cart_items:
            product = item.product
            
            if product.quantity < item.quantity:
                messages.error(request, f"Not enough stock for {product.name}. Only {product.quantity} available.")
                stock_issue = True
                continue
            
            # GST calculations using Decimal
            gst_percentage = Decimal(product.gst_percentage or 0)
            base_price = Decimal(product.price) * item.quantity
            gst_amount = (base_price * gst_percentage / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_price_with_gst = (base_price + gst_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            total_order_amount += total_price_with_gst
        
        if stock_issue:
            # If coupon was marked as used, revert it
            if used_coupon:
                used_coupon.is_used = False
                used_coupon.used_date = None
                used_coupon.save()
            return redirect('view_cart')
        
        # Apply coupon discount (10% of total order)
        if used_coupon:
            discount_amount = (total_order_amount * Decimal('10') / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Second pass: create purchases with applied discount
        for item in cart_items:
            product = item.product
            
            # GST calculations using Decimal
            gst_percentage = Decimal(product.gst_percentage or 0)
            base_price = Decimal(product.price) * item.quantity
            gst_amount = (base_price * gst_percentage / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_price_with_gst = (base_price + gst_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Calculate proportional discount for this item
            item_discount = Decimal('0')
            if discount_amount > 0:
                item_discount = (total_price_with_gst * discount_amount / total_order_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            final_price = total_price_with_gst - item_discount
            
            # Create purchase record
            purchase = Purchase.objects.create(
                user=request.user,
                product=product,
                quantity=item.quantity,
                date_bought=timezone.now(),
                delivery_address=address_text,
                payment_mode=payment_mode,
                gst_percentage=gst_percentage,
                gst_amount=gst_amount,
                total_price_with_gst=final_price,  # Final price after discount
                coupon_used=used_coupon.coupon.code if used_coupon else None,
                discount_amount=item_discount
            )
            
            # Send invoice email
            subject = f"Invoice for your purchase of {product.name}"
            to_email = request.user.email
            context = {
                'purchase': purchase,
                'coupon_discount': item_discount if item_discount > 0 else None,
                'original_total': total_price_with_gst
            }
            message = render_to_string('invoice_template.html', context)
            
            email = EmailMessage(subject, message, to=[to_email])
            email.content_subtype = "html"  # Send as HTML
            
            try:
                email.send()
            except Exception as e:
                print(f"Failed to send invoice email for {product.name}: {e}")
            
            # Update stock and remove from cart
            product.quantity -= item.quantity
            product.save()
            item.delete()
        
        success_message = "Your order has been placed successfully!"
        if used_coupon:
            success_message += f" You saved ₹{discount_amount} with coupon {used_coupon.coupon.code}!"
        
        messages.success(request, success_message)
        return redirect('bought_items')
    
    except (Address.DoesNotExist, ValueError) as e:
        # If coupon was marked as used during error, revert it
        if 'used_coupon' in locals() and used_coupon:
            used_coupon.is_used = False
            used_coupon.used_date = None
            used_coupon.save()
        
        messages.error(request, str(e) or "Please select or provide a valid delivery address")
        return redirect('checkout')


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings

from .models import Purchase


@login_required
def invoice_view(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)

    context = {
        'purchase': purchase
    }

    return render(request, 'invoice_template.html', context)


@login_required
def send_invoice_email(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    subject = f"Invoice for your purchase of {purchase.product.name}"
    to_email = purchase.user.email

    context = {
        'purchase': purchase,
    }

    message = render_to_string('invoice_template.html', context)

    email = EmailMessage(subject, message, to=[to_email])
    email.content_subtype = "html"  # Send as HTML

    try:
        email.send()
        return HttpResponse("Invoice email sent successfully.")
    except Exception as e:
        return HttpResponse(f"Error sending invoice: {e}")


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone

from .models import CartItem, Address, Purchase, Product





@login_required
def buy_now_checkout(request, product_id):
    """
    Creates a temporary cart with only the selected product for checkout
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.quantity <= 0:
        if hasattr(request, 'messages'):
            from django.contrib import messages
            messages.error(request, "This product is out of stock")
        return redirect('view_products')
    
    # Clear any existing cart
    cart = get_user_cart(request)
    CartItem.objects.filter(cart=cart).delete()
    
    # Add this product to cart with quantity 1
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    
    # Redirect to checkout
    return redirect('checkout')









from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Product, Purchase, Wishlist, Cart, CartItem, Category
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json

# Your existing views here (view_products, add_to_cart, etc.)
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Purchase, ReturnRequest

@login_required
def submit_return_request(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        proof_image = request.FILES.get('proof_image')

        ReturnRequest.objects.create(
            user=request.user,
            product_name=purchase.product.name,
            reason=reason,
            proof_image=proof_image
        )

        messages.success(request, 'Return request submitted successfully.')
        return redirect('bought_items')  # Or wherever you want to redirect

    return render(request, 'submit_return_request.html', {
        'product': purchase.product
    })

from django.contrib.admin.views.decorators import staff_member_required
from .models import ReturnRequest

@staff_member_required
def view_return_requests(request):
    requests = ReturnRequest.objects.all().order_by('-submitted_at')
    return render(request, 'admin/view_return_requests.html', {'requests': requests})

@staff_member_required
def approve_return(request, request_id):
    req = ReturnRequest.objects.get(id=request_id)
    req.status = 'Approved'
    req.save()

    send_mail(
        'Return Request Approved',
        f'Hello {req.user.first_name}, your return request for "{req.product_name}" has been approved. A replacement will be sent soon.',
        settings.DEFAULT_FROM_EMAIL,
        [req.user.email],
        fail_silently=False,
    )
    messages.success(request, "Return approved and email sent.")
    return redirect('view_return_requests')

# Add these new views for purchased items and admin orders

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import render
from .models import Purchase, Coupon, UserCoupon
import random

@login_required
def bought_items(request):
    user = request.user
    now = timezone.now()
    start_of_month = now.replace(day=1)
    
    # Purchases of this user ordered by recent first
    purchases = Purchase.objects.filter(user=user).order_by('-date_bought')
    
    # Pagination
    paginator = Paginator(purchases, 9)  # 9 items per page
    page = request.GET.get('page')
    purchases_page = paginator.get_page(page)
    
    # Count of purchases this month
    purchase_count = purchases.filter(date_bought__gte=start_of_month).count()
    
    # Assign 10% coupon if conditions met and coupon not already assigned this month
    if purchase_count > 10:
        already_assigned = UserCoupon.objects.filter(user=user, assigned_date__gte=start_of_month).exists()
        if not already_assigned:
            valid_coupons = Coupon.objects.filter(
                start_date__lte=now.date(),
                end_date__gte=now.date()
            )
            # Filter coupons if you have a discount_percent field, else just pick any
            if valid_coupons.exists():
                selected_coupon = random.choice(valid_coupons)
                UserCoupon.objects.create(user=user, coupon=selected_coupon)
    
    # Get all coupons assigned to this user
    user_coupons = UserCoupon.objects.filter(user=user)
    
    return render(request, 'bought_items.html', {
        'purchases': purchases_page,  # Keep the variable name as 'purchases' to match the template
        'user_coupons': user_coupons,
    })

# Admin views - make sure to protect them with appropriate permissions
def is_admin(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_admin)
def admin_orders(request):
    """Admin view for managing all orders"""
    # Apply filters if provided
    filter_status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Start with all purchases
    orders = Purchase.objects.all().order_by('-date_bought')
    
    # Apply status filter
    if filter_status:
        orders = orders.filter(status=filter_status)
    
    # Apply date range filters
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            orders = orders.filter(date_bought__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the end date fully
            date_to = date_to + timedelta(days=1)
            orders = orders.filter(date_bought__lt=date_to)
        except ValueError:
            pass
    
    # Calculate stats for dashboard
    total_orders = Purchase.objects.count()
    pending_orders = Purchase.objects.filter(status='processing').count()
    delivered_orders = Purchase.objects.filter(status='delivered').count()
    
    # Calculate total revenue (assuming quantity field exists, or default to 1)
    total_revenue = Purchase.objects.aggregate(
        total=Sum(F('product__price') * F('quantity'))
    )['total'] or 0
    
    # If quantity field doesn't exist in your model, use this instead:
    # total_revenue = Purchase.objects.aggregate(total=Sum('product__price'))['total'] or 0
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_revenue': round(total_revenue, 2),
    }
    
    return render(request, 'admin/admin_orders.html', context)


@user_passes_test(is_admin)
def admin_order_details(request):
    """AJAX view to get order details"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id = request.GET.get('order_id')
        if order_id:
            try:
                order = Purchase.objects.get(id=order_id)
                html = render_to_string('admin_order_detail_partial.html', {'order': order})
                return HttpResponse(html)
            except Purchase.DoesNotExist:
                return HttpResponse('<div class="alert alert-danger">Order not found.</div>')
    
    return HttpResponse('<div class="alert alert-danger">Invalid request.</div>')


@user_passes_test(is_admin)
def admin_update_order_status(request):
    """View to update order status"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if order_id and new_status:
            try:
                order = Purchase.objects.get(id=order_id)
                order.status = new_status
                order.admin_notes = notes
                order.last_updated = timezone.now()
                order.save()
                
                # Add success message
                from django.contrib import messages
                messages.success(request, f"Order #{order_id} status updated to {new_status}")
                
                return redirect('admin_orders')
            except Purchase.DoesNotExist:
                from django.contrib import messages
                messages.error(request, "Order not found")
        else:
            from django.contrib import messages
            messages.error(request, "Invalid request parameters")
    
    return redirect('admin_orders')


@user_passes_test(is_admin)
def admin_export_orders(request):
    """Export orders as CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Email', 'Product', 'Quantity', 'Price', 
                    'Date', 'Status', 'Payment Method', 'Delivery Address'])
    
    # Apply filters if provided
    filter_status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Start with all purchases
    orders = Purchase.objects.all().order_by('-date_bought')
    
    # Apply filters (same as in admin_orders view)
    if filter_status:
        orders = orders.filter(status=filter_status)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            orders = orders.filter(date_bought__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            date_to = date_to + timedelta(days=1)
            orders = orders.filter(date_bought__lt=date_to)
        except ValueError:
            pass
    
    for order in orders:
        writer.writerow([
            order.id,
            order.user.get_full_name() or order.user.username,
            order.user.email,
            order.product.name,
            order.quantity if hasattr(order, 'quantity') else 1,
            order.product.price,
            order.date_bought.strftime('%Y-%m-%d %H:%M:%S'),
            order.status,
            order.payment_mode,
            order.delivery_address
        ])
    
    return response







from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, ProductRating, Purchase
from django.contrib.auth.decorators import login_required

@login_required
def submit_rating(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        review_text = request.POST.get('review', '').strip()

        # Ensure user has purchased the product
        if not Purchase.objects.filter(user=request.user, product=product).exists():
            messages.error(request, "You can only rate products you have purchased.")
            return redirect('bought_items')

        # Avoid duplicate rating
        if ProductRating.objects.filter(product=product, user=request.user).exists():
            messages.warning(request, "You already rated this product.")
            return redirect('bought_items')

        # Create the rating and review
        ProductRating.objects.create(
            product=product,
            user=request.user,
            rating=rating_value,
            review=review_text
        )

        messages.success(request, "Thank you for rating this product!")

    return redirect('bought_items')



def dealer_orders(request):
    return render(request, 'dealer/orders.html')









# 21 may tuesday
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Coupon
from datetime import datetime

@login_required
def manage_coupons(request):
    if request.user.is_superuser:  # Allow only admin
        if request.method == "POST":
            name = request.POST.get('name')
            code = request.POST.get('code')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            if name and code and start_date and end_date:
                Coupon.objects.create(
                    name=name,
                    code=code,
                    start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                    end_date=datetime.strptime(end_date, "%Y-%m-%d").date()
                )
            return redirect('manage_coupons')
    
    coupons = Coupon.objects.all().order_by('-start_date')
    return render(request, 'admin/manage_coupons.html', {'coupons': coupons})


from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Purchase, Coupon, UserCoupon
import random
from django.contrib.auth.decorators import login_required

@login_required
def user_coupons(request):
    user = request.user
    now = timezone.now()
    start_of_month = now.replace(day=1)

    # Count purchases this month
    purchase_count = Purchase.objects.filter(user=user, date_bought__gte=start_of_month).count()

    # If user made more than 10 purchases this month and no coupon assigned yet
    if purchase_count > 10:
        already_assigned = UserCoupon.objects.filter(
            user=user,
            assigned_date__gte=start_of_month
        ).exists()

        if not already_assigned:
            valid_coupons = Coupon.objects.filter(
                discount_percent=10,
                start_date__lte=now.date(),
                end_date__gte=now.date()
            )
            if valid_coupons.exists():
                selected_coupon = random.choice(valid_coupons)
                UserCoupon.objects.create(user=user, coupon=selected_coupon)

    # Get all coupons assigned to the user
    coupons = UserCoupon.objects.filter(user=user)

    return render(request, 'user_coupons.html', {'coupons': coupons})










from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EmailSubscriber  # Ensure this model exists

def subscribe_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            subscriber, created = EmailSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'You have successfully subscribed to product updates!')
            else:
                messages.info(request, 'You are already subscribed.')
        else:
            messages.error(request, 'Please enter a valid email address.')
        return redirect('subscribe_user')
    return render(request, 'subscribe.html')







from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Message
from django.contrib.auth import get_user_model
from django.db.models import Q  # Correct import

User = get_user_model()

@login_required
def chat_with_admin(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if request.method == 'POST':
        msg = request.POST.get('message')
        if msg:
            Message.objects.create(sender=request.user, receiver=admin_user, message=msg)
            return redirect('chat_with_admin')

    # ✅ Correct use of Q instead of models.Q
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=admin_user)) |
        (Q(sender=admin_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    return render(request, 'chat_with_admin.html', {'messages': messages})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Message

User = get_user_model()

@login_required
def admin_chat(request):
    # List all users except the admin (assuming admin is request.user)
    users = User.objects.exclude(id=request.user.id)

    # Get user_id from URL params
    user_id = request.GET.get('user_id')

    chat_user = None
    messages = []

    if user_id:
        chat_user = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            msg = request.POST.get('message')
            if msg:
                Message.objects.create(sender=request.user, receiver=chat_user, message=msg)
                return redirect(f"{request.path}?user_id={chat_user.id}")

        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=chat_user)) |
            (Q(sender=chat_user) & Q(receiver=request.user))
        ).order_by('timestamp')

    context = {
        'users': users,
        'chat_user': chat_user,
        'messages': messages,
    }
    return render(request, 'admin/admin_chat.html', context)



from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Example logic: delivery in 3 to 5 days
    if request.user.is_authenticated:
        estimated_delivery = (date.today() + timedelta(days=4)).strftime('%B %d, %Y')
    else:
        estimated_delivery = None

    return render(request, 'product_detail.html', {
        'product': product,
        'estimated_delivery': estimated_delivery
    })








from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import Hub, DeliveryAgent

import random
import string

def generate_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def add_delivery_agent_view(request):
    if request.method == 'POST':
        hub_id = request.POST.get('hub')  # Select which hub the delivery agent belongs to
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        vehicle_number = request.POST.get('vehicle_number')
        license = request.POST.get('license')

        if DeliveryAgent.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)
        if DeliveryAgent.objects.filter(phone=phone).exists():
            return JsonResponse({'error': 'Phone number already registered'}, status=400)

        try:
            hub = Hub.objects.get(id=hub_id)
        except Hub.DoesNotExist:
            return JsonResponse({'error': 'Invalid HUB selected'}, status=400)

        password = generate_password()

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name,is_delivery_agent=True)
        user.save()

        agent = DeliveryAgent.objects.create(
            hub=hub,
            user=user,
            name=name,
            phone=phone,
            email=email,
            address=address,
            vehicle_number=vehicle_number,
            license=license,
        )

        send_mail(
            subject='Delivery Agent Account Created',
            message=f'Your delivery agent account has been created.\nUsername: {email}\nPassword: {password}',
            from_email='admin@yourdomain.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return JsonResponse({'message': 'Delivery agent added successfully and credentials sent via email.'})

    hubs = Hub.objects.all()
    return render(request, 'hub/delivery_agent_form.html', {'hubs': hubs})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def delivery_agent_dashboard(request):
    return render(request, 'delivery/delivery_agent_dashboard.html')






from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Hub, Branch, DeliveryAgent

@login_required
def hub_dashboard(request):
    user = request.user

    if not hasattr(user, 'is_hub') or not user.is_hub:
        return render(request, '403.html')  # Optional: Create a 'Forbidden' page

    try:
        hub = Hub.objects.get(email=user.email)
    except Hub.DoesNotExist:
        return render(request, '404.html', {'message': 'Hub not found.'})

    branch_count = Branch.objects.filter(hub=hub).count()
    agent_count = DeliveryAgent.objects.filter(hub=hub).count()

    context = {
        'hub': hub,
        'branch_count': branch_count,
        'agent_count': agent_count,
    }
    return render(request, 'hub/hub_dashboard.html', context)

















# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from .models import Hub, Branch
import random
import string
import json

User = get_user_model()

def generate_password(length=8):
    """Generate a random password"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hub_branch_management(request):
    """Main view that renders the single page with both forms"""
    hubs = Hub.objects.all().values('id', 'name', 'email', 'city')
    return render(request, 'admin/hub_branch_management.html', {
        'hubs': list(hubs)
    })

def add_hub_view(request):
    """Handle hub creation via AJAX"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            address = request.POST.get('address')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            pin_code = request.POST.get('pin_code')
            district = request.POST.get('district')
            state = request.POST.get('state')
            city = request.POST.get('city')

            # Validate required fields
            if not all([name, address, email, phone, pin_code, district, state, city]):
                return JsonResponse({
                    'error': 'All fields are required'
                }, status=400)

            # Check if email already exists
            if Hub.objects.filter(email=email).exists():
                return JsonResponse({
                    'error': 'Email already registered'
                }, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'error': 'Email already exists in user accounts'
                }, status=400)

            # Create hub
            hub = Hub.objects.create(
                name=name,
                address=address,
                email=email,
                phone=phone,
                pin_code=pin_code,
                district=district,
                state=state,
                city=city
            )

            # Generate password and create user account
            password = generate_password()

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            user.is_hub = True  # Mark user as hub
            user.save()

            # Send email with credentials
            try:
                send_mail(
                    subject='HUB Account Created - Login Credentials',
                    message=f'''
Dear {name},

Your HUB account has been successfully created!

Login Credentials:
• Username: {email}
• Password: {password}
• Login URL: {request.build_absolute_uri('/login/')}

Please keep these credentials secure and change your password after first login.

Hub Details:
• Name: {name}
• Address: {address}
• Phone: {phone}
• City: {city}, {state}

Best regards,
Admin Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'HUB added successfully and credentials sent via email!',
                    'hub': {
                        'id': hub.id,
                        'name': hub.name,
                        'email': hub.email,
                        'city': hub.city
                    }
                })
                
            except Exception as e:
                # If email fails, still return success but mention email issue
                return JsonResponse({
                    'success': True,
                    'message': f'HUB added successfully, but email delivery failed. Please contact admin.',
                    'hub': {
                        'id': hub.id,
                        'name': hub.name,
                        'email': hub.email,
                        'city': hub.city
                    }
                })

        except Exception as e:
            return JsonResponse({
                'error': f'An error occurred: {str(e)}'
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def add_branch_view(request):
    """Handle branch creation via AJAX"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            hub_id = request.POST.get('hub')
            address = request.POST.get('address')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            pin_code = request.POST.get('pin_code')
            district = request.POST.get('district')
            state = request.POST.get('state')
            city = request.POST.get('city')

            # Validate required fields
            if not all([name, hub_id, address, email, phone, pin_code, district, state, city]):
                return JsonResponse({
                    'error': 'All fields are required'
                }, status=400)

            # Check if email already exists
            if Branch.objects.filter(email=email).exists():
                return JsonResponse({
                    'error': 'Email already registered'
                }, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'error': 'Email already exists in user accounts'
                }, status=400)

            # Get hub
            try:
                hub = Hub.objects.get(id=hub_id)
            except Hub.DoesNotExist:
                return JsonResponse({
                    'error': 'Selected hub does not exist'
                }, status=400)

            # Create branch
            branch = Branch.objects.create(
                hub=hub,
                name=name,
                address=address,
                email=email,
                phone=phone,
                pin_code=pin_code,
                district=district,
                state=state,
                city=city,
            )

            # Generate password and create user account
            password = generate_password()

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            user.is_branch = True  # Mark user as branch
            user.save()

            # Send email with credentials
            try:
                send_mail(
                    subject='Branch Account Created - Login Credentials',
                    message=f'''
Dear {name},

Your Branch account has been successfully created under {hub.name}!

Login Credentials:
• Username: {email}
• Password: {password}
• Login URL: {request.build_absolute_uri('/login/')}

Please keep these credentials secure and change your password after first login.

Branch Details:
• Name: {name}
• Hub: {hub.name}
• Address: {address}
• Phone: {phone}
• City: {city}, {state}

Best regards,
Admin Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Branch added successfully and credentials sent via email!',
                    'branch': {
                        'id': branch.id,
                        'name': branch.name,
                        'email': branch.email,
                        'hub_name': hub.name
                    }
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': True,
                    'message': f'Branch added successfully, but email delivery failed. Please contact admin.',
                    'branch': {
                        'id': branch.id,
                        'name': branch.name,
                        'email': branch.email,
                        'hub_name': hub.name
                    }
                })

        except Exception as e:
            return JsonResponse({
                'error': f'An error occurred: {str(e)}'
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_hubs_api(request):
    """API endpoint to get all hubs for dropdown population"""
    if request.method == 'GET':
        hubs = Hub.objects.all().values('id', 'name', 'email', 'city')
        return JsonResponse({
            'success': True,
            'hubs': list(hubs)
        })
    return JsonResponse({'error': 'Invalid request method'}, status=405)





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Hub

# Manage all branches view
def manage_branches_view(request):
    branches = Branch.objects.all()
    return render(request, 'hub/manage_branches.html', {'branches': branches})

# Handle editing a branch (from modal form)
def edit_branch_view(request, id):
    if request.method == 'POST':
        branch = get_object_or_404(Hub, id=id)
        branch.name = request.POST.get('name')
        branch.location = request.POST.get('location')
        branch.contact_number = request.POST.get('contact_number')
        branch.email = request.POST.get('email')
        branch.save()
        messages.success(request, 'Branch updated successfully!')
    return redirect('manage_branches')

# Handle deleting a branch (from modal form)
def delete_branch_view(request, id):
    if request.method == 'POST':
        branch = get_object_or_404(Hub, id=id)
        branch.delete()
        messages.success(request, 'Branch deleted successfully!')
    return redirect('manage_branches')





#tuesday  27/05/25




from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import render
from .models import Purchase, Coupon, UserCoupon
import random

def is_superuser_check(user):
    return user.is_superuser  # or your custom logic



@user_passes_test(is_superuser_check)
def purchase_admin_view(request):
    all_purchases = Purchase.objects.all().order_by('-date_bought')
    paginator = Paginator(all_purchases, 15)
    page_number = request.GET.get('page')
    paged_all_purchases = paginator.get_page(page_number)
    return render(request, 'admin/purchases_overview.html', {'purchases': paged_all_purchases})



# Updated hub_purchase_list_view with assignment functionality
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
import uuid
from .models import Purchase, Branch, Parcel, DeliveryAgent, Hub  # adjust imports as needed

def hub_purchase_list_view(request):
    if not request.user.is_authenticated or not request.user.is_hub:
        return redirect('login')  # or handle unauthorized access

    # Get hub associated with logged-in user
    hub = get_object_or_404(Hub, email=request.user.email)

    # Handle POST (assignments)
    if request.method == 'POST':
        purchase_id = request.POST.get('purchase_id')
        action = request.POST.get('action')
        purchase = get_object_or_404(Purchase, id=purchase_id)

        if action == 'assign_to_branch':
            branch_id = request.POST.get('branch_id')
            branch = get_object_or_404(Branch, id=branch_id, hub=hub)  # ensure branch belongs to current hub

            if not purchase.parcel:
                parcel = Parcel.objects.create(
                    tracking_number=f"TRK{uuid.uuid4().hex[:8].upper()}",
                    sender="Hub",
                    recipient=purchase.user.username,
                    hub=hub,
                )
                purchase.parcel = parcel

            purchase.assigned_branch = branch
            purchase.status = 'assigned_to_branch'
            purchase.parcel.assigned_branch = branch
            purchase.parcel.status = 'Assigned to Branch'
            purchase.parcel.save()
            purchase.save()

            messages.success(request, f'Purchase assigned to branch: {branch.name}')

        elif action == 'assign_to_agent':
            agent_id = request.POST.get('agent_id')
            agent = get_object_or_404(DeliveryAgent, id=agent_id)

            purchase.assigned_delivery_agent = agent
            purchase.status = 'assigned_to_agent'
            if purchase.parcel:
                purchase.parcel.status = 'Assigned to Delivery Agent'
                purchase.parcel.save()
            purchase.save()

            messages.success(request, f'Purchase assigned to delivery agent: {agent.name}')

        return redirect('hub_purchase_list')

    # GET request
    purchases = Purchase.objects.all().order_by('-date_bought')
    paginator = Paginator(purchases, 15)
    page_number = request.GET.get('page')
    paged_purchases = paginator.get_page(page_number)

    # Filter branches for the current hub only
    branches = Branch.objects.filter(hub=hub)

    # You can filter agents too if needed
    delivery_agents = DeliveryAgent.objects.all()

    context = {
        'purchases': paged_purchases,
        'branches': branches,
        'delivery_agents': delivery_agents,
    }
    return render(request, 'hub/purchase_list.html', context)



# Branch view to see assigned parcels and assign to delivery agents

@login_required
def branch_assigned_parcels_view(request):
    user_branch = None

    # Attempt to get user branch/hub
    # Adjust these attribute names depending on your user model & relations:
    if hasattr(request.user, 'customuser') and hasattr(request.user.customuser, 'hub'):
        user_branch = request.user.customuser.hub
    elif hasattr(request.user, 'hub'):
        user_branch = request.user.hub
    else:
        # fallback if you have a Branch model linked by email
        try:
            from .models import Branch
            branch = Branch.objects.filter(email=request.user.email).first()
            if branch:
                user_branch = branch.hub
        except ImportError:
            pass

    if not user_branch:
        # Show all purchases if user not tied to hub
        purchases_queryset = Purchase.objects.filter(
            status__in=['assigned_to_branch', 'assigned_to_agent', 'out_for_delivery']
        ).order_by('-date_bought')
        delivery_agents = DeliveryAgent.objects.all()
        branch_hub_name = "All Hubs"
    else:
        # Filter by user_branch
        purchases_queryset = Purchase.objects.filter(
            assigned_branch__hub=user_branch,
            status__in=['assigned_to_branch', 'assigned_to_agent', 'out_for_delivery']
        ).order_by('-date_bought')
        delivery_agents = DeliveryAgent.objects.filter(hub=user_branch)
        branch_hub_name = user_branch.name

    if request.method == 'POST':
        purchase_id = request.POST.get('purchase_id')
        action = request.POST.get('action')
        purchase = get_object_or_404(Purchase, id=purchase_id)

        if action == 'assign_to_agent':
            agent_id = request.POST.get('agent_id')
            agent = get_object_or_404(DeliveryAgent, id=agent_id)

            # Check if agent belongs to same hub as user_branch or no branch
            if not user_branch or agent.hub == user_branch:
                purchase.assigned_delivery_agent = agent
                purchase.status = 'assigned_to_agent'
                if purchase.parcel:
                    purchase.parcel.status = 'Assigned to Delivery Agent'
                    purchase.parcel.save()
                purchase.save()
                messages.success(request, f'Purchase assigned to delivery agent: {agent.name}')
            else:
                messages.error(request, 'Selected delivery agent is not from your hub.')

        elif action == 'mark_out_for_delivery':
            purchase.status = 'out_for_delivery'
            if purchase.parcel:
                purchase.parcel.status = 'Out for Delivery'
                purchase.parcel.save()
            purchase.save()
            messages.success(request, 'Order marked as out for delivery.')

        return redirect('branch_assigned_parcels')

    paginator = Paginator(purchases_queryset, 15)
    page_number = request.GET.get('page')
    paged_purchases = paginator.get_page(page_number)

    context = {
        'purchases': paged_purchases,
        'delivery_agents': delivery_agents,
        'branch_hub': user_branch,
        'branch_hub_name': branch_hub_name,
    }

    return render(request, 'branch/branch_assigned_parcels.html', context)






from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import DeliveryAgent, Purchase

@login_required
def assigned_orders_view(request):
    try:
        agent = DeliveryAgent.objects.get(user=request.user)
    except DeliveryAgent.DoesNotExist:
        return HttpResponse("You are not registered as a delivery agent.", status=403)

    assigned_orders = Purchase.objects.filter(assigned_delivery_agent=agent).order_by('-id')
    return render(request, 'delivery/assigned_orders.html', {'assigned_orders': assigned_orders})




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Purchase

@login_required
def admin_assigned_orders_view(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)
    assigned_orders = Purchase.objects.filter(assigned_delivery_agent__isnull=False).order_by('-id')
    return render(request, 'admin/assigned_orders_admin.html', {'assigned_orders': assigned_orders})

@login_required
def hub_assigned_orders_view(request):
    if not request.user.is_hub:
        return HttpResponse("Unauthorized", status=403)
    assigned_orders = Purchase.objects.filter(assigned_delivery_agent__isnull=False).order_by('-id')
    return render(request, 'hub/assigned_orders_hub.html', {'assigned_orders': assigned_orders})





from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevents logout after password change
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Purchase, DeliveryAgent
from django.http import HttpResponseForbidden

@login_required
def update_delivery_info(request, order_id):
    purchase = get_object_or_404(Purchase, id=order_id)

    # Ensure this order belongs to the delivery agent
    try:
        agent = DeliveryAgent.objects.get(user=request.user)
    except DeliveryAgent.DoesNotExist:
        return HttpResponseForbidden("Not a delivery agent.")

    if purchase.assigned_delivery_agent != agent:
        return HttpResponseForbidden("Not assigned to this order.")

    if request.method == 'POST':
        status = request.POST.get('status')
        current_location = request.POST.get('current_location')
        delivery_date = request.POST.get('delivery_date')

        purchase.status = status
        purchase.current_location = current_location
        purchase.delivery_date = delivery_date
        purchase.save()

        return redirect('assigned_orders')  # Change to your assigned orders URL name

    return render(request, 'delivery/update_delivery_info.html', {'purchase': purchase})





















from .models import Purchase, Coupon, UserCoupon,Parcel
@login_required
def assign_parcel_to_branch(request, parcel_id):
    parcel = get_object_or_404(Parcel, id=parcel_id)
    hub = parcel.hub
    branches = Branch.objects.filter(hub=hub)

    if request.method == 'POST':
        branch_id = request.POST.get('assigned_branch')
        status = request.POST.get('status', 'At Hub')

        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id, hub=hub)
                parcel.assigned_branch = branch
                parcel.status = status
                parcel.save()
                return redirect('parcels_list')  # redirect to list after assign
            except Branch.DoesNotExist:
                error = "Selected branch is invalid."
        else:
            error = "Please select a branch."

        return render(request, 'hub/assign_parcel.html', {
            'parcel': parcel,
            'branches': branches,
            'error': error,
            'selected_branch': branch_id,
            'status': status,
        })

    return render(request, 'hub/assign_parcel.html', {
        'parcel': parcel,
        'branches': branches,
        'selected_branch': parcel.assigned_branch.id if parcel.assigned_branch else None,
        'status': parcel.status,
    })


@login_required
def parcels_list(request):
    hub = getattr(request.user, 'hub', None)
    if not hub:
        return render(request, 'hub/parcel_list.html', {
            'parcels': [],
            'error_message': 'You are not assigned to any Hub.'
        })

    parcels = Parcel.objects.filter(hub=hub).order_by('-created_at')
    print(f"Hub: {hub}, Parcels count: {parcels.count()}")  # Debug log

    paginator = Paginator(parcels, 10)
    page_number = request.GET.get('page')
    parcels_page = paginator.get_page(page_number)

    return render(request, 'hub/parcel_list.html', {
        'parcels': parcels_page,
    })
