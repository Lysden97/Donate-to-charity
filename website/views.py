from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View

from website.models import Donation, Institution, Category


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if not first_name or not last_name or not email or not password or not confirm_password:
            return render(request, 'register.html', {'error': 'Wszystkie pola są wymagane'})
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Hasła nie są takie same'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Użytkownik już istnieje'})
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'index')
            return redirect(redirect_url)
        else:
            return redirect('register')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')


class IndexView(View):
    def get(self, request):
        all_donations = Donation.objects.all()
        all_bags = sum(donation.quantity for donation in all_donations)
        supported_organizations = Institution.objects.count()
        institutions = Institution.objects.all()

        context = {
            'all_bags': all_bags,
            'supported_organizations': supported_organizations,
            'institutions': institutions
        }
        return render(request, 'index.html', context)


class AddDonationView(View):
    def get(self, request):
        categories = Category.objects.all()
        institutions = Institution.objects.all()
        context = {
            'categories': categories,
            'institutions': institutions,
        }
        if request.user.is_authenticated:
            return render(request, 'form.html', context)
        else:
            return redirect('login')
