from django.urls import path
from accounts.views import custom_login
from . import views

urlpatterns= [
    path('', views.home, name="home"),
    path('<str:ref_by>', views.home, name= "home"),
    path('search/', views.search, name= "search"),
    path('search/<str:ref_by>', views.search, name= "search"),
    path('info/<int:pk>/<str:ref_by>', views.info, name= "info"),
    path('info/<int:pk>/', views.info, name= "info"),
    path('add-product/', views.add_product, name= "add-product"),
    path('edit-product/<int:pk>', views.EditProduct.as_view(), name= "edit-product"),
    path('delete-product/<int:pk>', views.DelProduct.as_view(), name= "delete-product"),
    path('info/<int:pk>/add-image/', views.add_product_image, name= "add-image"),
    path('change-image/<int:pk>', views.ChangeImage.as_view(), name= "change-image"),
    path('del-image/<int:pk>', views.DelImage.as_view(), name= "del-image"),
    path('quote-request/', views.quote_request, name= "quote-request"),
    path('quote-list/', views.quote_list, name= "quote-list"),
    path('quote-search/', views.quote_list_search, name= "quote-search"),
    path('my-quote/', views.my_quotes, name= "my-quote"),
    path('myquote_search/', views.quote_search, name= "myquote-search"),
    path('quote-info/<int:pk>', views.quote_info, name= "quote-info"),
    path('quote-info/<int:pk>/staff-price/', views.staff_price_quote, name= "staff-price"),
    path('edit-quote/<int:pk>', views.EditQuote.as_view(), name= "edit-quote"),
    path('delete-quote/<int:pk>', views.DelQuote.as_view(), name= "delete-quote"),
    path('edit-quoteimage/<int:pk>', views.EditQuoteImage.as_view(), name= 'edit-quoteimage'),
    path('delete-quoteimage/<int:pk>', views.DelQuoteImage.as_view(), name= "delete-quoteimage"),
    path('info/<int:pk>/offer-info/<int:pk2>', views.offer_info, name= "offer-info"),
    path('info/<int:pk>/init-cart/', views.init_cart_purchase, name= "init-cart"),
    path('info/<int:pk>/init-cart/add-to-cart/<int:pk4>', views.add_cart, name="add-to-cart"),
    path('info/<int:pk>/init-cart/rem-fro-cart/<int:pk4>', views.remove_cart, name="rem-fro-cart"),
    path('auto-delete/<int:pk>', views.auto_delete, name= "auto-delete"),
    path('delete-pc/<int:pk>', views.DelProdCart.as_view(), name= "delete-pc"),
    path('add-offer/', views.AddOffer.as_view(), name= "add-offer"),
    path('edit-offer/<int:pk>', views.EditOffer.as_view(), name= "edit-offer"),
    path('delete-offer/<int:pk>', views.DelOffer.as_view(), name= "delete-offer"),
    path('profile/', views.profile, name= "profile"),
    path('profile-edit/<int:pk>', views.ProfileEdit.as_view(), name= "profile-edit"),
    path('add-bank/', views.add_bank, name= "add-bank" ),
    path('edit-bank/<int:pk>', views.EditBank.as_view(), name= "edit-bank"),
    path('delete-bank/<int:pk>', views.DeleteBank.as_view(), name= "delete-bank"),
    path('bank-details/', views.bank_details_upload, name= "bank-details"),
    path('bank-edit/<int:pk>', views.BankEdit.as_view(), name= "bank-edit"),
    path('bank-delete/<int:pk>', views.BankDelete.as_view(), name= "bank-delete"),
    path('withdraw/<int:pk>', views.withdraw, name= "withdraw"),
    path('withdraw-history/', views.withdrawal_history, name= "withdraw-history"),
    path('paystack-keys/', views.paystack_keys, name="paystack-keys"),
    path('paystack/', views.AddPaystack.as_view(), name= "paystack"),
    path('paystack-edit/<int:pk>', views.PaystackEdit.as_view(), name= "paystack-edit"),
    path('add-cat/', views.AddCat.as_view(), name= "add-cat"),
    path('edit-cat/', views.EditCat.as_view(), name= "edit-cat"),
    path('delete-cat/', views.DelCat.as_view(), name= "delete-cat"),
    path('trans-hist/', views.transaction_history, name="trans-hist"),
    path('init-payment/<int:pk>', views.initialize_payment, name= "init-payment"),
    path('verify-payment/<str:ref>', views.verify_payment, name= "verify-payment"),
    path('verify-cart/<str:ref>', views.verify_cartpayment, name= "verify-cart"),
    path('cart/', views.shopping_cart, name="cart"),
    path('addcart/', views.addcart, name="addcart"),
    path('delete-cart/<int:pk>', views.DelCart.as_view(), name="delete-cart"),
    path('paycart/<int:pk>', views.payforshoppingcart, name="paycart"),
    path('orders/', views.cust_order, name= "orders"),
    path('order-info/<int:pk>', views.order_info, name="order-info"),
    path('ordercart-info/<int:pk>', views.ordercart_info, name="ordercart-info"),
    path('add-location/', views.add_address, name="add-location"),
    path('email-setup/', views.email_setup, name="email-setup"),
    path('emailsetup-edit/<int:pk>', views.EditEmailSetup.as_view(), name="emailsetup-edit"),
    path('add-email/', views.add_email, name="add-email"),
    path('add-whatsapp/', views.add_whatsapp, name="add-whatsapp"),
    path('send-mail/', views.send_email_message, name="send-mail"),
    path('customer-info/', views.customer_info, name="customer-info"),
    path('bulktransfer/', views.bulktransfer, name="bulktransfer"),
    path('blog-page/', views.blog_page, name= "blog-page"),
    path('blog-search/', views.blog_search, name= "blog-search"),
    path('add-blog/', views.AddBlog.as_view(), name= "add-blog"),
    path('edit-blog/<int:pk>', views.EditBlog.as_view(), name= "edit-blog"),
    path('del-blog/<int:pk>', views.DelBlog.as_view(), name= "del-blog"),
    path('post-detail/<int:pk>', views.post_details, name= "post-detail"),
    path('add-blogcat/', views.AddBlogCat.as_view(), name= "add-blogcat"),
    path('del-blogcat/<int:pk>', views.DelBlogCat.as_view(), name= "del-blogcat"),
    path('accounts/login/', custom_login, name= "login"),
    path('profiles-details/', views.profiles_details, name="profiles-details"),
    path('reset/', views.reset_field_to_zero, name="reset"),
    path('about-us/', views.about_us, name="about-us"),
    path('about-us/<str:ref_by>', views.about_us, name="about-us"),
    path('contact/', views.social_accounts, name="contact"),
    path('contact/<str:ref_by>', views.social_accounts, name="contact"),
    path('add-about/', views.AddAboutUs.as_view(), name="add-about"),
    path('add-social/', views.AddSocial.as_view(), name="add-social"),
    path('edit-about/<int:pk>', views.EditAbout.as_view(), name="edit-about"),
    path('edit-social/<int:pk>', views.EditSocial.as_view(), name="edit-social"),
    path('del-about/<int:pk>', views.DelAbout.as_view(), name="del-about"),
    path('del-social/<int:pk>', views.DelSocial.as_view(), name="del-social"),
    path('add-staff/', views.AddStaff.as_view(), name="add-staff"),
    path('edit-staff/<int:pk>', views.EditStaff.as_view(), name="edit-staff"),
    path('del-staff/<int:pk>', views.DelStaff.as_view(), name="del-staff"),
    path('remove-ref/<int:pk>', views.remove_ref, name="remove-ref"),
    path('add-reset/', views.AddReset.as_view(), name="add-reset"),
    path('edit-reset/<int:pk>', views.EditReset.as_view(), name="edit-reset"),
    path('add-guide/', views.AddGuide.as_view(), name="add-guide"),
    path('edit-guide/<int:pk>', views.EditGuide.as_view(), name="edit-guide"),
    path('add-address/', views.AddAddress.as_view(), name="add-address"),
    path('edit-address/<int:pk>', views.EditAddress.as_view(), name="edit-address"),
    path('edit-permissions/', views.edit_permissions, name= "edit-permissions"),
    path('edit-profit/<int:pk>', views.EditProfit.as_view(), name="edit-profit"),
    path('withdraw-profit/<int:pk>', views.withdraw_profit, name= "withdraw-profit"),
    path('company-withdraw/<int:pk>', views.initiate_company_withdrawal, name="company-withdraw"),
    path('add-company/', views.add_companyaccount, name= "add-company"),
    path('edit-company/<int:pk>', views.edit_companyaccount, name="edit-company"),
    path('edit-profit/<int:pk>', views.EditProfit.as_view(), name="edit-profit"),
    path('company-drawhist/', views.company_drawhist, name="company-drawhist"),
    path('del-paycart/<int:pk>', views.DelPaycart.as_view(), name= "del-paycart"),
    path('del-payment/<int:pk>', views.DelPayment.as_view(), name= "del-payment"),
    path('del-comm/<int:pk>', views.DelComm.as_view(), name= "del-comm"),
]
