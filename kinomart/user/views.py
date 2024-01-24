from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress
from django.contrib import messages
from django.db.models import Q


# Create your views here.


def index(request):
    return render(request,'index.html')

def signup(request):
    if request.method=='POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        phone=request.POST['mobile']
        password=request.POST['password1']
        pin=request.POST['pin']




    
    # checking email taken
        if User.objects.filter(email__iexact=email).exists():
            messages.info(request,'Already registerd with this email')
            return redirect('signup')
        

    # checking for mobile number taken
        if User.objects.filter(phone__iexact=phone).exists():
            messages.info(request,'Already registered with this phone number')
            return redirect('signup')
        
        if password != request.POST['password2']:
            messages.info(request,'Password not matching!')
            return redirect('signup')
        address_line='Kottarappattu'

        us=User(first_name=first_name,email=email,phone=phone,password=password)
        us.save()
        ad=UserAddress(pin=pin,address_line=address_line,user_id=us)
        ad.save()

        # creating session when user registered succussfully
        
        request.session['user_email']=us.email

        return redirect('home')
    
    else:
        return render(request,'signup.html')


def login(request):
    if request.method=='POST':

        input=request.POST['mob_email']
        # validating the email or phone exising
        if User.objects.filter(Q(email__iexact=input) | Q(phone__iexact=input)).exists():

            us=User.objects.get(Q(email__iexact=input) | Q(phone__iexact=input))
            if us.password!=request.POST['password']:
                messages.info(request,'Incorrect Password!')
                return redirect('login_user')
            print('login success')
            request.session['user_email']=us.email
            return redirect('home')

        else:
            messages.info(request,'Invalid Email/Password')
            return redirect('login_user')

    else:
        return render(request,'login.html')
    


def logout(request):
    request.session.clear()
    return redirect('home')

def user_page(request):


    if 'user_email' in request.session:
        return render(request,'user_profile.html')
    
    else:
        return redirect('login_user')