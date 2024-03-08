from django.shortcuts import render,redirect
from django.contrib import messages
from user.models import User,UserAddress,Order,OrderItem
from wallet.models import Wallet,WalletTransactions
from products.models import Category,SubCategory,ProductImages,Products,ProductVarient,Unit,Brand
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from admin.models import Coupon
from offer.models import Offer
from decimal import Decimal
from django.http import HttpResponse
import csv
from django.db.models import F,Sum
from django.utils import timezone
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table,TableStyle
from reportlab.lib import colors
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def top_selling(request):
    top_selling_range=request.GET.get('data')
    print(top_selling_range)
    result=[]

    if top_selling_range =='product':
        header="Top Selling Products"   
        product_sales = OrderItem.objects.values('product').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        for i in range (9):
            product =ProductVarient.objects.get(id=product_sales[i]['product'])
            result.append(product.product_id.product_name)
    
    elif top_selling_range == 'category':
        header = "Top Selling Categories"
        
        # Aggregate the total quantity of each category sold
        category_sales = OrderItem.objects.values('product__product_id__sub_category__category__category').annotate(Total_quantity=Sum('quantity')).order_by('-Total_quantity')

        for i in range(min(9, len(category_sales))):
            category = Category.objects.get(category=category_sales[i]['product__product_id__sub_category__category__category'])
            result.append(category.category)
    elif top_selling_range == 'brand':
        header = "Top Selling Brand"

        brand_sales = OrderItem.objects.values('product__product_id__brand__brand_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')

        for i in range (min(9, len(brand_sales))):

            brand = Brand.objects.get(brand_name=brand_sales[i]['product__product_id__brand__brand_name'])
            result.append(brand.brand_name)
    

    print(result)
    return JsonResponse({'result':result,'header':header})
def chart_date_index(request):
    date_range = request.GET.get('date_range')
    print(date_range)

    label=[]
    data=[]
    data_revenue=[]


    end_date = datetime.now().date()
    if date_range == 'week':
        start_date = end_date - timedelta(days=7)
        delta = end_date - start_date

    elif date_range == 'month':
        start_date = end_date - timedelta(days=30)
        delta = end_date - start_date

    elif date_range == 'year':
        end_month = datetime.now()
        start_month = end_month - relativedelta(months=12)

        

        for i in range(13):  # 12 months + current month
            current_month = start_month + relativedelta(months=i)
            label.append(current_month.strftime('%b'))

            order_count = Order.objects.filter(order_date__year=current_month.year, order_date__month=current_month.month).count()
            revenue = Order.objects.filter(order_date__year=current_month.year, order_date__month=current_month.month, payment_status=True).aggregate(Sum('total_price'))['total_price__sum']
            data.append(order_count)

            if revenue:
                data_revenue.append(float(revenue))
            else:
                data_revenue.append(0)

        print(label)
        print(data)
        print(data_revenue)

        return JsonResponse({'label': label, 'data': data, 'data_revenue': data_revenue})
    else:
        start_date = end_date-timedelta(days=10)
        delta = end_date - start_date

        
    for i in range(delta.days+1):
        current_date = start_date + timedelta(days=i)
        label.append(current_date.strftime('%b %d'))

        order_count=Order.objects.filter(order_date__date=current_date).count()
        revenue=Order.objects.filter(order_date__date=current_date,payment_status=True).aggregate(Sum('total_price'))['total_price__sum']
        data.append(order_count)
        if revenue:
            data_revenue.append(float(revenue))
        else:
            data_revenue.append(0)

    return JsonResponse({'label':label,'data':data,'data_revenue':data_revenue})

@login_required
def index(request):
    if request.user.is_authenticated and request.user.is_superuser:
        end_date=timezone.now().date()
        start_date=end_date-timezone.timedelta(days=10)

        delta=end_date-start_date
        label=[]
        data=[]
        data_revenue=[]

        for i in range(delta.days+1):
            current_date = start_date + timedelta(days=i)
            label.append(current_date.strftime('%b %d'))

            order_count=Order.objects.filter(order_date__date=current_date).count()
            revenue=Order.objects.filter(order_date__date=current_date,payment_status=True).aggregate(Sum('total_price'))['total_price__sum']
            data.append(order_count)
            if revenue:
                data_revenue.append(float(revenue))
            else:
                data_revenue.append(0)
        return render(request,'admin/index_admin.html',{'label':label,'data':data,'data_revenue':data_revenue})
    return redirect('admin_login')

def login_admin(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(request,username=email,password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.info(request,'Invalid Email or Password!')
            return redirect('admin_login')
        

        

    else:
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect('index')

        return render(request,'admin/admin_login.html')
    
def logout_admin(request):
    request.session.clear()
    logout(request)
    return redirect('admin_login')
    
@login_required
def user_list(request):
    if request.user.is_authenticated and request.user.is_superuser:

        users=User.objects.all().order_by('id')
        
        return render(request,'admin/userlist.html',{'users':users})
    return redirect('admin_login')
@login_required
def list_product(request):
    if request.user.is_authenticated and request.user.is_superuser:
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
                'is_holded':variant.is_holded,
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
    varient=ProductVarient.objects.get(id=id)
    varient.is_holded=True
    varient.save()

    return redirect ('list_product')

@login_required
def admin_orders(request):
    if request.user.is_authenticated and request.user.is_superuser:

        orders=Order.objects.all().order_by('-id')
        return render(request, 'admin/orders.html',{'orders':orders})
    

@login_required
def block_user(request,id):
    if request.user.is_authenticated and request.user.is_superuser:

        us=User.objects.get(id=id)
        us.is_active=False
        us.save()
        return redirect('admin_userlist')
    return redirect('admin_login')
    

@login_required
def unblock_user(request,id):
    if request.user.is_authenticated and request.user.is_superuser:

        us=User.objects.get(id=id)
        us.is_active=True
        us.save()
        return redirect('admin_userlist')
    return redirect('admin_login')
    

@login_required
def add_product(request):
    if request.user.is_authenticated and request.user.is_superuser:

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

 
@login_required       
def edit_categories(request):
    if request.user.is_authenticated and request.user.is_superuser:
        
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
    


@login_required
def add_category(request):
    if request.user.is_authenticated and request.user.is_superuser:

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


@login_required
def update_category(request):
    if request.user.is_authenticated and request.user.is_superuser:

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


            else:
                cat.offer=None

        # updating products offer to None
                products = Products.objects.filter(sub_category__category=cat)
                for product in products:
                    product.offer=None
                    product.is_offer=False
                    product.save()

                    for variant in product.varients.all():

                        variant.offer_price=None
                        variant.save()







            cat.save()
        return redirect('edit_categories')
    return redirect('admin_login')

@login_required
def update_subcategory(request):
    if request.user.is_authenticated and request.user.is_superuser:

        if request.method == 'POST':
            subcategory_name = request.POST.get('subcategory_name')
            subcategory_id = request.POST.get('subcategory_id')
            cat=SubCategory.objects.get(id=subcategory_id)
            cat.sub_category=subcategory_name
            cat.save()
        return redirect('edit_categories')
    return redirect('admin_login')
    

@login_required
def add_subcategory(request):
    if request.user.is_authenticated and request.user.is_superuser:

        if request.method=='POST':
            sub_category=request.POST['subcategory_name']
            category_id=request.POST['category_id']
            category=Category.objects.get(id=category_id)
            SubCategory.objects.create(sub_category=sub_category,category=category)

            return redirect('edit_categories')
    return redirect('admin_login')
    

@login_required
def delete_subcategory(request,id):
    if request.user.is_authenticated and request.user.is_superuser:

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
    

@login_required
def delete_category(request, id):
    if request.user.is_authenticated and request.user.is_superuser:

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
        
        order=Order.objects.get(id=order_id)
        order.status=status
        order.save()
        print(status)
        print(order.payment_status)
        if status == 'Cancel' and order.payment_status:
            print("cancelling paid order")
            user=order.user
            amount=order.total_price
            wallet=Wallet.objects.get(user=user)
            wallet.balance+=amount
            wallet.last_transaction=f'+{amount}'
            wallet.save()

            WalletTransactions.objects.create(wallet=wallet,transaction_amount=amount,discription=f'Refund of cancelled order {order.id}')

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
    

# views for sales report
@login_required
def sales_report(request):
    if request.user.is_authenticated and request.user.is_superuser:


        orders=Order.objects.filter(payment_status=True).annotate(
        discount=F('actual_price') - F('total_price'))
        total_discount=orders.aggregate(Sum('discount'))['discount__sum']
        total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

        return render(request,'admin/sales_report_page.html',{'orders':orders,'total_discount':total_discount,'total_order_amount':total_order_amount})


#to get all orders in CSV
def sales_report_all(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'


    orders=Order.objects.filter(payment_status=True).annotate(
    discount=F('actual_price') - F('total_price'))

    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

    writer = csv.writer(response)
    writer.writerow(['OVERALL SALES REPORT'])
    writer.writerow([''])
    writer.writerow(['sales count',f'{orders.count()}'])
    writer.writerow(['Order Amount',f'{total_order_amount}'])
    writer.writerow(['Total Discount',f'{total_discount}'])
    writer.writerow([''])

    writer.writerow(['Id','order_date', 'User', 'Total','Discount','Paid','Payment Method'])

    
    

    for order in orders:
        id=order.id
        order_date=order.order_date.date()
        user=order.user
        total=order.actual_price
        discount=order.discount
        paid=order.total_price
        method=order.payment_method
        writer.writerow([id,order_date,user,total,discount,paid,method])

    return response

def sales_report_range(request,range):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    if range=='day':
        to_date=timezone.now().date()
        from_date=to_date-timezone.timedelta(days=1)

    elif range =='week':
        to_date=timezone.now().date()
        from_date=to_date-timezone.timedelta(days=7)

    elif range == 'month':
        to_date=timezone.now().date()
        from_date=to_date-timezone.timedelta(days=30)

    


    orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
    discount=F('actual_price') - F('total_price'))
    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

    writer = csv.writer(response)
    writer.writerow([f'Last {range} sales report'])
    writer.writerow([''])
    writer.writerow(['sales count',f'{orders.count()}'])
    writer.writerow(['Order Amount',f'{total_order_amount}'])
    writer.writerow(['Total Discount',f'{total_discount}'])
    writer.writerow([''])

    writer.writerow(['Id','order_date', 'User', 'Total','Discount','Paid','Payment Method'])

    
    

    for order in orders:
        id=order.id
        order_date=order.order_date.date()
        user=order.user
        total=order.actual_price
        discount=order.discount
        paid=order.total_price
        method=order.payment_method
        writer.writerow([id,order_date,user,total,discount,paid,method])

    return response


def sales_report_customrange(request,from_date,to_date):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    


    orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
    discount=F('actual_price') - F('total_price'))
    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

    writer = csv.writer(response)
    writer.writerow([f'Sales report from {from_date} to {to_date}'])

    writer.writerow([''])
    writer.writerow(['sales count',f'{orders.count()}'])
    writer.writerow(['Order Amount',f'{total_order_amount}'])
    writer.writerow(['Total Discount',f'{total_discount}'])
    writer.writerow([''])

    writer.writerow(['Id','order_date', 'User', 'Total','Discount','Paid','Payment Method'])

    
    

    for order in orders:
        id=order.id
        order_date=order.order_date.date()
        user=order.user
        total=order.actual_price
        discount=order.discount
        paid=order.total_price
        method=order.payment_method
        writer.writerow([id,order_date,user,total,discount,paid,method])

    return response



def sales_report_day(request):

    to_date=timezone.now().date()
    from_date=to_date-timezone.timedelta(days=1)
    orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
    discount=F('actual_price') - F('total_price'))

    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

    

    return render(request,'admin/sales_report.html',{'orders':orders,'total_discount':total_discount,'total_order_amount':total_order_amount,'from_date':from_date,'to_date':to_date,'range':'day'})

def sales_report_week(request):

    to_date=timezone.now().date()
    from_date=to_date-timezone.timedelta(days=7)
    orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
    discount=F('actual_price') - F('total_price'))
    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

    return render(request,'admin/sales_report.html',{'orders':orders,'total_discount':total_discount,'total_order_amount':total_order_amount,'from_date':from_date,'to_date':to_date,'range':'week'})



def sales_report_month(request):

    to_date=timezone.now().date()
    from_date=to_date-timezone.timedelta(days=30)
    orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
    discount=F('actual_price') - F('total_price'))
    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

    return render(request,'admin/sales_report.html',{'orders':orders,'total_discount':total_discount,'total_order_amount':total_order_amount,'from_date':from_date,'to_date':to_date,'range':'month'})

@csrf_exempt
def sales_report_custom(request):
    print('function called')
    if request.method == 'POST':
        print('post method')

        from_date=request.POST['from_date']
        to_date=request.POST['to_date']

        print(from_date)
        print(to_date)
        orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
        discount=F('actual_price') - F('total_price'))
        total_discount=orders.aggregate(Sum('discount'))['discount__sum']
        total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']

        return render(request,'admin/sales_report.html',{'orders':orders,'total_discount':total_discount,'total_order_amount':total_order_amount,'from_date':from_date,'to_date':to_date,'range':'custom'})


#***************************************************************************
# for pdf response
#*******************************************************

def sales_report_all_pdf(request):
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle('PDF Report')

    orders = Order.objects.filter(payment_status=True).annotate(
        discount=F('actual_price') - F('total_price')
    )

    total_discount = orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount = orders.aggregate(Sum('total_price'))['total_price__sum']

    # Set initial coordinates
    x = 50
    y = 750

    # Draw the report title and other details
    p.drawString(x, y, 'OVERALL SALES REPORT')
    y -= 25
    p.drawString(x, y, f'Sales Count: {orders.count()}')
    y -= 25
    p.drawString(x, y, f'Order Amount: {total_order_amount}')
    y -= 25
    p.drawString(x, y, f'Total Discount: {total_discount}')
    y -= 50

    data = [['Id', 'Order Date', 'User', 'Total', 'Discount', 'Paid', 'Payment Method']]  # Add headers to the data list
    for order in orders:
        row = [str(order.id), str(order.order_date.date()), str(order.user), str(order.actual_price), str(order.discount), str(order.total_price), str(order.payment_method)]
        data.append(row)

    table = Table(data)

    table.setStyle(TableStyle(
        [
            ('BACKGROUND', (0,0), (-1,0), colors.grey), 
            ('BACKGROUND', (0,1), (-1,-1), colors.white), 
            ('GRID', (0,0), (-1,-1),1, colors.black),  # Grid color
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # Center align all cells
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),  # Middle align all cells
            ('FONTSIZE', (0,0), (-1,-1), 14),  # Increase the font size
            ('LEFTPADDING', (0,0), (-1,-1), 12),  # Increase the left padding
            ('RIGHTPADDING', (0,0), (-1,-1), 12),  # Increase the right padding
            ('TOPPADDING', (0,0), (-1,-1), 12),  # Increase the top padding
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),  # Increase the bottom padding
            ('COLUMN_WIDTHS', (0,0), (-1,-1), [50, 100, 100, 100, 100, 100, 150])  # Specify the width for each column
        ]
    ))
    w, h = table.wrapOn(p, 600, 600)
    table.drawOn(p, x, y-h)  # Draw the table at the current position

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="overall_sales_report.pdf")


def sales_report_pdf(request,range):
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f"Last {range} sales report")


    if range=='day':
        to_date=timezone.now().date()
        from_date=to_date-timezone.timedelta(days=1)

    elif range == 'week':
        to_date = timezone.now().date()
        from_date = to_date - timezone.timedelta(days=7)


    elif range == 'month':
        to_date=timezone.now().date()
        from_date=to_date-timezone.timedelta(days=30)

    


    orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
    discount=F('actual_price') - F('total_price'))
    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']


    x = 50
    y = 750

    # Draw the report title and other details
    p.drawString(x, y, f"SALES REPORT  {from_date} - {to_date}")
    y -= 25
    p.drawString(x, y, f'Sales Count: {orders.count()}')
    y -= 25
    p.drawString(x, y, f'Order Amount: {total_order_amount}')
    y -= 25
    p.drawString(x, y, f'Total Discount: {total_discount}')
    y -= 50

    data = [['Id', 'Order Date', 'User', 'Total', 'Discount', 'Paid', 'Payment Method']]  # Add headers to the data list
    for order in orders:
        row = [str(order.id), str(order.order_date.date()), str(order.user), str(order.actual_price), str(order.discount), str(order.total_price), str(order.payment_method)]
        data.append(row)

    table = Table(data)

    table.setStyle(TableStyle(
        [
            ('BACKGROUND', (0,0), (-1,0), colors.grey), 
            ('BACKGROUND', (0,1), (-1,-1), colors.white), 
            ('GRID', (0,0), (-1,-1),1, colors.black),  # Grid color
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # Center align all cells
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),  # Middle align all cells
            ('FONTSIZE', (0,0), (-1,-1), 14),  # Increase the font size
            ('LEFTPADDING', (0,0), (-1,-1), 12),  # Increase the left padding
            ('RIGHTPADDING', (0,0), (-1,-1), 12),  # Increase the right padding
            ('TOPPADDING', (0,0), (-1,-1), 12),  # Increase the top padding
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),  # Increase the bottom padding
            ('COLUMN_WIDTHS', (0,0), (-1,-1), [50, 100, 100, 100, 100, 100, 150])  # Specify the width for each column
        ]
    ))
    w, h = table.wrapOn(p, 600, 600)
    table.drawOn(p, x, y-h)  # Draw the table at the current position

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Sales report  {from_date} - {to_date}.pdf")


def sales_report_pdf_customrange(request,from_date,to_date):
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f"Sales report {from_date} to {to_date}")


    if range=='day':
        to_date=timezone.now().date()
        from_date=to_date-timezone.timedelta(days=1)

    elif range == 'week':
        to_date = timezone.now().date()
        from_date = to_date - timezone.timedelta(days=7)


    elif range == 'month':
        to_date=timezone.now().date()
        from_date=to_date-timezone.timedelta(days=30)

    


    orders=Order.objects.filter(payment_status=True, order_date__range=(from_date, to_date)).annotate(
    discount=F('actual_price') - F('total_price'))
    total_discount=orders.aggregate(Sum('discount'))['discount__sum']
    total_order_amount=orders.aggregate(Sum('total_price'))['total_price__sum']


    x = 50
    y = 750

    # Draw the report title and other details
    p.drawString(x, y, f"SALES REPORT  {from_date} - {to_date}")
    y -= 25
    p.drawString(x, y, f'Sales Count: {orders.count()}')
    y -= 25
    p.drawString(x, y, f'Order Amount: {total_order_amount}')
    y -= 25
    p.drawString(x, y, f'Total Discount: {total_discount}')
    y -= 50

    data = [['Id', 'Order Date', 'User', 'Total', 'Discount', 'Paid', 'Payment Method']]  # Add headers to the data list
    for order in orders:
        row = [str(order.id), str(order.order_date.date()), str(order.user), str(order.actual_price), str(order.discount), str(order.total_price), str(order.payment_method)]
        data.append(row)

    table = Table(data)

    table.setStyle(TableStyle(
        [
            ('BACKGROUND', (0,0), (-1,0), colors.grey), 
            ('BACKGROUND', (0,1), (-1,-1), colors.white), 
            ('GRID', (0,0), (-1,-1),1, colors.black),  # Grid color
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # Center align all cells
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),  # Middle align all cells
            ('FONTSIZE', (0,0), (-1,-1), 14),  # Increase the font size
            ('LEFTPADDING', (0,0), (-1,-1), 12),  # Increase the left padding
            ('RIGHTPADDING', (0,0), (-1,-1), 12),  # Increase the right padding
            ('TOPPADDING', (0,0), (-1,-1), 12),  # Increase the top padding
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),  # Increase the bottom padding
            ('COLUMN_WIDTHS', (0,0), (-1,-1), [50, 100, 100, 100, 100, 100, 150])  # Specify the width for each column
        ]
    ))
    w, h = table.wrapOn(p, 600, 600)
    table.drawOn(p, x, y-h)  # Draw the table at the current position

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Sales report  {from_date} - {to_date}.pdf")
