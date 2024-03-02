from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    name= models.CharField(max_length= 50)

    def get_absolute_url(self):
        return reverse('home')

class Product(models.Model):
    image= models.ImageField(upload_to= "media")
    name= models.CharField(max_length=150)
    description= models.TextField()
    price= models.IntegerField()
    quantity= models.IntegerField(default=0)
    category= models.TextField()
    commission= models.IntegerField(blank=True, null=True)
    ref_discount= models.IntegerField(blank=True, null=True, default=None)
    discount= models.IntegerField(blank=True, null=True)
    date= models.DateTimeField(auto_now_add= True)

    def get_absolute_url(self):
        return reverse('home')

class Offer(models.Model):
    product= models.ManyToManyField(Product, blank= True)
    discount_percentage= models.IntegerField()
    valid_till= models.DateTimeField()

    def get_absolute_url(self):
        return reverse('home')

class Profile(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    image= models.ImageField(upload_to= "media", blank=True, null=True)
    name= models.CharField(max_length=25)
    code= models.CharField(max_length=5)
    email= models.EmailField()
    telephone= models.IntegerField()
    earnings= models.IntegerField(default= 0)
    rec_by= models.ForeignKey(User, on_delete= models.CASCADE, related_name= "rec_by", null=True)
    recommendations= models.ManyToManyField(User, blank=True, related_name= "recs")

    def get_absolute_url(self):
        return reverse('home')

class Payment(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    product= models.CharField(max_length=25)
    amount= models.IntegerField()
    email= models.EmailField(default='none@gmail.com')
    quantity= models.IntegerField(default=1)
    ref= models.CharField(max_length=7)
    transaction= models.CharField(max_length=25, default= "unconfirmed")
    date= models.DateField(auto_now_add= True)

class Bank(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    transfer_amount= models.IntegerField(default=0)
    transfer_note= models.TextField(blank=True, null=True)
    transfer_reference= models.CharField(max_length=25, blank=True, null=True)
    recipient_code= models.CharField(max_length=25, blank=True, null=True)
    bank_name= models.CharField(max_length=25, default='Not stated')
    bank_slug= models.CharField(max_length=25, blank=True, null=True, default= None)
    bank_code= models.CharField(max_length=25, blank=True, null=True, default= None)
    account_name= models.CharField(max_length=25, blank=True, null=True)
    account_number= models.IntegerField(blank=True, null=True)
    email= models.EmailField()

    def get_absolute_url(self):
        return reverse('home')

class Transfer(models.Model):
    user= models.ForeignKey(User, on_delete= models.CASCADE)
    amount= models.IntegerField()
    recipient= models.CharField(max_length=50)
    transfer_code= models.CharField(max_length=7)
    bank_code= models.CharField(max_length=25)
    account_number= models.IntegerField()
    recipient_name= models.CharField(max_length=200)
    status= models.CharField(max_length=25, blank=True, null= True, default= "unconfirmed")
    date= models.DateTimeField(auto_now_add= True)

    def get_absolute_url(self):
        return reverse('home')

class Banks(models.Model):
    bank_name= models.CharField(max_length=25, default='Not stated')
    name= models.CharField(max_length=25)
    code= models.CharField(max_length=25)

    def get_absolute_url(self):
        return reverse('add-bank')

class Blog_cat(models.Model):
    name= models.CharField(max_length=25)

    def get_absolute_url(self):
        return reverse('blog-page')

class Blog(models.Model):
    image= models.ImageField(upload_to= "media")
    video= models.FileField(upload_to= "media", blank=True, null=True, default=None)
    title= models.CharField(max_length=500)
    description= models.TextField()
    category= models.CharField(max_length=25)
    pub_date= models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('blog-page')

class Profit(models.Model):
    amount= models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('profile')

class CompanyAccount(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    bank_name= models.CharField(max_length=25, default='Not stated')
    bank_slug= models.CharField(max_length=25, blank=True, null=True)
    bank_code= models.CharField(max_length=25, blank=True, null=True)
    account_name= models.CharField(max_length=25, blank=True, null=True)
    account_number= models.IntegerField(blank=True, null=True)
    email= models.EmailField()


class WithdrawProfit(models.Model):
    user= models.ForeignKey(User, on_delete= models.CASCADE)
    amount= models.IntegerField()
    recipient= models.CharField(max_length=50)
    transfer_code= models.CharField(max_length=7)
    bank_name= models.CharField(max_length=25)
    account_number= models.IntegerField()
    recipient_name= models.CharField(max_length=200)
    status= models.CharField(max_length=25, blank=True, null= True, default= "unconfirmed")
    date= models.DateTimeField(auto_now_add= True)

    def get_absolute_url(self):
        return reverse('home')

class PaystackKeys(models.Model):
    public_key = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=100)

    # Singleton pattern to ensure only one entry
    def save(self, *args, **kwargs):
        if not self.pk and PaystackKeys.objects.exists():
            # Only allow one entry
            raise ValidationError('Only one PaystackKeys entry allowed')
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Paystack Keys'
    
    def get_absolute_url(self):
        return reverse('paystack-keys')

class ProductCart(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    product= models.CharField(max_length=150)
    price= models.IntegerField()
    quantity= models.IntegerField()
    commission= models.IntegerField()

class Cart2(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    name= models.CharField(max_length=25)
    product= models.ManyToManyField(ProductCart, blank= True)

class PayCart(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    cart= models.CharField(max_length=25)
    amount= models.IntegerField()
    email= models.EmailField(default='none@gmail.com')
    commission= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ref= models.CharField(max_length=7)
    transaction= models.CharField(max_length=25, default= "unconfirmed")
    date= models.DateField(auto_now_add= True)

class Location(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    location= models.TextField()

class EmailSet(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    email_address= models.EmailField()
    email_password= models.TextField()

    def get_absolute_url(self):
        return reverse('profile')

class Alertmail(models.Model):
    user= models.ForeignKey(User, on_delete= models.CASCADE)
    email_address= models.EmailField()

    def get_absolute_url(self):
        return reverse('profile')

class CallMeBot(models.Model):
    user= models.ForeignKey(User, on_delete= models.CASCADE)
    phone_number= models.IntegerField()
    api_key= models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse('profile')

class About(models.Model):
    image= models.ImageField(upload_to= "media")
    video= models.FileField(upload_to= "media", blank=True, null=True, default=None)
    title= models.CharField(max_length=100)
    description= models.TextField()

    def get_absolute_url(self):
        return reverse('about-us')

class Socials(models.Model):
    whatsapp= models.CharField(max_length=25)
    facebook= models.URLField(blank=True, null=True)
    twitter= models.URLField(blank=True, null=True)
    instagram= models.URLField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('about-us')

class ContactInfo(models.Model):
    telephone= models.CharField(max_length=500)
    address= models.TextField()
    email= models.EmailField()

    def get_absolute_url(self):
        return reverse('about-us')

class Staff(models.Model):
    image= models.ImageField(default=None)
    name= models.CharField(max_length=250)
    position= models.TextField()
    email= models.EmailField(blank= True, null= True)

    def get_absolute_url(self):
        return reverse('about-us')

class Reset(models.Model):
    link= models.URLField()

    def get_absolute_url(self):
        return reverse('profile')

class WhatsappReset(models.Model):
    phone_number= models.IntegerField()
    api_key= models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse('profile')

class InstructionBot(models.Model):
    image= models.ImageField()
    instruct= models.TextField()

    def get_absolute_url(self):
        return reverse('profile')
    
class Permissions(models.Model):
    status= models.CharField(max_length=25)

class Permission(models.Model):
    permissions= models.CharField(max_length=25)

class Testimony(models.Model):
    user=  models.ForeignKey(User, on_delete= models.CASCADE)
    text= models.TextField()

