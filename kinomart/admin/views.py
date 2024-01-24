from django.shortcuts import render,redirect
from django.contrib import messages
from user.models import User,UserAddress

# Create your views here.
def index(request):
    return render(request,'index_admin.html')

def login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        if email!='admin@kino.com':
            messages.info(request,'Invalid Email Address!')
            return redirect('admin_login')
        elif password!='1234':
            messages.info(request,'Incorrct Password')
            return redirect('admin_login')
        else:
            return redirect('index')

    else:
        return render(request,'admin_login.html')
    

def user_list(request):
    users=User.objects.all()
    
    return render(request,'userlist.html',{'users':users})

def block_user(request,id):
    us=User.objects.get(id=id)
    us.is_active=False
    us.save()
    return redirect('admin_userlist')

def unblock_user(request,id):
    us=User.objects.get(id=id)
    us.is_active=True
    us.save()
    return redirect('admin_userlist')