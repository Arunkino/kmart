from django.shortcuts import render,redirect
from .models import Offer

# Create your views here.

def offer(request):

    offers=Offer.objects.all().order_by('-id')

    return render(request,'admin/offer.html',{'offers':offers})


def add_offer(request):

    if request.method == 'POST':
        
        offer_name=request.POST['offer_name']
        expiry_date=request.POST['expiry_date']
        discount=request.POST['discount_percentage']

        Offer.objects.create(offer_name=offer_name,expiry_date=expiry_date,discount=discount)


        return redirect('offer')


def edit_offer(request):
    if request.method=='POST':
        id=request.POST['coupon-id']

        offer=Offer.objects.get(id=id)


        offer.offer_name=request.POST['offer_name']
        offer.discount=request.POST['discount_percentage']
        offer.expiry_date=request.POST['expiry_date']
        

        offer.save()

        return redirect('offer')