from django.shortcuts import render,redirect
from django.contrib import messages
from user.models import User,UserAddress
from products.models import Category,SubCategory,ProductImages,Products,ProductVarient,Unit

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
def list_product(request):
    variants = ProductVarient.objects.select_related('product_id', 'product_id__sub_category', 'product_id__sub_category__category').all()
    variant_data = []
    for variant in variants:
        product = variant.product_id
        sub_category = product.sub_category
        category = sub_category.category
        images = ProductImages.objects.filter(product_id=product).first()
        image = images.image.url if images else None
        variant_data.append({
            'id': product.id,
            'name': product.product_name,
            'description': product.description,
            'category': category.category,
            'price': variant.price,
            'image': image,
        })
    return render(request, 'list_product.html', {'variants': variant_data})

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
            quantity=request.POST['quantity'+str(i)]
            unit=Unit.objects.get(id=request.POST['unit'+str(i)])
            stock=request.POST['stock'+str(i)]
            price=request.POST['price'+str(i)]
            ProductVarient.objects.create(quantity=quantity,unit=unit,stock=stock,price=price,product_id=pr)
            print("variant",i,"created")

                    
        print('product object created with image....')
        return redirect('index')



    else:
        categories=Category.objects.all()
        sub_categories=SubCategory.objects.all()
        units=Unit.objects.all()

        return render(request,'add_product.html',{'categories':categories,'sub_categories':sub_categories,'units':units})