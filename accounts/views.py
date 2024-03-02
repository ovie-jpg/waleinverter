from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth.models import User, auth
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.contrib import messages
from solar.models import Profile, EmailSet, Reset, WhatsappReset, InstructionBot
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

# Create your views here.

def register(request, **kwargs):
    if request.method == 'POST':
        ref_by= str(kwargs.get('ref_by'))
        code= str(uuid.uuid4()).replace("-", "")[:5]
        username= request.POST['username']
        first_name= request.POST['first_name']
        last_name= request.POST['last_name']
        password1= request.POST['password1']
        password2= request.POST['password2']
        telephone= request.POST['telephone']
        email= request.POST['email']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'username taken')
            elif Profile.objects.filter(code= ref_by).exists():
                user= User.objects.create_user(username= username, first_name= first_name, last_name= last_name, password= password1, email= email)
                ref_profile= Profile.objects.get(code= ref_by)
                ref_user= User.objects.get(username= ref_profile.name)
                ref_profile.recommendations.add(user)
                profile= Profile.objects.create(user= user, name= user.username, code= code, email= user.email, telephone= telephone, rec_by= ref_user)
                user.save()
                ref_profile.save()
                profile.save()
                return redirect(reverse('signin'))
            else:
                user= User.objects.create_user(username= username, first_name= first_name, last_name= last_name, password= password1, email= email)
                profile= Profile.objects.create(user= user, name= user.username, code= code, email= user.email, telephone= telephone)
                user.save()
                profile.save()
                return redirect(reverse('signin'))
        else:
            messages.info(request, 'password not matching')
    return render(request, 'register.html')

def custom_login(request, **kwargs):
    if request.method == 'POST':
        ref_by= str(kwargs.get('ref_by'))
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if Profile.objects.filter(user=user).exists():
            profile= Profile.objects.get(user=user)
        if user is not None:
            if Profile.objects.filter(code=ref_by).exists() and profile.rec_by == None:
                ref_profile= Profile.objects.get(code=ref_by)
                profile.rec_by= ref_profile.user
                ref_profile.recommendations.add(user)
                profile.save()
                ref_profile.save()
                auth.login(request, user)
                return redirect('home')
            else:
                auth.login(request, user)
                return redirect('home')
        else:
            messages.info(request, 'invalid details')

    return render(request, 'login.html')

def reset_password(request, username):
    if request.method == 'POST':
        password1= request.POST['password1']
        password2= request.POST['password2']
        
        user= User.objects.get(username=username)
        if password1==password2:
            user.set_password(password2)
            user.save()
            return redirect('home')
        else:
            messages.info(request, 'password do not match')
    return render(request, 'reset-password.html')

def bot_reset(request):
    guide= None
    if InstructionBot.objects.filter(pk=1).exists():
        guide= InstructionBot.objects.get(pk=1)
    reset= Reset.objects.get(pk=1)
    if request.method=='POST':
        username= request.POST['username']
        apikey= request.POST['apikey']
        if Profile.objects.filter(name=username).exists():
            profile=Profile.objects.get(name=username)
            try:
                phonenumber = f'+{profile.telephone}'
                text = f'click this link to reset your password: {reset.link}{profile.name}'
                apikey = apikey

                url = "https://api.callmebot.com/whatsapp.php"
                params = {
                    "phone": phonenumber,
                    "text": text,
                    "apikey": apikey
                }

                response = requests.post(url, params=params)
                messages.info(request, 'sent successfuly, check your whatsapp')
            except:
                messages.info(request, 'could not send, make sure api key is correct')
        else:
            messages.info(request, 'user does not exist')
    context= {
        'guide': guide
    }
    return render(request, 'bot-reset.html', context)

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        reset = Reset.objects.get(pk=1)
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            email_owner = EmailSet.objects.get(pk=1)
            try:
                sender_email = email_owner.email_address
                receiver_email = user.email
                password = email_owner.email_password

                # Create message container
                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = receiver_email
                message['Subject'] = 'Password reset link'

                # Email content
                body = f'Click this link to reset your password: {reset.link}{username}'
                message.attach(MIMEText(body, 'plain'))

                # Create SMTP session
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    text = message.as_string()
                    server.sendmail(sender_email, receiver_email, text)
                    messages.info(request, 'Reset link sent to email')
            except Exception as e:
                messages.info(request, f'Unable to connect to Gmail server: {e}')
        else:
            messages.info(request, 'Account not found')
            user = None
    return render(request, 'forgot-password.html')

def logout(request):
    auth.logout(request)
    return redirect('home')