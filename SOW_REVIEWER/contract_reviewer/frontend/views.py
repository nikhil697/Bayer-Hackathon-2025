from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def upload(request):
    return render(request, 'upload.html')

def compare(request):
    return render(request, 'compare.html')

def dashboard(request):
    return render(request, 'dashboard.html')
