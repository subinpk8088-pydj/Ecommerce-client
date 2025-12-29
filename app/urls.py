#Hospital management django

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
   
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('blog/', views.blog, name='blog'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),




    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
   
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    
    path('products/add/', views.add_product, name='add_product'),
    
     path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('users/', views.admin_users, name='admin_users'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

     path('help/', views.admin_help, name='admin_help'),
      path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
     path('products/', views.view_products, name='view_products'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('purchased/', views.bought_items, name='bought_items'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('purchases/', views.bought_items, name='bought_items'),
    path('buy-page/<int:product_id>/', views.buy_page, name='buy_page'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
    path('buy-now-checkout/<int:product_id>/', views.buy_now_checkout, name='buy_now_checkout'),
    
    
    
    # Admin URLs - make sure to protect these with proper permission checks
    path('orders/', views.admin_orders, name='admin_orders'),
    path('orders/details/', views.admin_order_details, name='admin_order_details'),
    path('orders/update-status/', views.admin_update_order_status, name='admin_update_order_status'),
    path('orders/export/', views.admin_export_orders, name='admin_export_orders'),
    
    
    path('rate-product/<int:product_id>/', views.submit_rating, name='submit_rating'),
    path('validate/', views.validate_field, name='validate_field'),
    path('manage-addresses/', views.manage_addresses, name='manage_addresses'),
    path('set_default_address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    
    
    
    # Admin dealer approval URLs
    path('dealers/pending/', views.pending_dealers, name='pending_dealers'),
    path('dealers/approve/<int:user_id>/', views.approve_dealer, name='approve_dealer'),
    
    # Dealer dashboard URLs
    

    path('dealer/dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('orders/', views.dealer_orders, name='dealer_orders'),

     path('invoice/<int:purchase_id>/', views.invoice_view, name='invoice_view'),
    path('send-invoice/<int:purchase_id>/', views.send_invoice_email, name='send_invoice_email'),
    
    
    # 21 may tuesday
     path('manage-coupons/', views.manage_coupons, name='manage_coupons'),
     
     path('coupons/', views.user_coupons, name='user_coupons'),
     
      # 22 may tuesday
     path('subscribe/', views.subscribe_user, name='subscribe_user'),
     
     
     path('return/<int:purchase_id>/', views.submit_return_request, name='submit_return_request'),
    path('view-returns/', views.view_return_requests, name='view_return_requests'),
    path('approve-return/<int:request_id>/', views.approve_return, name='approve_return'),
    
    
    path('change-password/', views.change_password, name='change_password'),
    
path('view-assigned-orders-admin/', views.admin_assigned_orders_view, name='view_assigned_orders_admin'),
path('view-assigned-orders-hub/', views.hub_assigned_orders_view, name='view_assigned_orders_hub'),

    
     path('chat-with-admin/', views.chat_with_admin, name='chat_with_admin'),
     
path('chat/', views.admin_chat, name='admin_chat'),
 path('product/<int:product_id>/', views.product_detail, name='product_detail'),
 
  path('add-hub/', views.add_hub_view, name='add_hub'),
  path('add-branch/', views.add_branch_view, name='add_branch'),
path('add_delivery_agent/', views.add_delivery_agent_view, name='add_delivery_agent'),
path('hub/dashboard/', views.hub_dashboard, name='hub_dashboard'),


 path('branch/dashboard/', views.branch_dashboard, name='branch_dashboard'),
path('delivery-dashboard/', views.delivery_agent_dashboard, name='delivery_agent_dashboard'),


path('hub-branch-management/', views.hub_branch_management, name='hub_branch_management'),
path('api/hubs/', views.get_hubs_api, name='get_hubs_api'),



path('manage_branches/', views.manage_branches_view, name='manage_branches'),

path('edit_branch/<int:id>/', views.edit_branch_view, name='edit_branch'),
path('delete_branch/<int:id>/', views.delete_branch_view, name='delete_branch'),


#tuesday  27/05/25


path('purchases-overview/', views.purchase_admin_view, name='purchase_admin_view'),
path('hub/purchases/', views.hub_purchase_list_view, name='hub_purchase_list'),

path('parcels/', views.parcels_list, name='parcels_list'),
path('parcel/<int:parcel_id>/assign/', views.assign_parcel_to_branch, name='assign_parcel'),



path('assigned-parcels/', views.branch_assigned_parcels_view, name='branch_assigned_parcels'),


path('assigned-orders/', views.assigned_orders_view, name='assigned_orders'),
path('update-order/<int:order_id>/', views.update_delivery_info, name='update_delivery_info'),



path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
]
