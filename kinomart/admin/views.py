from django.shortcuts import render,redirect
from django.contrib import messages
from user.models import User,UserAddress,Order,OrderItem
from products.models import Category,SubCategory,ProductImages,Products,ProductVarient,Unit,Brand
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from admin.models import Coupon
from offer.models import Offer
from decimal import Decimal

# Create your views here.
def index(request):
    if 'admin_email' in request.session:
        return render(request,'admin/index_admin.html')
    return redirect('admin_login')

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
            request.session['admin_email']=email
            return redirect('index')

    else:
        if 'admin_email' in request.session:
            return redirect('index')

        return render(request,'admin/admin_login.html')
    
def logout(request):
    request.session.clear()
    return redirect('admin_login')
    

def user_list(request):
    if 'admin_email' in request.session:

        users=User.objects.all().order_by('id')
        
        return render(request,'admin/userlist.html',{'users':users})
    return redirect('admin_login')
def list_product(request):
    if 'admin_email' in request.session:
        categories=Category.objects.prefetch_related('subcategories').all()
        variants = ProductVarient.objects.select_related('product_id', 'product_id__sub_category','product_id__brand', 'product_id__sub_category__category').all()
        variant_data = []
        for variant in variants:
            product = variant.product_id
            sub_category = product.sub_category
            brand=product.brand
            if sub_category is not None:
                category = sub_category.category
            images = ProductImages.objects.filter(product_id=product).first()
            image = images.image.url if images else None
            variant_data.append({
                'id': variant.id,
                'name': product.product_name,
                'product_id':product.id,
                'description': product.description,
                'category': category.category,
                'price': variant.price,
                'stock' : variant.stock,
                'brand' : brand.brand_name,
                'image': image,
            })
        return render(request, 'admin/list_product.html', {'variants': variant_data,'categories':categories})
    return redirect('admin_login')

def edit_product(request,id):

    varient = ProductVarient.objects.select_related('product_id', 'product_id__sub_category','product_id__brand', 'product_id__sub_category__category').get(id=id)
    categories=Category.objects.all()
    sub_categories=SubCategory.objects.all()
    brands=Brand.objects.all().order_by('id')
    images=ProductImages.objects.filter(product_id=varient.product_id)


    return render(request,'admin/edit_product.html',{'varient':varient,'categories':categories,'sub_categories':sub_categories,'brands':brands,'images':images})

def hold_product(request,id):
    pass


def admin_orders(request):

    orders=Order.objects.all().order_by('-id')
    return render(request, 'admin/orders.html',{'orders':orders})
def block_user(request,id):
    if 'admin_email' in request.session:

        us=User.objects.get(id=id)
        us.is_active=False
        us.save()
        return redirect('admin_userlist')
    return redirect('admin_login')
    

def unblock_user(request,id):
    if 'admin_email' in request.session:

        us=User.objects.get(id=id)
        us.is_active=True
        us.save()
        return redirect('admin_userlist')
    return redirect('admin_login')
    

def add_product(request):
    if 'admin_email' in request.session:

        if request.method=='POST':

            image1 = request.FILES.get('image1')

            
            
                
            name=request.POST['product_name']
            desc=request.POST['description']
            brand=request.POST['brand']
            cat=Category.objects.get(id=request.POST['category'])
            sub=SubCategory.objects.get(id=request.POST['sub_category'])

            pr=Products(product_name=name,description=desc,sub_category=sub,brand_id=brand)
            if request.POST['is_offer']=='True':
                pr.is_offer=True
                off=int((request.POST['offer_select']))
                print("offerrr idd",off)
                offer=Offer.objects.get(id=off)
                pr.offer=offer

            pr.save()
            ProductImages.objects.create(product_id=pr,image=image1)
            if 'image2' in request.FILES:
                image2 = request.FILES['image2']
                ProductImages.objects.create(product_id=pr,image=image2)

            if 'image3' in request.FILES:
                image3 = request.FILES['image3']
                ProductImages.objects.create(product_id=pr,image=image3)

    # for getting the number of varients
            variant_count = int(request.POST.get('variantCount'))
            varients=[]
            for i in range(1,variant_count+1):
                quantity=request.POST['quantity'+str(i)]
                unit=Unit.objects.get(id=request.POST['unit'+str(i)])
                stock=request.POST['stock'+str(i)]
                price=Decimal(request.POST['price'+str(i)])
                
                if request.POST['is_offer']=='True':
                    print(request.POST['offer_select'])
                    off=int((request.POST['offer_select']))
                    print("offerrr idd",off)
                    offer=Offer.objects.get(id=off)
                    print("offer object",offer)
                    offer_price=price-((price*Decimal(offer.discount))/100)
                    print(offer_price)
                    ProductVarient.objects.create(quantity=quantity,unit=unit,stock=stock,price=price,product_id=pr,offer_price=offer_price)
            
                else:
                    ProductVarient.objects.create(quantity=quantity,unit=unit,stock=stock,price=price,product_id=pr)

            return redirect('list_product')





        else:
            categories=Category.objects.all()
            sub_categories=SubCategory.objects.all()
            units=Unit.objects.all()
            brands=Brand.objects.all().order_by('id')
            offers=Offer.objects.all()

            return render(request,'admin/add_product.html',{'categories':categories,'sub_categories':sub_categories,'units':units,'brands':brands,'offers':offers})
    return redirect('admin_login')
    

def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = SubCategory.objects.filter(category_id=category_id).order_by('sub_category')

    return render(request, 'admin/subcategory_dropdown_list_options.html', {'subcategories': subcategories})

        
def edit_categories(request):
    if 'admin_email' in request.session:
        
        categories = Category.objects.prefetch_related('subcategories').all().order_by('category')
        category_data = []

        for category in categories:
            subcategories = category.subcategories.all().order_by('sub_category')
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
                'category_offer': category.offer,
                'subcategories': subcategory_data,
            })
            
        offers=Offer.objects.all()
        return render(request, 'admin/edit_categories.html', {'categories': category_data,'offers':offers})
    return redirect('admin_login')
    


def add_category(request):
    if 'admin_email' in request.session:

        if request.method == 'POST':
            category_name = request.POST.get('category_name')
            category=Category(category=category_name)
            
            
            
            # checking for offer
            if request.POST['is_offer']=='True':
                offer_id=int((request.POST['offer_select']))
                offer=Offer.objects.get(id=offer_id)
                category.offer=offer

            category.save()
                


                
                
        return redirect('edit_categories')
    return redirect('admin_login')


def update_category(request):
    if 'admin_email' in request.session:

        if request.method == 'POST':
            category_name = request.POST.get('category_name')
            category_id = request.POST.get('category_id')
            cat=Category.objects.get(id=category_id)
            cat.category=category_name


            if request.POST['is_offer']=='True':
                offer_id=int(request.POST['offer_select'])
                offer=Offer.objects.get(id=offer_id)
                discount=offer.discount
                cat.offer=offer

        # updating products offer
                products = Products.objects.filter(sub_category__category=cat)
                for product in products:
                    product.offer=offer
                    product.is_offer=True
                    product.save()

                    for variant in product.varients.all():

                        price=variant.price
                        variant.offer_price=price-((price*Decimal(discount))/100)
                        variant.save()







            cat.save()
        return redirect('edit_categories')
    return redirect('admin_login')

def update_subcategory(request):
    if 'admin_email' in request.session:

        if request.method == 'POST':
            subcategory_name = request.POST.get('subcategory_name')
            subcategory_id = request.POST.get('subcategory_id')
            cat=SubCategory.objects.get(id=subcategory_id)
            cat.sub_category=subcategory_name
            cat.save()
        return redirect('edit_categories')
    return redirect('admin_login')
    

def add_subcategory(request):
    if 'admin_email' in request.session:

        if request.method=='POST':
            sub_category=request.POST['subcategory_name']
            category_id=request.POST['category_id']
            category=Category.objects.get(id=category_id)
            SubCategory.objects.create(sub_category=sub_category,category=category)

            return redirect('edit_categories')
    return redirect('admin_login')
    

def delete_subcategory(request,id):
    if 'admin_email' in request.session:

        sub_category=SubCategory.objects.get(id=id)
        products=sub_category.products.all()

        product_variants = [product.varients.all() for product in products]
        for product_variant in product_variants:
            for variant in product_variant:
                variant.is_holded=True
                variant.save()
        sub_category.delete()
        return redirect('edit_categories')
    return redirect('admin_login')
    

def delete_category(request, id):
    if 'admin_email' in request.session:

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
        return redirect('edit_categories')
    return redirect('admin_login')
    
@csrf_exempt
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

        # update the order status
        Order.objects.filter(id=order_id).update(status=status)

        return JsonResponse({'status': 'success'})
    


# all about coupons starts here

def coupon_management(request):
    coupons=Coupon.objects.all().order_by('-id')


    return render(request,'admin/coupon.html',{'coupons':coupons})

def add_coupon(request):
    if request.method=='POST':
        coupon_code=request.POST['coupon_code']
        count=request.POST['count']
        expiry_date=request.POST['expiry_date']
        min_order=request.POST['min_order']
        discount_percentage=request.POST['discount_percentage']

        Coupon.objects.create(coupon_code=coupon_code,count=count,expiry_date=expiry_date,min_order=min_order,discount_percentage=discount_percentage)

        return redirect('coupon_management')
    

def edit_coupon(request):
    if request.method=='POST':
        id=request.POST['coupon-id']

        coupon=Coupon.objects.get(id=id)


        coupon.coupon_code=request.POST['coupon_code']
        coupon.count=request.POST['count']
        coupon.expiry_date=request.POST['expiry_date']
        coupon.min_order=request.POST['min_order']
        coupon.discount_percentage=request.POST['discount_percentage']

        coupon.save()

        return redirect('coupon_management')