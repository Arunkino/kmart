from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress

# Create your views here.


def index(request):
    return render(request,'index.html')

def signup(request):
    if request.method=='POST':
        first_name=request.POST['first_name']
        email=request.POST['email']
        phone=request.POST['mobile']
        password=request.POST['password1']
        pin=680519
        address_line='Kottarappattu'

        us=User(first_name=first_name,email=email,phone=phone,password=password)
        us.save()
        ad=UserAddress(pin=pin,address_line=address_line,user_id=us)
        ad.save()
        

        return redirect('home')
    
    else:
        return render(request,'signup.html')
