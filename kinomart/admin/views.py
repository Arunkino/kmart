from django.shortcuts import render,redirect
from django.contrib import messages
from user.models import User,UserAddress
from products.models import Category,SubCategory,ProductImages,Products,ProductVarient,Unit,Brand

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
    categories=Category.objects.prefetch_related('subcategories').all()
    variants = ProductVarient.objects.select_related('product_id', 'product_id__sub_category','product_id__brand', 'product_id__sub_category__category').all()
    variant_data = []
    for variant in variants:
        product = variant.product_id
        sub_category = product.sub_category
        brand=product.brand
        category = sub_category.category
        images = ProductImages.objects.filter(product_id=product).first()
        image = images.image.url if images else None
        variant_data.append({
            'id': product.id,
            'name': product.product_name,
            'description': product.description,
            'category': category.category,
            'price': variant.price,
            'stock' : variant.stock,
            'brand' : brand.brand_name,
            'image': image,
        })
    return render(request, 'list_product.html', {'variants': variant_data,'categories':categories})

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
        image1 = request.FILES['image1']
        image2 = request.FILES['image2']
        image3 = request.FILES['image3']
        name=request.POST['product_name']
        desc=request.POST['description']
        brand=request.POST['brand']
        cat=Category.objects.get(id=request.POST['category'])
        sub=SubCategory.objects.get(id=request.POST['sub_category'])

        pr=Products(product_name=name,description=desc,sub_category=sub,brand_id=brand)
        pr.save()
        ProductImages.objects.create(product_id=pr,image=image1)
        ProductImages.objects.create(product_id=pr,image=image2)
        ProductImages.objects.create(product_id=pr,image=image3)

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
        brands=Brand.objects.all().order_by('id')

        return render(request,'add_product.html',{'categories':categories,'sub_categories':sub_categories,'units':units,'brands':brands})
    
def edit_catagories(request):
        
    categories = Category.objects.prefetch_related('subcategories').all()
    category_data = []

    for category in categories:
        subcategories = category.subcategories.all()
        subcategory_data = []
        
        for subcategory in subcategories:
            products = subcategory.products.all()
            product_data = []
            
            for product in products:
                variants = product.varients.all()
                variant_data = []
                
                for variant in variants:
                    images = ProductImages.objects.filter(product_id=product).first()
                    image = images.image.url if images else None
                    variant_data.append({
                        'id': variant.id,
                        
                        'description': product.description,
                        'price': variant.price,
                        'stock': variant.stock,
                        'brand': product.brand.brand_name,
                        'image': image,
                    })
                    
                product_data.append({
                    'product_id': product.id,
                    'product_name': product.product_name,
                    'variants': variant_data,
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
        

    return render(request, 'edit_categories.html', {'categories': category_data})


def add_category(request):
    pass

def delete_subcategory(request,id):
    sub_category=SubCategory.objects.get(id=id)
    products=sub_category.products.all()

    product_variants = [product.varients.all() for product in products]
    for product_variant in product_variants:
        for variant in product_variant:
            variant.is_holded=True
            variant.save()
    sub_category.delete()
    return redirect('edit_catagories')

def delete_category(request, id):
    category = Category.objects.get(id=id)
    subcategories = category.subcategories.all()

    for subcategory in subcategories:
        products = subcategory.products.all()

        for product in products:
            product_variants = product.varients.all()

            for variant in product_variants:
                variant.is_holded = True
                variant.save()

    category.delete()
    return redirect('edit_catagories')
