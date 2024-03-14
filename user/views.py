from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress,Cart,Order,OrderItem,OrderAddress,Wishlist,TempData
from products.models import Category,ProductImages,Products,ProductVarient
from wallet.models import Wallet,WalletTransactions
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model,authenticate,login,logout
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
import razorpay
from admin.models import Coupon,AppliedCoupon
from datetime import datetime
from decimal import Decimal
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table,TableStyle
from reportlab.lib import colors

# Create your views here.

def forgot_password(request):

    return render(request,'user/forgot_password.html')

def invoice(request,id):
    order=Order.objects.get(id=id)
    print(order)
    order_items=OrderItem.objects.filter(order=order)
    order_address=OrderAddress.objects.get(order=order)
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle('Sale Invoice')

  
    # Set initial coordinates
    x = 50
    y = 750

    # Draw the report title and other details
    p.drawString(x+200, y, '-- TAX INVOICE --')
    y -= 25
    p.line(x, y, x + 500, y)
    y -= 25
    p.drawString(x, y, f'KINO MART')
    y -= 15
    p.drawString(x, y, f'Bangalore, 600123')
    y -= 15
    p.drawString(x, y, f'Email : mart@kino.com')
    y -= 15
    p.drawString(x, y, f'Customer Care: +91 9876543210')
    y -= 50

    p.line(x, y+20, x + 500, y+20)
    y += 135

    x+=280



     # Draw the report title and other details
    y -= 25
    y -= 20
    p.drawString(x, y, f'Invoice No: {order.id}')
    y -=15
    p.drawString(x, y, f'Invoice Date: {order.order_date.strftime('%d-%m-%Y')}')
    y -= 15
    p.drawString(x, y, f'Order Amount: {order.total_price}')
    y -= 15
    p.drawString(x, y, f'Order Id: {order.order_id}')
    y -= 50

    y -= 30

    x-=280
#Draw address details
    p.drawString(x,y, "Shipping Address")
    y-=30
    p.drawString(x,y, f"{order.user}")
    y-=15
    p.drawString(x,y, f"{order_address.address_line}")
    y-=15
    
    p.drawString(x,y, f"{order_address.landmark}")
    y-=15
    p.drawString(x,y, f"PINCODE: {order_address.pin}")
    y-=15
    p.drawString(x,y, f"{order_address.city}")
    y-=15
    p.drawString(x,y, f"{order_address.state}")
    y-=15
    p.drawString(x,y, f"MOB: {order.user.phone}")
    y-=25

#Draw payment summary
    y+=145
    x+= 280
    p.drawString(x,y, "Payment Summary")
    y-=30
    p.drawString(x,y, "Sub Total")
    p.drawString(x+100,y, f":  {order.actual_price-50}")
    y-=15

    p.drawString(x,y, "Delivery Charge")
    p.drawString(x+100,y, f":  50.00")
    y-=15

    p.drawString(x,y, "Discount")
    p.drawString(x+100,y, f":  {order.actual_price-order.total_price}")
    y-=15

    p.drawString(x,y, "Tax")
    p.drawString(x+100,y, f":  0.00")
    y-=20

    p.drawString(x,y, "TOTAL")
    p.drawString(x+100,y, f":  {order.total_price}")
    y-=25


    y-=25



    x-= 280
    data = [['Sl','Item Id', 'Product', 'Qty', 'Total']]  # Add headers to the data list
    for i,item in enumerate(order_items, start=1) :
        row = [str(i),str(item.id), str(item.product), str(item.quantity),str(item.price)]
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

    y-=h


    p.drawRightString(x+500,y-100, "Authorised Signature")
    p.drawRightString(x+500,y-130, "Kino Mart")
    
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")



    return redirect('/')
def index(request):
    wishlist_items=None
    if request.user.is_authenticated and Wishlist.objects.filter(user=request.user).exists():
        wishlist_items=Wishlist.objects.filter(user=request.user)
    categories = Category.objects.prefetch_related('subcategories').all()
    category_data = []
    for category in categories:
        subcategories = category.subcategories.all()
        subcategory_data = []    
        for subcategory in subcategories:
            products = subcategory.products.all()
            product_data = []        
            for product in products:
                images = ProductImages.objects.filter(product_id=product).first()
                image = images.image.url if images else None
                variant = product.varients.first()
                is_wishlist=False
                if wishlist_items and  wishlist_items.filter(product=product).exists():
                    is_wishlist=True

                
                    


                if variant and not variant.is_holded:
                    product_data.append({
                    'product_id': product.id,
                    'variant_id':variant.id,
                    'product_name': product.product_name,
                    'description': product.description,
                    'price': variant.price,
                    'offer_price':variant.offer_price,
                    'quantity':variant.quantity,
                    'unit':variant.unit, 
                    'brand': product.brand.brand_name,
                    'is_offer':product.is_offer,
                    'offer':product.offer,
                    'image': image,     
                    'is_wishlist':is_wishlist, 
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
    return render(request,'user/index.html',{'categories': category_data,})


def search_index(request):
    search=request.GET['search']
    wishlist_items=None
    if request.user.is_authenticated and Wishlist.objects.filter(user=request.user).exists():
        wishlist_items=Wishlist.objects.filter(user=request.user)
    categories = Category.objects.prefetch_related('subcategories').all()
    category_data = []
    for category in categories:
        subcategories = category.subcategories.all()
        subcategory_data = []    
        for subcategory in subcategories:
            products = subcategory.products.filter(Q(product_name__icontains=search) | Q(description__icontains=search))
            product_data = []        
            for product in products:
                is_wishlist=False
                if wishlist_items and  wishlist_items.filter(product=product).exists():
                    is_wishlist=True
                images = ProductImages.objects.filter(product_id=product).first()
                image = images.image.url if images else None
                variant = product.varients.first()

                
                    


                if variant and not variant.is_holded:
                    product_data.append({
                    'product_id': product.id,
                    'variant_id':variant.id,
                    'product_name': product.product_name,
                    'description': product.description,
                    'price': variant.price,
                    'offer_price':variant.offer_price,
                    'quantity':variant.quantity,
                    'unit':variant.unit, 
                    'brand': product.brand.brand_name,
                    'is_offer':product.is_offer,
                    'offer':product.offer,
                    'image': image, 
                    'is_wishlist':is_wishlist,     
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

    
    return render(request, 'user/search_index.html', {'categories': category_data,})
 
def reset_password(request):
    if request.method == 'POST':
        email=request.POST.get('mob_email')

        if not User.objects.filter(email=email).exists():
            messages.info(request,'Email not existing!')
            return redirect('forgot_password')
        
        otp=random.randint(10000,99999)
        request.session['otp']=otp
        request.session['email']=email


        subject = 'RESET PASSWORD'
        message = f' Your otp for PASSWORD RESET is {otp} \n If it is not from you, please change your password immedietly!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email,]   
        print(otp)
        send_mail( subject, message, email_from, recipient_list )
        print("email send success")
        return render(request,'user/otp_forgot_password.html',{'email':email})
    
    email=request.session['email']
    return render(request,'user/otp_forgot_password.html',{'email':email})
    



def otp_check_forgot_password(request):
    if request.method == 'POST':
        otp= request.POST['otp']     
        if otp != str(request.session['otp']):
            messages.info(request,'You Entered a Wrong OTP!')  
            return redirect('reset_password')
        else:
            if request.POST['password1'] != request.POST['password2']:
                messages.info(request,'Password not matching!')
                return redirect('reset_password')
            else:

            # everything is correct, then changing password and redirect to login
                password= request.POST['password1']
                email= request.POST['email']
                user=User.objects.get(email=email)
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)


                messages.info(request,'Password changed successfully')
                return redirect('login_user')
                



def signup(request):
    if request.method=='POST':

        User=get_user_model()
        request.session.clear()
        

        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        phone=request.POST['mobile']

        if request.POST['refferal_code']:
            refferal_code=request.POST['refferal_code']
            if not User.objects.filter(referral_code=refferal_code).exists():

                messages.info(request,'You have entered a wrong refferal code!')

                return redirect('signup')
            else:
                request.session['refferal_code']=refferal_code


# validating mobile number
        if len(phone)!=10:
            messages.info(request,'Mobile number must be 10 digits')

            return redirect('signup')
        password=request.POST['password1']
        address_line=request.POST['address']
        city=request.POST['city']
        landmark=request.POST['landmark']
        pin=request.POST['pin']
        if not pin.isdigit():
            messages.info(request,'Pincode must be numeric')

            return redirect('signup')

        
        if password != request.POST['password2']:
            messages.info(request,'Password not matching!')
            return redirect('signup')


    
    # checking email taken
        if User.objects.filter(Q(email__iexact=email)|Q(phone__iexact=phone)).exists():
            user= User.objects.filter(Q(email__iexact=email)|Q(phone__iexact=phone)).first()
            if user.is_active:
                messages.info(request,'Already registerd with this email/phone ')
                return redirect('login_user')
            else:
                messages.info(request,'Already registerd with this email. Please verify your email with otp to compleate the registration')
                otp=random.randint(10000,99999)
                request.session['otp']=otp


                subject = 'Thank you for registering on Kino Mart'
                message = f' Your otp for registration is {otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email,]   
                print(otp)
                send_mail( subject, message, email_from, recipient_list )
                print("email send success")
                request.session['user_id']=user.id
                return render(request,'user/otp.html',{'email':email})



        

   
        
        
# we need to send email for otp verification
        
        otp=random.randint(10000,99999)
        request.session['otp']=otp
        print("OTP SEND",otp)

        subject = 'Thank you for registering on Kino Mart'
        message = f' Your otp for registration is {otp}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email,]   
        send_mail( subject, message, email_from, recipient_list )
        print("email send success")


        User=get_user_model()
        us=User(first_name=first_name,last_name=last_name,email=email,phone=phone,username=email,is_active=False)
        us.password=make_password(password)
        
        us.save()
        Wallet.objects.create(user=us)

        
        ad=UserAddress(pin=pin,address_line=address_line,city=city,landmark=landmark,user_id=us)
        ad.save()
        request.session['user_id']=us.id
        request.session['user_address']=ad.id


        

        return render(request,'user/otp.html',{'email':email})
    
    else:
        return render(request,'user/signup.html')
    

def otp_user(request):
    if request.method=='POST':
        print(request.POST['otp'])
        print("Generated OTP:",request.session['otp'])
        if request.POST['otp']==str(request.session['otp']):
            print("OTP VALIDATED SUCCESSFULLY")



# When otp validation is successfull, create user instance. 
            user=User.objects.get(id=request.session['user_id'])
            user.is_active=True
            user.save()

            refferal_code=request.session.get('refferal_code')

            if refferal_code:
                # if refferal_code then adding money to reffered user 
                        reffered_user=User.objects.get(referral_code=refferal_code)
                        wallet=Wallet.objects.get(user=reffered_user)
                        wallet.balance+=100
                        wallet.last_transaction="+100"
                        wallet.save()

                        WalletTransactions.objects.create(wallet=wallet,transaction_amount=100,discription=f"Refferal bonus for {user}")
                # adding money to new user 
                        wallet=Wallet.objects.get(user=user)
                        wallet.balance+=100
                        wallet.last_transaction="+100"
                        wallet.save()

                        WalletTransactions.objects.create(wallet=wallet,transaction_amount=100,discription=f"Refferal bonus by {reffered_user}")


            
            # creating session when user registered succussfully with auto login
            
            request.session['user_email']=user.email
            # user = authenticate(request, username=user.username, password=user.password)
            if user is not None:
                # Log the user in
                # login(request, user)
                user.is_active = True
                user.save()
                messages.info(request,'Signup Success!!')

                return redirect('login_user')
            messages.info(request,'Something went wrong!!')
            
            return redirect('otp_user')
        else:
            messages.info(request,'Incorrect OTP entered!!')
            return redirect('otp_user')



    return render(request,'user/otp.html')


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
    return render(request,'user/login.html')
    


def logout_user(request):
    request.session.clear()
    logout(request)
    return redirect('home')



def view_product(request,id):
    
    product=Products.objects.prefetch_related('varients','images').get(id=id)
    is_wishlist=False
    if request.user.is_authenticated and Wishlist.objects.filter(user=request.user,product=product).exists():
        is_wishlist=True
    varients=product.varients.all()
    varient_data=[]
    for varient in varients:
        if not varient.is_holded:
            varient_data.append({
                'id':varient.id,
                'qty':varient.quantity,
                'unit':varient.unit,
                'is_offer':product.is_offer,
                'offer_price':varient.offer_price,
                'price':varient.price,
                

            })
        
    


    return render(request,'user/view_product.html',{'product':product,'varient_data':varient_data,'is_wishlist':is_wishlist })





# User profile page related

def user_page(request):


    if 'user_email' in request.session:
        user=request.user
        return render(request,'user/user_profile.html',{'user':user})
    
    else:
        return redirect('login_user')
    
def user_address(request):
    user=User.objects.get(email=request.session['user_email'])
    
    addresses=UserAddress.objects.filter(user_id__exact=user).order_by('-is_default',)
    return render(request,'user/user_address.html',{'addresses':addresses,'user':user})


def add_address(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        pin = request.POST.get('pin')
        state = request.POST.get('state')

        user=User.objects.get(email=request.session['user_email'])
        # Create a new address instance
        new_address = UserAddress.objects.create(city=city,landmark=landmark,state=state,pin=pin,address_line=address,user_id=user,is_default=False)
        new_address.save()
        return JsonResponse({'message': 'Address added successfully!'}) 
        # return redirect('user_address')
    

def update_address(request):
    if request.method=='POST':
        address = request.POST.get('address')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        pin = request.POST.get('pin')
        state = request.POST.get('state')
        
        ad=UserAddress.objects.get(id=int(request.POST.get('ad-id')))
        

        # Update address instance
        ad.address_line=address
        ad.landmark=landmark
        ad.city=city
        ad.pin=pin
        ad.state=state

        ad.save()

        return redirect('user_address')




def delete_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address=UserAddress.objects.get(id=address_id)
        if address.is_default:
            return JsonResponse({'message': 'This is your default address, Change it and try again!!'})

        address.delete()
        return JsonResponse({'message': 'Address deleted successfully!'})
    

@csrf_exempt
def default_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        # Fetch the UserAddress instance
        ad = UserAddress.objects.get(id=address_id)
        addresses=UserAddress.objects.filter(user_id__exact=ad.user_id)

        for address in addresses:
            address.is_default=False
            address.save()

        ad.is_default=True
        ad.save()

        
        return JsonResponse({'status': 'success'})
    

def order_history(request):

    user=request.user
    orders=Order.objects.filter(user=user).prefetch_related('items').order_by('-id')

    orders_list=[]
    for order in orders:
        order_id=order.id
        order_date=order.order_date.date()
        total=order.total_price
        payment_method=order.payment_method
        status=order.status
        payment_status=order.payment_status

        item_details=[]

        for item in order.items.all():
            image=ProductImages.objects.filter(product_id=item.product.product_id.id).first()

            product=item.product
            product_id=product.product_id.id
            quantity=item.quantity
            price=item.price
            item_details.append(
                {
                    'product':product,
                    'product_id':product_id,
                    'quantity':quantity,
                    'price':price,
                    'image':image,
                    


                }
            )

        

        orders_list.append(
            {
                'order_id':order_id,
                'order_date':order_date,
                'total':total,
                'payment_method':payment_method,
                'status':status,
                'return_status':order.return_status,
                'items':item_details,
                'payment_status':payment_status,
                'user':order.user,
                'razorpay_order_id':order.order_id,

            }
        )

            
    return render(request,'user/order_history.html',{'orders':orders_list,})

def cancel_order(request,id):
    order=Order.objects.get(id=id)
    order.return_status="Cancelled"
    order.save()

    if order.payment_status:
        wallet=Wallet.objects.get(user=request.user)
        wallet.balance+=order.total_price
        wallet.last_transaction=f'+{order.total_price}'
        wallet.save()

        transaction=WalletTransactions.objects.create(wallet=wallet,transaction_amount=order.total_price,discription=f'Order ID:{order.id} - refund')
        messages.info(request,f'Order cancelled and ₹{order.total_price} has been refunded to your wallet')


        return redirect('order_history')
    
    messages.info(request,f'Order cancelled')


    return redirect('order_history')

def return_order(request,id):
    order=Order.objects.get(id=id)
    order.return_status='Returned'
    order.save()

    return redirect('order_history')


def wishlist(request):

    wishlist_items=Wishlist.objects.filter(user=request.user)


    product_list=[]
    for item in wishlist_items:
        product=item.product
        image=ProductImages.objects.filter(product_id=product).first()
        image = image.image.url if image else None
        variant=product.varients.first()

        product_list.append({
            'product_id':product.id,
            'product_name':product.product_name,
            'image':image,
            'variant_id':variant.id,


        })



    return render(request,'user/wishlist.html',{'products':product_list})


def wallet(request):
    wallet=Wallet.objects.get(user=request.user)
    transactions=WalletTransactions.objects.filter(wallet=wallet).order_by('id')


    transactions=WalletTransactions.objects.filter(wallet=wallet).order_by('id')
    return render(request,'user/wallet.html',{'wallet':wallet,'transactions':transactions})






@login_required
def edit_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        user = request.user  # Get the logged in user

        # Validate the data
        if not first_name or not last_name or not email or not phone:
            return JsonResponse({'error': 'All fields are required'})

        # Update user details
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = email
        user.phone = phone

        # Save the user and handle potential errors
        try:
            user.full_clean()  # Validate the model
            user.save()
        except ValidationError as e:
            return JsonResponse({'error': str(e)})

        return JsonResponse({'message': 'Profile updated successfully!'})
    


def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user =request.user
        
        # Validate old password
        if not user.check_password(old_password):
            return JsonResponse({'message': 'You have entered a wrong old password!!!'})

        # Check if new passwords match
        if new_password1 != new_password2:
            return JsonResponse({'message': 'New passwords not matching!'})

        # Edit user password
        user.set_password(new_password1)
        user.save()
        update_session_auth_hash(request, user)
        


        return JsonResponse({'message': 'Password changed successfully!'})
    

def cart(request):
    if not request.user.is_authenticated:
            messages.info(request,'You need to login first for adding items to the cart')
            return redirect('login_user')
    user=request.user
    cart_items=Cart.objects.filter(user=user).order_by('id')
    item_details=[]
    product_total=0
    delivery=50


    address = UserAddress.objects.filter(Q(user_id=user) & Q(is_default=True)).first()
    print(address)

    for item in cart_items:
        variant=item.product
        quantity=item.quantity
        price=0

        if variant.offer_price:
            price=variant.offer_price

        else:
            price=variant.price
        product_total+=(price*quantity)

        product=variant.product_id
        image=ProductImages.objects.filter(product_id=product).first()


        item_details.append(
            {
                'id':item.id,
                'product_name':product.product_name,
                'product_id':product.id,
                'image':image.image.url if image else None,
                'quantity':quantity,
                'unit':f'{variant.quantity}/{variant.unit}',
                'price':price,

            }
        )
        


    context={'cart_items':item_details,'product_total':product_total,'delivery':delivery,'total':product_total+delivery,'address':address}
    return render(request,'user/cart.html',context)




@csrf_exempt
def remove_from_wishlist(request):
    productId=int(request.POST['productId'])
    product=Products.objects.get(id=productId)
    wishlist_item=Wishlist.objects.filter(user=request.user,product=product)
    wishlist_item.delete()
    return JsonResponse({'message': 'Product removed from wishlist successfully!'})


@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':

        productId = int(request.POST.get('productId'))
        product=Products.objects.get(id=productId)

# finding rate from database, not from template.
        
        if not request.user.is_authenticated:
            messages.info(request,'You need to login first for adding items to the wishlist')

            return JsonResponse({'error': 'login_required'})
        user=request.user

        if  not productId or not user:
            return JsonResponse({'error': 'An error occured!!'})
        

        

        if Wishlist.objects.filter(user=user,product=product).exists():
            return JsonResponse({'message': 'Product already in wishlist!'})


        try:
            Wishlist.objects.create(user=user,product=product)
            print("whishlist added")
            return JsonResponse({'message': 'Product added to wishlist successfully!'})

        except:
            return JsonResponse({'message': 'Product not added to wishlist. An error occured!!'})




# add_to_cart ajax call now from detail page
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':

        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity'))
        variantId = int(request.POST.get('variantId'))

# finding rate from database, not from template.
        
        if not request.user.is_authenticated:
            messages.info(request,'You need to login first for adding items to the cart')

            return JsonResponse({'error': 'login_required'})
        user=request.user

        if not product_id or not quantity or not variantId or not user:
            return JsonResponse({'error': 'An error occured!!'})
        

        # If the variant is already in the cart for same user, then we can add to that
        cart_item = Cart.objects.filter(user=user, product=variantId).first()
        var=ProductVarient.objects.get(id=variantId)


                
        # if the item is already in the wishlist, we need delete that
        wishlist_item = Wishlist.objects.filter(user=user,product=product_id)

        try:
            if wishlist_item:
                wishlist_item.delete()
            if cart_item:
                print("cart already exists")
                cart_item.quantity+=quantity
                cart_item.price=var.price*cart_item.quantity
                cart_item.save()
                print("cart added")
                return JsonResponse({'message': 'Product added to cart successfully!'})

            price=var.price*quantity

            new_cart=Cart.objects.create(user=user,product=var,quantity=quantity,price=price)
            new_cart.save()
            print("cart added")
            return JsonResponse({'message': 'Product added to cart successfully!'})

        except:
            return JsonResponse({'message': 'Product not added to cart. Some error occured!!'})


# cart quantity updating from the cart page


@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        cart_id = request.POST.get('cartid')
        new_quantity = int(request.POST.get('quantity'))

        print("cartid",cart_id)
        print(new_quantity)

            

        # Fetch the cart item
        cart_item = Cart.objects.get(id=cart_id)
        if new_quantity==0:
            cart_item.delete()
            cart_items = Cart.objects.filter(user=request.user) 
            new_total = sum(item.price for item in cart_items)
            grand_total=new_total+50
            return JsonResponse({'message': 'Item removed from the cart!','newTotal': new_total,'grand_total':grand_total})

        product_variant = cart_item.product

        # Update the quantity
        cart_item.quantity = new_quantity

        if product_variant.offer_price:
            cart_item.price= new_quantity*product_variant.offer_price

        else:
            cart_item.price= new_quantity*product_variant.price
        cart_item.save()


        item_total=cart_item.price

        cart_items = Cart.objects.filter(user=request.user) 
        new_total = sum(item.price for item in cart_items)
        grand_total=new_total+50


        return JsonResponse({'message': 'Cart updated successfully!','newTotal': new_total,'grand_total':grand_total,'item_total':item_total})

    else:
        return JsonResponse({'error': 'Invalid request'})

        


def cart_count(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).count()
        return JsonResponse({'count': count})
    else:
        return JsonResponse({'count': 0})

def continue_checkout(request):
    if request.method == 'POST':
        order_id=request.POST['order_id']
        payment_method=request.POST['payment']

        order=Order.objects.get(id=order_id)
        user=order.user
        print(order)

    #for wallet payment
        if payment_method=='wallet':
            wallet=Wallet.objects.get(user=user)

            print("wallet balance",wallet.balance)
            if wallet.balance < order.total_price: #insuficiant balance
                messages.info(request,"You don't have sufficiant balance on your wallet!!")
                print("You don't have sufficiant balance on your wallet!!")

                return redirect('wallet')
            # if wallet has sufficiant balance, then creating order.
            client = razorpay.Client(auth=('rzp_test_b714EP5tPrXbn2', 'I5DOPeyeM27wIDIO37uP0foG'))

            # create order
            amount = int(float(order.total_price) * 100)
            response_payment = client.order.create(dict(amount=amount,currency='INR'))

            print(response_payment)


            order_id=response_payment['id']
            order_status=response_payment['status']

            if order_status == 'created':
           

                
                # updating wallet
                wallet.balance-=order.total_price
                wallet.last_transaction=f'-{order.total_price}'
                wallet.save()

                w_transaction=WalletTransactions.objects.create(wallet=wallet,transaction_amount=-(order.total_price),discription=f'Order ID:{order.id} purchase')

                #updating order status
                order.order_id=order_id
                order.payment_status=True
                order.payment_method=payment_method
                order.save()

                discount=Decimal(order.actual_price)-Decimal(order.total_price)

                return render(request, 'user/success.html', {'status': True,'discount':discount,'order_id':order.id})
            


    #Wallet payment ends here
            
            #for upi or cart
        else:
            
    # for order like upi or card, creating razorpay order and storing details in tempdata
            print("CARD OR UPI")
            client = razorpay.Client(auth=('rzp_test_b714EP5tPrXbn2', 'I5DOPeyeM27wIDIO37uP0foG'))

            # create order
            amount = int(float(order.total_price) * 100)
            response_payment = client.order.create(dict(amount=amount,currency='INR'))

            order_id=response_payment['id']
            order_status=response_payment['status']

            if order_status == 'created':
                order.order_id=order_id
                order.payment_method=payment_method
                order.save()
                

            
            

                return render(request, 'user/order_history.html', {'show_checkout_modal': True,'selected_order':order,})




        return redirect('order_history')

def checkout(request):
    if request.method == 'POST':
        user=request.user
        payment_method=request.POST['payment']
        address_id=request.POST['address_id']
        instructions=request.POST.get('instructions')
        total_price=Decimal(request.POST['total_price'])

        print(payment_method)
# for wallet payment
        if payment_method=='wallet':
            wallet=Wallet.objects.get(user=user)

            print("wallet balance",wallet.balance)
            print("order amount",total_price)
            if wallet.balance < total_price: #insuficiant balance
                messages.info(request,"You don't have sufficiant balance on your wallet!!")
                print("You don't have sufficiant balance on your wallet!!")

                return redirect('cart')
            # if wallet has sufficiant balance, then creating order.
            address=UserAddress.objects.get(id=address_id)
            client = razorpay.Client(auth=('rzp_test_b714EP5tPrXbn2', 'I5DOPeyeM27wIDIO37uP0foG'))

            # create order
            amount = int(float(total_price) * 100)
            response_payment = client.order.create(dict(amount=amount,currency='INR'))

            print(response_payment)


            order_id=response_payment['id']
            order_status=response_payment['status']

            if order_status == 'created':
                order=Order.objects.create(user=user,payment_method=payment_method,delivery_instructions=instructions,total_price=total_price,order_id=order_id)

                order_address = OrderAddress.objects.create(city=address.city,state=address.state,landmark=address.landmark,pin=address.pin,address_line=address.address_line,order=order)


                cart_items=Cart.objects.filter(user=user)

                actual_price=50 #Adding delivery charge
                for item in cart_items:
                    single_price=item.product.price
                    actual_price+=(single_price*item.quantity)

                    # updating stock
                    variant=item.product
                    variant.stock-=item.quantity
                    variant.save()
                    print("stock updatedd:::")

                    OrderItem.objects.create(order=order,product=item.product,quantity=item.quantity,price=item.price)
                
                order.actual_price=actual_price 
                order.payment_status=True
                order.save()
                print("actual_order price",actual_price)

                cart_items.delete()

                if 'coupon_code' in request.POST and request.POST['coupon_code']:
                    code = request.POST['coupon_code']
                    coupon=Coupon.objects.get(coupon_code=code)
                    AppliedCoupon.objects.create(user=request.user,coupon=coupon)
                    coupon.count-=1
                    coupon.save()


                # updating wallet
                wallet.balance-=total_price
                wallet.last_transaction=f'-{total_price}'
                wallet.save()

                w_transaction=WalletTransactions.objects.create(wallet=wallet,transaction_amount=-(total_price),discription=f'Order ID:{order.id} purchase')

                print("actualll",actual_price)
                print("totalll",total_price)
                discount=Decimal(actual_price)-Decimal(total_price)

                return render(request, 'user/success.html', {'status': True,'discount':discount,'order_id':order.id})
            


    #Wallet payment ends here


    #for cod payment
        if payment_method=='cod':

            if total_price >=1000:
                messages.info(request,"Order above 1000 can't be cash on delevery")
                return redirect('cart')

            
            # if wallet has sufficiant balance, then creating order.
            address=UserAddress.objects.get(id=address_id)
            client = razorpay.Client(auth=('rzp_test_b714EP5tPrXbn2', 'I5DOPeyeM27wIDIO37uP0foG'))

            # create order
            amount = int(float(total_price) * 100)
            response_payment = client.order.create(dict(amount=amount,currency='INR'))

            print(response_payment)


            order_id=response_payment['id']
            order_status=response_payment['status']

            if order_status == 'created':
                order=Order.objects.create(user=user,payment_method=payment_method,delivery_instructions=instructions,total_price=total_price,order_id=order_id)

                order_address = OrderAddress.objects.create(city=address.city,state=address.state,landmark=address.landmark,pin=address.pin,address_line=address.address_line,order=order)


                cart_items=Cart.objects.filter(user=user)

                actual_price=50 #Adding delivery charge
                for item in cart_items:
                    single_price=item.product.price
                    actual_price+=(single_price*item.quantity)

                    # updating stock
                    variant=item.product
                    variant.stock-=item.quantity
                    variant.save()
                    print("stock updatedd:::")

                    OrderItem.objects.create(order=order,product=item.product,quantity=item.quantity,price=item.price)
                
                order.actual_price=actual_price 
                order.payment_status=False
                order.save()
                print("actual_order price",actual_price)

                cart_items.delete()

                if 'coupon_code' in request.POST and request.POST['coupon_code']:
                    code = request.POST['coupon_code']
                    coupon=Coupon.objects.get(coupon_code=code)
                    AppliedCoupon.objects.create(user=request.user,coupon=coupon)
                    coupon.count-=1
                    coupon.save()


                
                print("actualll",actual_price)
                print("totalll",total_price)
                discount=Decimal(actual_price)-Decimal(total_price)

                return render(request, 'user/success.html', {'status': True,'discount':discount,})
            #COD ENDS HERE  ############################################################################################


        # for order like upi or card, creating razorpay order and storing details in tempdata
        print("CARD OR UPI")
        client = razorpay.Client(auth=('rzp_test_b714EP5tPrXbn2', 'I5DOPeyeM27wIDIO37uP0foG'))

        # create order
        amount = int(float(total_price) * 100)
        response_payment = client.order.create(dict(amount=amount,currency='INR'))

        order_id=response_payment['id']
        order_status=response_payment['status']

        if order_status == 'created':
            
            if TempData.objects.filter(user=user).exists():
                data=TempData.objects.get(user=user)
                data.address_id=address_id
                data.payment_method=payment_method
                data.instructions=instructions
                data.total_price=total_price
                data.order_id=order_id
                data.save()
            else:
                data=TempData.objects.create(address_id=address_id,user=user,payment_method=payment_method,instructions=instructions,total_price=total_price,order_id=order_id)
            print("TEMP DATA CREATED")


        if 'coupon_code' in request.POST and request.POST['coupon_code']:
                code = request.POST['coupon_code']
                data.coupon_code=code
                data.save()
        

        return render(request, 'user/cart.html', {'show_checkout_modal': True,'order':data,})


#FOR GET METHOD
    return redirect ('cart')
    
    
    
@csrf_exempt
def payment_status(request):
    print("ghjkgfhjghj")

    response=request.POST
    print("******************",response)
    dic={
    'razorpay_order_id': response['razorpay_order_id'],
    'razorpay_payment_id': response['razorpay_payment_id'],
    'razorpay_signature': response['razorpay_signature'],
    }
    client = razorpay.Client(auth=("rzp_test_b714EP5tPrXbn2", "I5DOPeyeM27wIDIO37uP0foG"))



    try:

        status=client.utility.verify_payment_signature(dic)
        print("status:",status)
        print(type(status))

        if status:

            data=TempData.objects.get(order_id=response['razorpay_order_id'])
            print("checking both order id is same or not")
            print("razorpay order:",response['razorpay_order_id'])
            print("temp data id:",data.order_id)
    # checking for coupon code

            if data.coupon_code:
                code = data.coupon_code
                coupon=Coupon.objects.get(coupon_code=code)
                AppliedCoupon.objects.create(user=data.user,coupon=coupon)
                coupon.count-=1
                coupon.save()
                print("coupon count updated")

            order=Order.objects.create(order_id=data.order_id,user=data.user,delivery_instructions=data.instructions,total_price=data.total_price,payment_method=data.payment_method,payment_status=True)
            order.razorpay_payment_id=response['razorpay_payment_id']
            order.save()

            address=UserAddress.objects.get(id=data.address_id)
            order_address = OrderAddress.objects.create(city=address.city,state=address.state,landmark=address.landmark,pin=address.pin,address_line=address.address_line,order=order)


            cart_items=Cart.objects.filter(user=data.user)

            actual_price=50 #Adding delivery charge
            for item in cart_items:
                single_price=item.product.price
                actual_price+=(single_price*item.quantity)

                # updating stock
                variant=item.product
                variant.stock-=item.quantity
                variant.save()
                print("stock updatedd:::")

                OrderItem.objects.create(order=order,product=item.product,quantity=item.quantity,price=item.price)
            
            order.actual_price=actual_price 
            order.payment_status=status
            order.save()
            print("actual_order price",actual_price)

            cart_items.delete()


            discount=Decimal(order.actual_price)-Decimal(order.total_price)



            
            

            return render(request, 'user/success.html', {'status': True,'discount':discount,'order_id':order.id})


    except Exception as e:
        print("EXEPTION")
        print(e)
        return render(request, 'user/success.html', {'status': False})

    
@csrf_exempt
def continue_payment_status(request):

    response=request.POST
    print("******************",response)
    dic={
    'razorpay_order_id': response['razorpay_order_id'],
    'razorpay_payment_id': response['razorpay_payment_id'],
    'razorpay_signature': response['razorpay_signature'],
    }
    client = razorpay.Client(auth=("rzp_test_b714EP5tPrXbn2", "I5DOPeyeM27wIDIO37uP0foG"))



    try:

        status=client.utility.verify_payment_signature(dic)
        print("status:",status)

        if status:

            order=Order.objects.get(order_id=response['razorpay_order_id'])
            print("checking both order id is same or not")
            print("razorpay order:",response['razorpay_order_id'])
   

            order.payment_status=status
            order.save()



            discount=Decimal(order.actual_price)-Decimal(order.total_price)



            
            

            return render(request, 'user/success.html', {'status': True,'discount':discount,'order_id':order.id})


    except Exception as e:
        print("EXEPTION")
        print(e)
        return render(request, 'user/success.html', {'status': False})



def apply_coupon(request):
    if request.method== 'POST':
        coupon_code=request.POST['coupon_code']

        c=Coupon.objects.filter(coupon_code=coupon_code)

        if not c.exists():
            return JsonResponse({'message': 'Not a valid coupon code!'})
        
        coupon=c.first()


# checking for expiry date and count
        if coupon.expiry_date < datetime.now().date() or coupon.count<=0:
            return JsonResponse({'message': 'Coupon Expired!'})
# checking for minimum order
        
        product_total=float(request.POST['product_total'])
        
        if coupon.min_order > product_total:
            return JsonResponse({'message': f'Minimum Purchase for ₹{coupon.min_order}'})

        
        user=request.user

# checking for is the user already used this coupon
        if AppliedCoupon.objects.filter(user=user,coupon=coupon).exists():
            return JsonResponse({'message': 'You are already used this coupon'})




        discount = float(product_total) * (float(coupon.discount_percentage) / 100)
        print("Discount Percentage:", coupon.discount_percentage)
        print("Total:", product_total)
        print("Discount:", discount)

        request.session['coupon_code']=coupon_code



        total=product_total-discount+50

        return JsonResponse({'message': f'Coupon applied,  Discount - {coupon.discount_percentage}%','discount':discount,'total':total})




        