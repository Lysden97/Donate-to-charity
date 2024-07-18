from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
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


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(request, 'profile.html', {'user': user})


class UserSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        return render(request, 'user_settings.html', context)

    def post(self, request):
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        if user.check_password(password):
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, 'Twoje dane zostały zaktualizowane.')
        else:
            messages.error(request, 'Podano nieprawidłowe hasło')

        context = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        return render(request, 'user_settings.html', context)


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'change_password.html')

    def post(self, request):
        user = request.user
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not user.check_password(old_password):
            messages.error(request, 'Wpisane obecne hasło jest niepoprawne.')
        elif new_password1 != new_password2:
            messages.error(request, 'Nowe hasła nie są takie same.')
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Twoje hasło zostało zmienione.')
        return render(request, 'change_password.html')