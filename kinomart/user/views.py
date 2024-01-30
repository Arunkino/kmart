from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model,authenticate,login,logout
from django.contrib.auth.hashers import make_password

# Create your views here.


def index(request):
    return render(request,'index.html')

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
        if User.objects.filter(email__iexact=email).exists():
            messages.info(request,'Already registerd with this email')
            return redirect('signup')
        

    # checking for mobile number taken
        if User.objects.filter(phone__iexact=phone).exists():
            messages.info(request,'Already registered with this phone number')
            return redirect('signup')
        
        
        

        us=User(first_name=first_name,last_name=last_name,email=email,phone=phone,username=email)
        us.password=make_password(password)
        
        us.save()

        ad=UserAddress(pin=pin,address_line=address_line,city=city,landmark=landmark,user_id=us)
        ad.save()

        # creating session when user registered succussfully with auto login
        
        request.session['user_email']=us.email

        return redirect('home')
    
    else:
        return render(request,'signup.html')


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