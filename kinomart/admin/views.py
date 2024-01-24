from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'index_admin.html')

def login(request):
    if request.method=='post':
        pass
    else:
        return render(request,'admin_login.html')