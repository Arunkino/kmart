from django.shortcuts import render,redirect
from django.contrib import messages
from user.models import User,UserAddress
from products.models import Category,SubCategory,ProductImages,Products,ProductVarient

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

def add_product(request):
    if request.method=='POST':
        image = request.FILES['image1']
        name=request.POST['product_name']
        desc=request.POST['description']
        cat=Category.objects.get(id=request.POST['category'])
        sub=SubCategory.objects.get(id=request.POST['sub_category'])

        pr=Products(product_name=name,description=desc,sub_category=sub)
        pr.save()
        ProductImages.objects.create(product_id=pr,image=image)

# for getting the number of varients
        variant_count = int(request.POST.get('variantCount'))
        varients=[]
        for i in range(1,variant_count+1):
            print(request.POST['quantity'+str(i)])        
        print('product object created with image....')
        return redirect('index')



    else:
        categories=Category.objects.all()
        sub_categories=SubCategory.objects.all()

        return render(request,'add_product.html',{'categories':categories,'sub_categories':sub_categories})