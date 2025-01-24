from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Product, Category, Profile, Offer, Payment, Bank, Banks, Transfer, PaystackKeys, Profit, Blog, Blog_cat, Cart2, PayCart, Location, EmailSet, Alertmail, About, Socials, CallMeBot, ContactInfo, Staff, Reset, WhatsappReset, InstructionBot, Permission, Permissions, Testimony, WithdrawProfit, CompanyAccount, ProductCart, Prod_image, Quote, Quote_image
import uuid
from datetime import date, datetime
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from .forms import ProductEdit, Blog_cat, BlogEdit, BlogForm
import requests
from django.contrib import messages
from decimal import Decimal
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils import timezone
from django.db.models import Sum
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request, **kwargs):
    ref_by= str(kwargs.get("ref_by"))
    abouts= About.objects.all()
    staffs= Staff.objects.all()
    testimonies= Testimony.objects.all()
    contact= None
    if Socials.objects.filter(pk=1).exists():
        contact= Socials.objects.get(pk=1)
    
    contact_info= None
    if ContactInfo.objects.filter(pk=1).exists():
        contact_info= ContactInfo.objects.get(pk=1)
    products= Product.objects.all()
    for product in products:
        prod_images= Prod_image.objects.filter(product= product)
    if request.method == 'POST':
        text= request.POST['text']
        testimony= Testimony.objects.create(user=request.user, text=text)
        testimony.save()
        return redirect('home')
    context= {
        'products': products,
        'prod_images': prod_images,
        'abouts': abouts,
        'staffs': staffs,
        'contact': contact,
        'contact_info': contact_info,
        'testimonies': testimonies,
        'ref_by': ref_by
    }
    return render(request, 'home.html', context)

def auto_delete(request, pk):
    offer= Offer.objects.get(pk=pk)
    offer.delete()
    return redirect('home')

def add_cart(request, pk, pk4):
    cart= Cart2.objects.get(pk=pk4)
    product= ProductCart.objects.get(pk=pk)
    cart.product.add(product)
    return redirect('info', product.pk)

def remove_cart(request, pk, pk4):
    cart= Cart2.objects.get(pk=pk4)
    product= ProductCart.objects.get(pk=pk)
    cart.product.remove(product)
    return redirect('info', product.pk)

def remove_ref(request, pk):
    profile=Profile.objects.get(pk=pk)
    profile2= Profile.objects.get(recommendations= request.user)
    profile.rec_by= None
    profile2.recommendations.remove(request.user)
    profile.save()
    profile2.save()
    return redirect('profile')

def init_cart_purchase(request, pk):
    cart= Cart2.objects.get(user=request.user)
    product= Product.objects.get(pk=pk)
    productcart= ProductCart.objects.filter(product=product.name, user=request.user)
    if request.method == 'POST':
        quantity= int(request.POST['quantity'])
        if ProductCart.objects.filter(product= product.name, user=request.user).exists():
            messages.info(request, 'already exists; delete the previous below')
        elif product.discount is not None:
            if product.commission is not None:
                commission= product.commission/100 * product.discount
                ProductCart.objects.create(user=request.user, product=product.name, price= product.discount*quantity, quantity= quantity, commission= commission)
                return redirect('init-cart', product.pk)
            else:
                ProductCart.objects.create(user=request.user, product=product.name, price= product.discount*quantity, quantity= quantity, commission= 0)
                return redirect('init-cart', product.pk)
        else:
            if product.ref_discount != None and product.commission != None:
                if Profile.objects.filter(recommendations= request.user).exists():
                    price= product.price - (product.ref_discount/100 * product.price)
                    commission= product.commission/100 * price
                    ProductCart.objects.create(user=request.user, product=product.name, price= price*quantity, quantity= quantity, commission= commission)
                    return redirect('init-cart', product.pk)
                else:
                    commission= product.commission/100 * product.price
                    ProductCart.objects.create(user=request.user, product=product.name, price= product.price*quantity, quantity= quantity, commission= commission)
                    return redirect('init-cart', product.pk)
            elif product.commission is not None:
                commission= product.commission/100 * product.price
                ProductCart.objects.create(user=request.user, product=product.name, price= product.price*quantity, quantity= quantity, commission= commission)
                return redirect('init-cart', product.pk)
            else:
                ProductCart.objects.create(user=request.user, product=product.name, price= product.price*quantity, quantity= quantity, commission= 0)
                return redirect('init-cart', product.pk)
    context= {
        'productcarts': productcart,
        'cart': cart
    }
    return render(request, 'init-cart.html', context)

class DelProdCart(DeleteView):
    model= ProductCart
    template_name= "delete-pc.html"
    success_url= reverse_lazy('home') 

def info(request, pk, **kwargs):
    ref_by= str(kwargs.get("ref_by"))
    profilez= None
    if request.user.is_authenticated and Profile.objects.filter(user=request.user).exists():
        profilez= Profile.objects.get(user=request.user)
    else:
        profilez= None
    abouts= About.objects.all()
    staffs= Staff.objects.all()
    contact= None
    if Socials.objects.filter(pk=1).exists():
        contact= Socials.objects.get(pk=1)
    
    contact_info= None
    if ContactInfo.objects.filter(pk=1).exists():
        contact_info= ContactInfo.objects.get(pk=1)
    profile= None
    if Profile.objects.filter(code=ref_by).exists():
        profile= Profile.objects.get(code=ref_by)
    else:
        profile= None
    
    product= Product.objects.get(pk=pk)
    prod_images= Prod_image.objects.filter(product= product)
    mess= ''
    if product.ref_discount and profile is not None:
        mess= f'congrats you qualify for a {product.ref_discount}% discount on this product'
    ref= str(uuid.uuid4()).replace("-", "")[:7]
    offers= Offer.objects.all()
    offer= ''
    total_price= None
    carts= None
    if request.user.is_authenticated and Cart2.objects.filter(user=request.user).exists():
        carts= Cart2.objects.filter(user=request.user)
        for cart in carts:
            for cart in carts:
                total_price= cart.product.aggregate(total_price=Sum('price'))['total_price']
    else:
        carts=None

    today= timezone.now()
    seconds= ''

    if Offer.objects.filter(product=product).exists():
        offer= Offer.objects.get(product=product)
        product.discount= product.price - (offer.discount_percentage/100 * product.price)
        time_diff= offer.valid_till - today
        seconds = time_diff.total_seconds()
        product.save()
    elif Offer.objects.filter(product=product).exists() == False:
        product.discount= None
        seconds= ''
        product.save()

    if request.method == 'POST':
        quantity= int(request.POST['quantity'])
        try:
            if product.discount:
                if product.ref_discount is not None and Profile.objects.filter(recommendations= request.user).exists():
                    amount= (product.discount-(product.ref_discount/100*product.discount))*quantity
                    payment= Payment.objects.create(user= request.user, product= product.name, amount= amount, ref= ref)
                    return redirect('init-payment', payment.pk)
                else:
                    amount= product.discount*quantity
                    payment= Payment.objects.create(user= request.user, product= product.name, amount= amount, ref= ref)
                    return redirect('init-payment', payment.pk)
            elif product.ref_discount is not None and Profile.objects.filter(recommendations= request.user).exists():
                amount = (product.price-(product.ref_discount/100*product.price))*quantity
                payment= Payment.objects.create(user= request.user, product= product.name, amount= amount, ref= ref, email= request.user.email)
                return redirect('init-payment', payment.pk)
            else:
                amount = product.price*quantity
                payment= Payment.objects.create(user= request.user, product= product.name, amount= amount, ref= ref, email= request.user.email)
                return redirect('init-payment', payment.pk)
        except:
            messages.info(request, 'register on the website or login to purchase')

    context= {
        'product': product,
        'prod_images': prod_images,
        'offers': offers,
        'offer': offer,
        'ref_by': ref_by,
        'seconds': seconds,
        'today': today,
        'carts': carts,
        'profile': profile,
        'profilez': profilez,
        'mess': mess,
        'abouts': abouts,
        'staffs': staffs,
        'contact': contact,
        'contact_info': contact_info,
        'total_price': total_price
    }
    return render(request, "info.html", context)

def add_product_image(request, pk):
    product= Product.objects.get(pk=pk)
    if request.method== 'POST':
        image1= request.FILES['image']
        prod_image= Prod_image.objects.create(product= product, image= image1)
        prod_image.save()
        return redirect('info', product.pk)
    return render(request, 'add-images.html')

class ChangeImage(UpdateView):
    model= Prod_image
    template_name= "change-image.html"
    fields= ('image',)

class DelImage(DeleteView):
    model= Prod_image
    template_name= "del-image.html"
    success_url= reverse_lazy('home')

def quote_request(request):
    try:
        if request.method== 'POST':
            desc= request.POST['description']
            image= request.FILES['image']
            phone= request.POST['phone']
            quote= Quote.objects.create(user= request.user, first_name= request.user.first_name, last_name= request.user.last_name, email= request.user.email, phone= phone, image= image, quote= desc)
            quote.save()
            try:
                email_owner= None
                if EmailSet.objects.filter(pk=1).exists():
                    email_owner= EmailSet.objects.get(pk=1)
                    alertmails= Alertmail.objects.all()
                    for alertmail in alertmails:    
                        # Email configuration
                        sender_email = email_owner.email_address
                        receiver_email = alertmail.email_address
                        password = email_owner.email_password

                        # Create message container
                        message = MIMEMultipart()
                        message['From'] = sender_email
                        message['To'] = receiver_email
                        message['Subject'] = 'Order Notification'

                        # Email content
                        body = f'you"ve received a quote order from {request.user.first_name} {request.user.last_name} on the website'
                        message.attach(MIMEText(body, 'plain'))

                        # Create SMTP session
                        with smtplib.SMTP('smtp.gmail.com', 587) as server:
                            server.starttls()
                            server.login(sender_email, password)
                            text = message.as_string()
                            server.sendmail(sender_email, receiver_email, text)
            except:
                messages.info(request, 'unable to connect to gmail server')

            try:
                callmebots= CallMeBot.objects.all()
                for callmebot in callmebots:
                    phonenumber = f"+{callmebot.phone_number}"
                    text = f'you"ve received a quote order from {request.user.first_name} {request.user.last_name} on the website'
                    apikey = callmebot.api_key

                    url = "https://api.callmebot.com/whatsapp.php"
                    params = {
                        "phone": phonenumber,
                        "text": text,
                        "apikey": apikey
                    }

                    response = requests.post(url, params=params)
            except:
                messages.info(request, 'unable to connect to CallMeBot')
            return redirect('my-quote')
    except:
        messages.info(request, 'log in or sign up to request a quote')
    return render(request, 'quote-request.html')

@login_required
def my_quotes(request):
    quotes= Quote.objects.filter(user=request.user).order_by('-date')
    context= {
        'quotes': quotes
    }
    return render(request, 'my-quote.html', context)

@login_required
def quote_list(request):
    quotes= Quote.objects.all().order_by('-date')
    context= {
        'quotes': quotes
    }
    return render(request, 'quote-list.html', context)

def quote_info(request, pk):
    quote= Quote.objects.get(pk=pk)
    quote_images= Quote_image.objects.filter(quote=quote)
    if request.method == 'POST':
        image= request.FILES['image']
        quote_image= Quote_image.objects.create(quote=quote, image=image)
        quote_image.save()
        return redirect('quote-info', quote.pk)
    context= {
        'quote_images': quote_images,
        'quote': quote
    }
    return render(request, 'quote-info.html', context)

def staff_price_quote(request, pk):
    quote= Quote.objects.get(pk=pk)
    if request.method == 'POST':
        price= float(request.POST['price'])
        quote.price= price
        quote.save()
        try:
            email_owner= None
            if EmailSet.objects.filter(pk=1).exists():
                email_owner= EmailSet.objects.get(pk=1)
                # Email configuration
                sender_email = email_owner.email_address
                receiver_email = quote.email
                password = email_owner.email_password

                # Create message container
                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = receiver_email
                message['Subject'] = 'Respnse to Quote Request'

                # Email content
                body = f'Dear {request.user.first_name} {request.user.last_name}, your quote request stated "{quote.quote}" has been answered with a price of {price}. Log into www.wwatech.com for more info'
                message.attach(MIMEText(body, 'plain'))

                # Create SMTP session
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    text = message.as_string()
                    server.sendmail(sender_email, receiver_email, text)
        except:
            messages.info(request, 'unable to connect to gmail server')
        return redirect('quote-info', quote.pk)
    return render(request, 'staff-price.html')

class EditQuote(UpdateView):
    model= Quote
    template_name= 'edit-quote.html'
    fields= ('image', 'quote', 'phone')

class DelQuote(DeleteView):
    model= Quote
    template_name= 'delete-quote.html'
    success_url= reverse_lazy('my-quote')

class EditQuoteImage(UpdateView):
    model= Quote_image
    template_name= 'edit-quoteimage.html'
    fields= ('image',)

class DelQuoteImage(DeleteView):
    model= Quote_image
    template_name= 'delete-quoteimage.html'
    success_url= reverse_lazy('my-quote')

def quote_list_search(request):
    search= request.GET['search']
    quotes= Quote.objects.filter(last_name__icontains=search) or Quote.objects.filter(first_name__icontains=search)
    context= {
        'search': search,
        'quotes': quotes
    }
    return render(request, "quote-search.html", context)

def quote_search(request):
    search= request.GET['search']
    quotes= Quote.objects.filter(quote__icontains=search)
    context= {
        'search': search,
        'quotes': quotes
    }
    return render(request, "myquote-search.html", context)

def search(request, **kwargs):
    ref_by= str(kwargs.get("ref_by"))
    search= request.GET['search']
    products= Product.objects.filter(name__icontains=search)
    testimonies= Testimony.objects.all()
    if request.method == 'POST':
        text= request.POST['text']
        testimony= Testimony.objects.create(user=request.user, text=text)
        testimony.save()
        return redirect('home')

    context= {
        'ref_by': ref_by,
        'search': search,
        'products': products,
        'testimonies': testimonies
    }
    return render(request, 'search.html', context)

@login_required
def offer_info(request, pk, pk2):
    product= Product.objects.get(pk=pk)
    offer= Offer.objects.get(pk= pk2)

    if request.method == 'POST':
        if product in offer.product.all():
            offer.product.remove(product)
            return redirect('info', product.pk)
        else:
            offer.product.add(product)
            return redirect('info', product.pk)
    context= {
        'product': product,
        'offer': offer
    }
    return render(request, 'offer-info.html', context)


@login_required
def add_product(request):
    category= Category.objects.all()
    if request.method== 'POST':
        image= request.FILES['image']
        video= request.FILES['video']
        name = request.POST['name']
        description= request.POST['description']
        price= request.POST['price']
        quantity= request.POST['quantity']
        category= request.POST['category']
        commission= request.POST['commission']
        ref_discount= request.POST['ref_discount']
        if commission== '':
            product= Product.objects.create(image=image, video=video, name=name, description=description, price=price, quantity=quantity, category=category)
            product.save()
            return redirect('home')
        elif ref_discount== '':
            product= Product.objects.create(image=image, name=name, description=description, price=price, quantity=quantity, category=category, commission=commission)
            product.save()
            return redirect('home')
        else:
            product= Product.objects.create(image=image, name=name, description=description, price=price, quantity=quantity, category=category, commission=commission, ref_discount=ref_discount)
            product.save()
            return redirect ('home')
    
    context= {
        'catogories': category
    }
    return render(request, 'add-product.html', context)

class EditProduct(UpdateView):
    model= Product
    template_name= "edit-product.html"
    form_class= ProductEdit


class DelProduct(DeleteView):
    model= Product
    template_name= "delete-product.html"
    success_url= reverse_lazy('home')


class AddOffer(CreateView):
    model= Offer
    template_name= "add-offer.html"
    fields= ('discount_percentage', 'valid_till')


class EditOffer(UpdateView):
    model= Offer
    template_name= "edit-offer.html"
    fields= ('discount_percentage', 'valid_till')


class DelOffer(DeleteView):
    model= Offer
    template_name= "delete-offer.html"
    success_url= reverse_lazy('home')

def withdraw_profit(request, pk):
    profit= Profit.objects.get(pk=1)
    company= CompanyAccount.objects.get(pk=pk)
    transfer_code= str(uuid.uuid4()).replace("-", "")[:7]
    banks= Banks.objects.get(bank_name=company.bank_name)
    if request.method == 'POST':
        amount= int(request.POST['amount'])
        if amount > profit.amount:
            messages.info(request, 'insufficient, this is above your balance')
        else:
            withdraw= WithdrawProfit.objects.create(user= request.user, amount=amount, recipient=banks.name, transfer_code= transfer_code, bank_name= banks.bank_name, account_number= company.account_number, recipient_name= company.account_name)
            return redirect('company-withdraw', withdraw.pk)
    context= {
        'profit': profit
    }
    return render(request, 'withdraw-profit.html', context)

def initiate_company_withdrawal(request, pk):
    withdraw= WithdrawProfit.objects.get(pk=pk)
    bank= Banks.objects.get(bank_name=withdraw.bank_name)
    paystack= PaystackKeys.objects.get(pk=1)
    paystack_secretkey= paystack.secret_key
    profit= Profit.objects.get(pk=1)
    headers= {
        "Authorization": 'Bearer ' + paystack_secretkey,
        "Content-Type": 'application/json'
    }
    payload = {
        'source': 'balance',
        'amount': withdraw.amount * 100,  # Amount in kobo (1 NGN = 100 kobo)
        'recipient': withdraw.recipient,
        'transfer_code': withdraw.transfer_code,
        'bank_code': bank.code,
        'account_number': withdraw.account_number,
        'recipient_name': withdraw.recipient_name,
    }
    url= 'https://api.paystack.co/transfer'
    if request.method == 'POST':
        try:
            response= requests.post(url, json=payload, headers= headers)
            res_json= response.json()
            messages.info(request, res_json)
            if res_json['status'] == False:
                withdraw.status= "Failed"
                withdraw.save()
                # return redirect('withdraw-history')
            else:
                withdraw.status= "successful"
                profit.amount -= withdraw.amount
                withdraw.save()
                profit.save()
                # return redirect('withdraw-history')
        except:
            messages.info(request, 'error: check if bank details are correct')
    context= {
        'withdraw':withdraw
    }
    return render(request, 'company-withdraw.html', context)

def add_companyaccount(request):
    banks= Banks.objects.all()
    if request.method== 'POST':
        bank_name= request.POST['bank_name']
        account_name= request.POST['account_name']
        account_number= request.POST['account_number']
        company= CompanyAccount.objects.create(user=request.user, bank_name= bank_name, account_name=account_name, account_number=account_number, email= request.user.email)
        return redirect('profile')
    context= {
        'banks': banks
    }
    return render(request, 'add-company.html', context)

def edit_companyaccount(request, pk):
    company= CompanyAccount.objects.get(pk=pk)
    banks= Banks.objects.all()
    if request.method== 'POST':
        bank_name= request.POST['bank_name']
        account_name= request.POST['account_name']
        account_number= request.POST['account_number']
        company.bank_name= bank_name
        company.account_name= account_name
        company.account_number= account_number
        company.save()
        return redirect('profile')
    context= {
        'company': company,
        'banks': banks
    }
    return render(request, 'edit-company.html', context)


@login_required
def profile(request):
    expired= request.session.get_expiry_date()
    expired_date= timezone.localtime(expired)
    seconds= None
    today= timezone.now()
    company= None
    if CompanyAccount.objects.filter(pk=1).exists():
        company= CompanyAccount.objects.get(pk=1)
    permission= Permission.objects.get(pk=1)
    profit= Profit.objects.get(pk=1)
    reset= None
    if Reset.objects.filter(pk=1).exists():
        reset= Reset.objects.get(pk=1)
    profile= Profile.objects.get(user= request.user)
    if profile.rec_by is not None:
        time_diff= expired_date - today
        seconds = time_diff.total_seconds()
    email_setup= None
    if EmailSet.objects.filter(pk=1).exists():
        email_setup= EmailSet.objects. get(pk=1)
    address= 'Add address for easy delivery of products'
    if Location.objects.filter(user=request.user).exists():
        address= Location.objects.get(user=request.user)
    transfer_code= str(uuid.uuid4()).replace("-", "")[:7]
    if Bank.objects.filter(user=request.user).exists():
        bank= Bank.objects.get(user=request.user)
        bank2= Banks.objects.get(bank_name=bank.bank_name)
    else:
        bank= None
    
    if request.method == 'POST':
        if bank is not None:
            transfer= Transfer.objects.create(user= request.user, amount= profile.earnings, recipient= bank2.name, transfer_code= transfer_code, bank_code= bank2.code, account_number= bank.account_number, recipient_name= bank.account_name)
            transfer.save()
            return redirect('withdraw', transfer.pk)
        else:
            messages.info(request, 'upload bank details first')
    
    guide= None
    if InstructionBot.objects.filter(pk=1).exists():
        guide= InstructionBot.objects.get(pk=1)
        
    context= {
        'profile': profile,
        'bank': bank,
        'address': address,
        'reset': reset,
        'guide': guide,
        'email_setup': email_setup,
        'permission': permission,
        'profit': profit,
        'company': company,
        'seconds': seconds,
        'expired': expired
    }
    return render(request, 'profile.html', context)

class ProfileEdit(UpdateView):
    model= Profile
    template_name= "edit-profile.html"
    fields= ('image', 'telephone')

@login_required
def add_bank(request):
    res_json= None
    try:
        paystack= PaystackKeys.objects.get(pk=1)
        paystack_secretkey= paystack.secret_key
        headers= {
            "Authorization": 'Bearer ' + paystack_secretkey,
            "Content-Type": 'application/json'
        }
        url= 'https://api.paystack.co/bank'
        response= requests.get(url, headers= headers)
        res_json= response.json()
    except:
        messages.info(request, "unable to get bank slugs and codes")
    
    banks= Banks.objects.all()

    if request.method == 'POST':
        bank_name= request.POST['bank_name']
        name= request.POST['name']
        code= request.POST['code']

        if Banks.objects.filter(name=name).exists():
            messages.info(request, 'bank already registered')
        else:
            banks= Banks.objects.create(bank_name=bank_name, name=name, code=code)
            return redirect(profile)

    context= {
        'banks': banks,
        'res_json': res_json
    }
    return render(request, 'add-bank.html', context)

class EditBank(UpdateView):
    model= Banks
    template_name= "edit-bank.html"
    fields= '__all__'

class DeleteBank(DeleteView):
    model= Banks
    template_name= "delete-bank.html"
    success_url= reverse_lazy('profile')

@login_required
def bank_details_upload(request):
    banks= Banks.objects.all()
    profile= Profile.objects.get(user=request.user)

    if request.method == 'POST':
        bank_name= request.POST['bank_name']
        account_name= request.POST['account_name']
        account_number= request.POST['account_number']

        if Bank.objects.filter(account_number=account_number).exists() and Bank.objects.filter(bank_name= bank_name).exists():
            messages.info(request, 'Details already exists')
        else:
            bank= Bank.objects.create(user= request.user, transfer_amount= profile.earnings, bank_name=bank_name, account_name=account_name, account_number=account_number, email= request.user.email)
            bank.save()
            return redirect('profile')
    
    context= {
        'banks': banks,
    }
    return render(request, "bank-details.html", context)

class BankEdit(UpdateView):
    model= Bank
    template_name= "bank-edit.html"
    fields= ('account_name', 'account_number')

class BankDelete(DeleteView):
    model= Bank
    template_name= "bank-delete.html"
    success_url= reverse_lazy('profile')

class AddCat(CreateView):
    model= Category
    template_name= "add-cat.html"
    fields= ('name',)

    def get_absolute_url(self):
        return reverse('home')

class EditCat(UpdateView):
    model= Category
    template_name= "edit-cat.html"
    fields= ('name',)

class DelCat(DeleteView):
    model= Category
    template_name= "delete-cat.html"
    success_url= reverse_lazy('home')

@login_required
def transaction_history(request):
    payments= Payment.objects.filter(user= request.user).order_by('-date')
    paycart= PayCart.objects.filter(user=request.user).order_by('-date')
    context= {
        'payments': payments,
        'paycarts': paycart
    }
    return render(request, 'trans-hist.html', context) 

@login_required
def initialize_payment(request, pk):
    payment= Payment.objects.get(pk=pk)
    paystack= PaystackKeys.objects.get(pk=1)
    redirect= None
    paystack_publickey= paystack.public_key
    paystack_secretkey= paystack.secret_key
    headers= {
        "Authorization": 'Bearer ' + paystack_secretkey,
        "Content-Type": 'application/json'
    }
    url= 'https://api.paystack.co/transaction/verify/'
    response= requests.get(url + payment.ref, headers= headers)
    res_json= response.json()
    if res_json['status'] == True:
        redirect= True
    else:
        redirect= False

    context= {
        'payment': payment,
        'public_key': paystack_publickey,
        'redirect': redirect
    }
    return render (request, 'init-payment.html', context)

@login_required
def verify_payment(request, ref):
    payment= Payment.objects.get(ref=ref)
    product= Product.objects.get(name= payment.product)
    paystack= PaystackKeys.objects.get(pk=1)
    paystack_secretkey= paystack.secret_key
    headers= {
        "Authorization": 'Bearer ' + paystack_secretkey,
        "Content-Type": 'application/json'
    }
    url= 'https://api.paystack.co/transaction/verify/'
    response= requests.get(url + payment.ref, headers= headers)
    res_json= response.json()
    if res_json['status'] == True:
        payment.transaction= "successful"
        if product.quantity != 0:
            product.quantity -= payment.quantity
            product.save()
        payment.save()
    else:
        payment.transaction= "unsuccessful"
        payment.save()
    
    if res_json['status'] == True:
        try:
            email_owner= None
            if EmailSet.objects.filter(pk=1).exists():
                email_owner= EmailSet.objects.get(pk=1)
                alertmails= Alertmail.objects.all()
                for alertmail in alertmails:    
                    # Email configuration
                    sender_email = email_owner.email_address
                    receiver_email = alertmail.email_address
                    password = email_owner.email_password

                    # Create message container
                    message = MIMEMultipart()
                    message['From'] = sender_email
                    message['To'] = receiver_email
                    message['Subject'] = 'Order Notification'

                    # Email content
                    body = 'An order was placed on your website'
                    message.attach(MIMEText(body, 'plain'))

                    # Create SMTP session
                    with smtplib.SMTP('smtp.gmail.com', 587) as server:
                        server.starttls()
                        server.login(sender_email, password)
                        text = message.as_string()
                        server.sendmail(sender_email, receiver_email, text)
        except:
            messages.info(request, 'unable to connect to gmail server')

        if res_json['status'] == True:
            try:
                callmebots= CallMeBot.objects.all()
                for callmebot in callmebots:
                    phonenumber = f"+{callmebot.phone_number}"
                    text = "You Receive an order"
                    apikey = callmebot.api_key

                    url = "https://api.callmebot.com/whatsapp.php"
                    params = {
                        "phone": phonenumber,
                        "text": text,
                        "apikey": apikey
                    }

                    response = requests.post(url, params=params)
            except:
                messages.info(request, 'unable to connect to CallMeBot')

    
    profit= Profit.objects.get(pk=1)
    bank= None
    
    if payment.transaction == "successful":
        if Profile.objects.filter(recommendations= request.user).exists() and product.commission is not None:
            ref_profile= Profile.objects.get(recommendations= request.user)
            ref_user= User.objects.get(username=ref_profile.name)
            if Bank.objects.filter(user=ref_user).exists():
                ref_profile.earnings += product.commission/100 * payment.amount
                profit.amount += payment.amount - (product.commission/100*payment.amount)
                bank= Bank.objects.get(user=ref_user)
                bank.transfer_amount += product.commission/100 * payment.amount
                bank.save()
                ref_profile.save()
                profit.save()
            else:
                ref_profile.earnings += product.commission/100 * payment.amount
                profit.amount += payment.amount - (product.commission/100*payment.amount)
                ref_profile.save()
                profit.save()
        else:
          profit.amount += payment.amount
          profit.save()
    context= {
        'response': response.json,
        'payment': payment
    }
    return render(request, 'verify.html', context)


def blog_page(request):
    blogs= Blog.objects.all().order_by('-pub_date')
    cats= Blog_cat.objects.all()
    context= {
        'blogs': blogs,
        'cats': cats
    }
    return render(request, 'blog-page.html', context)

class AddBlog(CreateView):
    model= Blog
    template_name= "add-blog.html"
    form_class= BlogForm

class EditBlog(UpdateView):
    model= Blog
    template_name= "edit-blog.html"
    form_class= BlogEdit

class DelBlog(DeleteView):
    model= Blog
    template_name= "del-blog.html"
    success_url= reverse_lazy('home')

class AddBlogCat(CreateView):
    model= Blog_cat
    template_name= "add-blogcat.html"
    fields= '__all__'

class DelBlogCat(DeleteView):
    model= Blog_cat
    template_name= "del-blogcat.html"
    success_url= reverse_lazy('home')


def post_details(request, pk):
    blog= Blog.objects.get(pk=pk)
    cats= Blog_cat.objects.all()
    context= {
        'blog': blog,
        'cats': cats
    }
    return render(request, 'post-details.html', context)

@login_required
def withdraw(request, pk):
    paystack= PaystackKeys.objects.get(pk=1)
    paystack_secretkey= paystack.secret_key
    transfer= Transfer.objects.get(pk=pk)
    profile= Profile.objects.get(user= transfer.user)
    headers= {
        "Authorization": 'Bearer ' + paystack_secretkey,
        "Content-Type": 'application/json'
    }
    payload = {
        'source': 'balance',
        'amount': transfer.amount * 100,  # Amount in kobo (1 NGN = 100 kobo)
        'recipient': transfer.recipient,
        'transfer_code': transfer.transfer_code,
        'bank_code': transfer.bank_code,
        'account_number': transfer.account_number,
        'recipient_name': transfer.recipient_name,
    }
    url= 'https://api.paystack.co/transfer'
    if request.method == 'POST':
        try:
            response= requests.post(url, json=payload, headers= headers)
            res_json= response.json()
            messages.info(request, res_json)
            if res_json['status'] == False:
                transfer.status= "Failed"
                transfer.save()
                # return redirect('withdraw-history')
            else:
                transfer.status= "successful"
                profile.earnings= 0
                transfer.save()
                profile.save()
                # return redirect('withdraw-history')
        except:
            messages.info(request, 'error: check if bank details are correct')
        
    context= {
        'transfer': transfer,
    }
    return render(request, 'withdraw.html', context)

@login_required
def withdrawal_history(request):
    transfer= Transfer.objects.filter(user=request.user).order_by('-date')
    transfer1s= Transfer.objects.all()
    withdrawals= WithdrawProfit.objects.all()
    context= {
        'transfers': transfer,
        'transfer1s': transfer1s,
        'withdrawals': withdrawals
    }
    return render(request, 'withdraw-history.html', context)

def company_drawhist(request):
    withdrawals= WithdrawProfit.objects.all()
    context= {
        'withdrawals': withdrawals
    }
    return render(request, 'company-drawhist.html', context)

@login_required
def paystack_keys(request):
    paystack= None
    if PaystackKeys.objects.filter(pk=1).exists():
        paystack= PaystackKeys.objects.get(pk=1)
    context= {
        'paystack':paystack
    }
    return render(request, 'paystack-keys.html', context)


class AddPaystack(CreateView):
    model= PaystackKeys
    template_name= 'paystack.html'
    fields= '__all__'

class PaystackEdit(UpdateView):
    model= PaystackKeys
    template_name= 'paystack-edit.html'
    fields= '__all__'

@login_required
def shopping_cart(request):
    ref= str(uuid.uuid4()).replace("-", "")[:7]
    carts= Cart2.objects.filter(user=request.user)
    total_price= None
    total_com= None
    for cart in carts:
        total_price= cart.product.aggregate(total_price=Sum('price'))['total_price']
        total_com = cart.product.aggregate(total_com=Sum('commission'))['total_com']
        if request.method == 'POST':
            paycart= PayCart.objects.create(user= request.user, cart= cart.name, amount= total_price, commission=total_com, ref= ref)
            return redirect('paycart', paycart.pk)
    
    context= {
        'carts': carts,
        'total_price': total_price,
        'total_com': total_com
    }
    return render(request, 'cart.html', context)

@login_required
def addcart(request):
    if request.method== 'POST':
        name= request.POST['name']
        cart= Cart2.objects.create(user=request.user, name=name)
        return redirect('cart')
    return render(request, 'addcart.html')

class DelCart(DeleteView):
    model= Cart2
    template_name= 'delete-cart.html'
    success_url= reverse_lazy('cart')

@login_required
def payforshoppingcart(request, pk):
    paycart= PayCart.objects.get(pk=pk)
    redirect= None
    paystack= PaystackKeys.objects.get(pk=1)
    paystack_publickey= paystack.public_key
    paystack_secretkey= paystack.secret_key
    headers= {
        "Authorization": 'Bearer ' + paystack_secretkey,
        "Content-Type": 'application/json'
    }
    url= 'https://api.paystack.co/transaction/verify/'
    response= requests.get(url + paycart.ref, headers= headers)
    res_json= response.json()
    if res_json['status'] == True:
        redirect= True
    else:
        redirect= False
    context= {
        'paycart': paycart,
        'public_key':paystack_publickey,
        'redirect': redirect
    }
    return render(request, 'paycart.html', context)

@login_required
def verify_cartpayment(request, ref):
    paycart= PayCart.objects.get(ref=ref)
    paystack= PaystackKeys.objects.get(pk=1)
    paystack_secretkey= paystack.secret_key
    headers= {
        "Authorization": 'Bearer ' + paystack_secretkey,
        "Content-Type": 'application/json'
    }
    url= 'https://api.paystack.co/transaction/verify/'
    response= requests.get(url + paycart.ref, headers= headers)
    res_json= response.json()
    if res_json['status'] == True:
        paycart.transaction= "successful"
        paycart.save()
    else:
        paycart.transaction= "unsuccessful"
        paycart.save()

    if res_json['status'] == True:
        try:
            email_owner= None
            if EmailSet.objects.filter(pk=1).exists():
                email_owner= EmailSet.objects.get(pk=1)
                alertmails= Alertmail.objects.all()
                for alertmail in alertmails:    
                    # Email configuration
                    sender_email = email_owner.email_address
                    receiver_email = alertmail.email_address
                    password = email_owner.email_password

                    # Create message container
                    message = MIMEMultipart()
                    message['From'] = sender_email
                    message['To'] = receiver_email
                    message['Subject'] = 'Order Notification'

                    # Email content
                    body = 'An order was placed on your website'
                    message.attach(MIMEText(body, 'plain'))

                    # Create SMTP session
                    with smtplib.SMTP('smtp.gmail.com', 587) as server:
                        server.starttls()
                        server.login(sender_email, password)
                        text = message.as_string()
                        server.sendmail(sender_email, receiver_email, text)
        except:
            messages.info(request, 'unable to connect to gmail server')

    if res_json['status'] == True:
            try:
                callmebots= CallMeBot.objects.all()
                for callmebot in callmebots:
                    phonenumber = f"+{callmebot.phone_number}"
                    text = "You Receive an order"
                    apikey = callmebot.api_key

                    url = "https://api.callmebot.com/whatsapp.php"
                    params = {
                        "phone": phonenumber,
                        "text": text,
                        "apikey": apikey
                    }

                    response = requests.post(url, params=params)
            except:
                messages.info(request, 'unable to connect to CallMeBot')

    profile= ''
    if Profile.objects.filter(user= request.user).exists():
        profile= Profile.objects.get(user= request.user)
    profit= Profit.objects.get(pk=1)
    
    if paycart.transaction == "successful":
        if Profile.objects.filter(recommendations= request.user).exists() and paycart.commission is not None:
            ref_profile= Profile.objects.get(recommendations= request.user)
            ref_user= User.objects.get(username=ref_profile.name)
            if Bank.objects.filter(user=ref_user).exists():
                ref_profile.earnings += paycart.commission
                profit.amount += paycart.amount - paycart.commission
                bank= Bank.objects.get(user=ref_user)
                bank.transfer_amount += paycart.commission
                bank.save()
                ref_profile.save()
                profit.save()
            else:
                ref_profile.earnings += paycart.commission
                profit.amount += paycart.amount - paycart.commission
                ref_profile.save()
                profit.save()
        else:
          profit.amount += paycart.amount
          profit.save()
          
    context= {
        'response': response.json,
        'paycart': paycart
    }
    return render(request, 'verify-cart.html', context)

@login_required
def cust_order(request):
    payment= Payment.objects.all()
    paycart= PayCart.objects.all()
    context= {
        'payments': payment,
        'paycarts': paycart
    }
    return render(request, 'order.html', context)

@login_required
def order_info(request, pk):
    payment= Payment.objects.get(pk=pk)
    address= 'Not stated'
    if Location.objects.filter(user=payment.user).exists():
        address= Location.objects.get(user=payment.user)
    profile= Profile.objects.get(user=payment.user)
    context= {
        'payment': payment,
        'address': address,
        'profile': profile
    }
    return render(request, 'order-info.html', context)

@login_required
def ordercart_info(request, pk):
    paycart= PayCart.objects.get(pk=pk)
    carts= Cart2.objects.filter(user= paycart.user)
    address= 'Not stated'
    if Location.objects.filter(user=paycart.user).exists():
        address= Location.objects.get(user=paycart.user)
    profile= Profile.objects.get(user=paycart.user)
    for cart in carts:
        total_price= cart.product.aggregate(total_price=Sum('price'))['total_price']
        total_com = cart.product.aggregate(total_com=Sum('commission'))['total_com']
    context= {
        'paycart': paycart,
        'address': address,
        'profile': profile,
        'total_price': total_price,
        'total_com': total_com,
        'carts': carts
    }
    return render(request, 'ordercart-info.html', context)

@login_required
def add_address(request):
    if request.method == 'POST':
        location=request.POST['location']
        address= Location.objects.create(user=request.user, location=location)
        address.save()
        return redirect('profile')
    return render(request, 'add-location.html')

@login_required
def email_setup(request):
    if request.method== 'POST':
        email_address= request.POST['email_address']
        email_password= request.POST['email_password']
        owner_email= EmailSet.objects.create(user=request.user, email_address=email_address, email_password=email_password)
        owner_email.save()
        return redirect('profile')
    return render(request, 'email-setup.html')

@login_required
def add_email(request):
    if request.method== 'POST':
        email_address= request.POST['email_address']
        alertmail= Alertmail.objects.create(user=request.user, email_address=email_address)
        return redirect('profile')
    return render(request, 'add-email.html')

class EditEmailSetup(UpdateView):
    model= EmailSet
    template_name= 'emailsetup-edit.html'
    fields= ('email_address', 'email_password')

@login_required
def add_whatsapp(request):
    if request.method== 'POST':
        phone_number= request.POST['phone_number']
        api_key= request.POST['api_key']
        callmebot= CallMeBot.objects.create(user=request.user, phone_number=phone_number, api_key=api_key)
        return redirect('profile')
    return render(request, 'add-whatsapp.html')

@login_required
def send_email_message(request):
    messages_info= None
    email_owner= EmailSet.objects.get(pk=1)
    profiles= Profile.objects.all()
    if request.method== 'POST':
        subject= request.POST['subject']
        message_send= request.POST['message_send']
        try:
            for profile in profiles:    
                sender_email = email_owner.email_address
                receiver_email = profile.email
                password = email_owner.email_password

                # Create message container
                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = receiver_email
                message['Subject'] = subject

                # Email content
                body = message_send
                message.attach(MIMEText(body, 'plain'))

                # Create SMTP session
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    text = message.as_string()
                    server.sendmail(sender_email, receiver_email, text)
                    messages.info(request, 'message sent successfully')
        except Exception as e:
            messages.info(request, f'Unable to connect to Gmail server: {e}')

    return render(request, 'send-mail.html')

def customer_info(request):
    response= HttpResponse(content_type= 'text/csv')
    response['Content-Disposition']= 'attachment; filename= customers.csv'

    writer= csv.writer(response)

    profiles= Profile.objects.all()

    writer.writerow(['Name', 'Phone Number', 'email'])

    for profile in profiles:
        writer.writerow([profile.name, f'+{profile.telephone}', profile.email])

    return response

def bulktransfer(request):
    response= HttpResponse(content_type= 'text/csv')
    response['Content-Disposition']= 'attachment; filename= bulktransfer.csv'

    writer= csv.writer(response)

    banks= Bank.objects.all()

    writer.writerow(['Transfer Amount', 'Transfer Note(optional)', 'Transfer Reference(optional)', 'Recipient Code', 'Bank Slug', 'Account Number', 'Account Name(optional)', 'Email Address(optional)'])

    for bank in banks:
        bank2= Banks.objects.get(bank_name=bank.bank_name)
        writer.writerow([bank.transfer_amount, bank.transfer_note, bank.transfer_reference, bank.recipient_code, bank2.name, bank.account_number, bank.account_name, bank.email])

    return response

def profiles_details(request):
    profiles= Profile.objects.all()
    total_amount = profiles.aggregate(total_amount=Sum('earnings'))['total_amount']
    context= {
        'profiles':profiles,
        'total': total_amount
    }
    return render(request, 'profiles-details.html', context)

def reset_field_to_zero(request):
    Profile.objects.update(earnings=0)
    Bank.objects.update(transfer_amount=0)
    return redirect('profiles-details')

def about_us(request, **kwargs):
    ref_by= str(kwargs.get("ref_by"))
    abouts= About.objects.all()
    staffs= Staff.objects.all()
    contact= None
    if Socials.objects.filter(pk=1).exists():
        contact= Socials.objects.get(pk=1)
    
    contact_info= None
    if ContactInfo.objects.filter(pk=1).exists():
        contact_info= ContactInfo.objects.get(pk=1)
    
    context= {
        'abouts': abouts,
        'ref_by': ref_by,
        'contact': contact,
        'contact_info': contact_info,
        'staffs': staffs
    }
    return render(request, 'about-us.html', context)

class AddAboutUs(CreateView):
    model= About
    template_name= 'add-about.html'
    fields= '__all__'

class EditAbout(UpdateView):
    model= About
    template_name= "edit-about.html"
    fields= '__all__'

class DelAbout(DeleteView):
    model= About
    template_name= "del-about.html"
    success_url= reverse_lazy('about-us')

def social_accounts(request, **kwargs):
    email_owner= EmailSet.objects.get(pk=1)
    if request.method == 'POST':
        try:
            name= request.POST['name']
            subject= request.POST['subject']
            email= request.POST['email']
            message_send= request.POST['message_send']
            sender_email = email_owner.email_address
            receiver_email = email_owner.email_address
            password = email_owner.email_password

            # Create message container
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Subject'] = f'{subject} from {email}'

            # Email content
            body = f'my name is {name} {message_send}'
            message.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                text = message.as_string()
                server.sendmail(sender_email, receiver_email, text)
                messages.info(request, 'message sent successfully')
        except:
            messages.info(request, 'unable to connect to Gmail Server')

    ref_by= str(kwargs.get("ref_by"))
    contact= None
    if Socials.objects.filter(pk=1).exists():
        contact= Socials.objects.get(pk=1)
    else:
        contact= None
    
    contact_info= None
    if ContactInfo.objects.filter(pk=1).exists():
        contact_info= ContactInfo.objects.get(pk=1)

    context= {
        'contact': contact,
        'ref_by': ref_by,
        'contact_info': contact_info
    }
    return render(request, 'contact-us.html', context)

class AddSocial(CreateView):
    model= Socials
    template_name= 'add-social.html'
    fields= '__all__'

class EditSocial(UpdateView):
    model= Socials
    template_name= "edit-social.html"
    fields= '__all__'

class DelSocial(DeleteView):
    model= Blog
    template_name= "del-social.html"
    success_url= reverse_lazy('home')

class AddStaff(CreateView):
    model= Staff
    template_name= 'add-staff.html'
    fields= '__all__'

class EditStaff(UpdateView):
    model= Staff
    template_name= "edit-staff.html"
    fields= '__all__'

class DelStaff(DeleteView):
    model= Staff
    template_name= "del-staff.html"
    success_url= reverse_lazy('about-us')

class AddReset(CreateView):
    model= Reset
    template_name= 'add-reset.html'
    fields= '__all__'

class EditReset(UpdateView):
    model= Reset
    template_name= 'edit-reset.html'
    fields= '__all__'

class AddGuide(CreateView):
    model= InstructionBot
    template_name= 'add-guide.html'
    fields= '__all__'

class EditGuide(UpdateView):
    model= InstructionBot
    template_name= 'edit-guide.html'
    fields= '__all__'

class AddAddress(CreateView):
    model= ContactInfo
    template_name= 'add-address.html'
    fields= '__all__'

class EditAddress(UpdateView):
    model= ContactInfo
    template_name= 'edit-address.html'
    fields= '__all__'

def edit_permissions(request):
    permissions_lists= Permissions.objects.all()
    permission= Permission.objects.get(pk=1)
    if request.method == 'POST':
        permission_given= request.POST['permission_given']
        permission.permissions= permission_given
        permission.save()
        return redirect('profile')

    context= {
        'permission': permission,
        'permission_lists': permissions_lists
    }
    return render(request, 'permission.html', context)

class EditProfit(UpdateView):
    model= Profit
    template_name= 'edit-profit.html'
    fields= '__all__'

class DelPaycart(DeleteView):
    model= PayCart
    template_name= "del-paycart.html"
    success_url= reverse_lazy('orders')

class DelPayment(DeleteView):
    model= Payment
    template_name= "del-payment.html"
    success_url= reverse_lazy('orders')

class DelComm(DeleteView):
    model= Testimony
    template_name= "del-comm.html"
    success_url= reverse_lazy('home')

def blog_search(request):
    search= request.GET['search']
    blogs= Blog.objects.filter(title__icontains=search)
    cats= Blog_cat.objects.all()
    context= {
        'search': search,
        'blogs': blogs,
        'cats': cats
    }
    return render(request, 'blog-search.html', context)