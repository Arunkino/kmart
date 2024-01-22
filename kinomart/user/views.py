from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress
from django.contrib import messages


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
        if User.objects.exists(email=email):
            messages.info(request,'Already registerd with this email')
            return redirect('signup')
        

    # checking for mobile number taken
        if User.objects.exists(phone=phone):
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
        

        return redirect('home')
    
    else:
        return render(request,'signup.html')


def login(request):
    if request.method=='POST':
        pass

    else:
        return render(request,'login.html')