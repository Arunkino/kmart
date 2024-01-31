from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress
from products.models import Category,ProductImages,Products
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model,authenticate,login,logout
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.


def index(request):

    categories = Category.objects.prefetch_related('subcategories').all()
    category_data = []

    for category in categories:
        subcategories = category.subcategories.all()
        subcategory_data = []
        
        for subcategory in subcategories:
            products = subcategory.products.all()
            product_data = []
            
            for product in products:
                images = ProductImages.objects.filter(product_id=product).first()
                image = images.image.url if images else None
                variant = product.varients.first()
                
                
                
                        
                    
                    
                product_data.append({
                    'product_id': product.id,
                    'product_name': product.product_name,
                    'description': product.description,
                    'price': variant.price,
                    'quantity':variant.quantity,
                    'unit':variant.unit, 
                    'brand': product.brand.brand_name,

                    'image': image,
                    
                })
                
            subcategory_data.append({
                'subcategory_id': subcategory.id,
                'subcategory_name': subcategory.sub_category,
                'products': product_data,
            })
            
        category_data.append({
            'category_id' : category.id,
            'category_name': category.category,
            'subcategories': subcategory_data,
        })


    return render(request,'index.html',{'categories': category_data,})

def signup(request):
    if request.method=='POST':

        User=get_user_model()


        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        phone=request.POST['mobile']
        password=request.POST['password1']
        address_line=request.POST['address']
        city=request.POST['city']
        landmark=request.POST['landmark']
        pin=request.POST['pin']
        
        if password != request.POST['password2']:
            messages.info(request,'Password not matching!')
            return redirect('signup')


    
    # checking email taken
        if User.objects.filter(Q(email__iexact=email)|Q(phone__iexact=phone)).exists():
            user= User.objects.filter(Q(email__iexact=email)|Q(phone__iexact=phone)).first()
            if user.is_active:
                messages.info(request,'Already registerd with this email/phone ')
                return redirect('login')
            else:
                messages.info(request,'Already registerd with this email. Please verify your email with otp to compleate the registration')
                otp=random.randint(10000,99999)
                request.session['otp']=otp


                subject = 'Thank you for registering on Kino Mart'
                message = f' Your otp for registration is {otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email,]   
                send_mail( subject, message, email_from, recipient_list )
                print("email send success")
                request.session['user_id']=user.id
                return render(request,'otp.html',{'email':email})



        

   
        
        
# we need to send email for otp verification
        
        otp=random.randint(10000,99999)
        request.session['otp']=otp


        subject = 'Thank you for registering on Kino Mart'
        message = f' Your otp for registration is {otp}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email,]   
        send_mail( subject, message, email_from, recipient_list )
        print("email send success")


        User=get_user_model()
        us=User(first_name=first_name,last_name=last_name,email=email,phone=phone,username=email,is_active=False)
        us.password=make_password(password)
        us.save()
        ad=UserAddress(pin=pin,address_line=address_line,city=city,landmark=landmark,user_id=us)
        ad.save()
        request.session['user_id']=us.id
        request.session['user_address']=ad.id


        

        return render(request,'otp.html',{'email':email})
    
    else:
        return render(request,'signup.html')
    

def otp_user(request):
    if request.method=='POST':
        print(request.POST['otp'])
        print("Generated OTP:",request.session['otp'])
        if request.POST['otp']==str(request.session['otp']):
            print("OTP VALIDATED SUCCESSFULLY")



# When otp validation is successfull, create user instance. 
            user=User.objects.get(id=request.session['user_id'])
            user.is_active=True
            user.save()

            
            # creating session when user registered succussfully with auto login
            
            request.session['user_email']=user.email
            return redirect('home')
        else:
            messages.info(request,'Incorrect OTP entered!!')
            return redirect('otp_user')



    return render(request,'otp.html')


def login_user(request):
    if request.method=='POST':

        input=request.POST['mob_email']
        password=request.POST['password']
        # validating the email or phone exising

        user=authenticate(request,username=input,password=password)

        if user is not None:
            if user.is_active:
                login(request,user)
                print("login success")
                request.session['user_email']=user.email

                return redirect('home')
            
            else:
                messages.info(request,'Your account is blocked by the admin!!!\n please contact customercare.')
                return redirect('login_user')
            
        else:
            messages.info(request,'Invalid Email/Password')
            return redirect('login_user')
        
# for get method
    return render(request,'login.html')
    


def logout_user(request):
    request.session.clear()
    logout(request)
    return redirect('home')

def user_page(request):


    if 'user_email' in request.session:
        return render(request,'user_profile.html')
    
    else:
        return redirect('login_user')
    


def view_product(request,id):
    product=Products.objects.prefetch_related('varients','images').get(id=id)

    


    return render(request,'view_product.html',{'product':product})