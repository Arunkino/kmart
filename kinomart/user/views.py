from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import User,UserAddress
from products.models import Category,ProductImages,Products
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model,authenticate,login,logout
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

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


    return render(request,'user/order_history.html')


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

        user = User.objects.get(email=request.session['user_email'])

        # Validate old password
        if not user.check_password(old_password):
            return JsonResponse({'message': 'You have entered a wrong old password!!!'})

        # Check if new passwords match
        if new_password1 != new_password2:
            return JsonResponse({'message': 'New passwords not matching!'})

        # Edit user password
        user.set_password(new_password1)
        user.save()

        return JsonResponse({'message': 'Password changed successfully!'})
    