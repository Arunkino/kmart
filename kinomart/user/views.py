from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress,Cart,Order,OrderItem,OrderAddress
from products.models import Category,ProductImages,Products,ProductVarient
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

# Create your views here.


def index(request):
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
    
                product_data.append({
                    'product_id': product.id,
                    'variant_id':variant.id,
                    'product_name': product.product_name,
                    'description': product.description,
                    'price': variant.price,
                    'quantity':variant.quantity,
                    'unit':variant.unit, 
                    'brand': product.brand.brand_name,
                    'is_offer':product.is_offer,
                    'image': image,      
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

def signup(request):
    if request.method=='POST':

        User=get_user_model()


        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        phone=request.POST['mobile']
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

            
            # creating session when user registered succussfully with auto login
            
            request.session['user_email']=user.email
            return redirect('home')
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

    varients=product.varients.all()
    varient_data=[]
    for varient in varients:
        varient_data.append({
            'id':varient.id,
            'qty':varient.quantity,
            'unit':varient.unit,
            'price':varient.price,

        })
        
    


    return render(request,'user/view_product.html',{'product':product,'varient_data':varient_data})





# User profile page related

def user_page(request):


    if 'user_email' in request.session:
        return render(request,'user/user_profile.html')
    
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
        order_date=order.order_date
        total=order.total_price
        payment_method=order.payment_method
        status=order.status

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

            }
        )

            
    return render(request,'user/order_history.html',{'orders':orders_list,})

def cancel_order(request,id):
    order=Order.objects.get(id=id)
    order.return_status="Cancelled"
    order.save()

    return redirect('order_history')

def return_order(request,id):
    order=Order.objects.get(id=id)
    order.return_status='Returned'
    order.save()

    return redirect('order_history')


def wishlist(request):


    return render(request,'user/wishlist.html')


def wallet(request):


    return render(request,'user/wallet.html')






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
        price=item.price
        product_total+=price

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


                

        try:
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
            return JsonResponse({'message': 'Item removed from the cart!'})

        product_variant = cart_item.product

        # Update the quantity
        cart_item.quantity = new_quantity
        cart_item.price= new_quantity*product_variant.price
        cart_item.save()

        return JsonResponse({'message': 'Cart updated successfully!'})

    else:
        return JsonResponse({'error': 'Invalid request'})

        


def cart_count(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).count()
        return JsonResponse({'count': count})
    else:
        return JsonResponse({'count': 0})
    

def checkout(request):
    if request.method == 'POST':
        user=request.user
        payment_method=request.POST['payment']
        address_id=request.POST['address_id']
        instructions=request.POST.get('instructions')
        total_price=request.POST['total_price']

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

            for item in cart_items:
                OrderItem.objects.create(order=order,product=item.product,quantity=item.quantity,price=item.price)
            
            cart_items.delete()



        if payment_method=='cod':

            return render(request, 'user/success.html', {'status': True})

        return render(request, 'user/cart.html', {'show_checkout_modal': True,'order':order})
    
    return redirect ('cart')
    
    
    
@csrf_exempt
def payment_status(request):

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
        order=Order.objects.get(order_id=response['razorpay_order_id'])
        order.razorpay_payment_id=response['razorpay_payment_id']
        order.payment_status=True
        order.save()
        return render(request, 'user/success.html', {'status': True})


    except:
        return render(request, 'user/success.html', {'status': False})





        