import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseBadRequest
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
        number_of_bags = Donation.objects.aggregate(total_bags=models.Sum('quantity'))['total_bags'] or 0
        number_of_institutions = Donation.objects.values('institution').distinct().count()

        foundations = Institution.objects.filter(type=Institution.FOUNDATION)
        paginator_foundations = Paginator(foundations, 5)
        page_number_foundations = request.GET.get('page_foundations')
        page_object_foundations = paginator_foundations.get_page(page_number_foundations)

        local_collections = Institution.objects.filter(type=Institution.LOCAL_COLLECTION)
        paginator_local_collections = Paginator(local_collections, 5)
        page_number_local_collections = request.GET.get('page_local_collections')
        page_object_local_collections = paginator_local_collections.get_page(page_number_local_collections)

        ngos = Institution.objects.filter(type=Institution.NGO)
        paginator_ngos = Paginator(ngos, 5)
        page_number_ngos = request.GET.get('page_ngos')
        page_object_ngos = paginator_ngos.get_page(page_number_ngos)

        context = {
            'number_of_bags': number_of_bags,
            'number_of_institutions': number_of_institutions,
            'foundations': page_object_foundations,
            'local_collections': page_object_local_collections,
            'ngos': page_object_ngos,
        }

        return render(request, 'index.html', context)


class AddDonationView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        categories = Category.objects.all()
        organizations = Institution.objects.all()
        for organization in organizations:
            category_ids = list(organization.categories.values_list('id', flat=True))
            organization.category_ids_json = json.dumps(category_ids)
        context = {
            'categories': categories,
            'organizations': organizations,
        }
        if request.user.is_authenticated:
            return render(request, 'form.html', context)
        else:
            return redirect('login')

    def post(self, request):
        bags = request.POST.get('bags')
        categories_ids = request.POST.getlist('categories')
        organization_id = request.POST.get('organization')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        more_info = request.POST.get('more_info')

        if not (
                bags and categories_ids and organization_id and address and city and postcode and phone and date and time):
            return HttpResponseBadRequest('Missing required data')

        try:
            organization = Institution.objects.get(pk=organization_id)
        except Institution.DoesNotExist:
            return HttpResponseBadRequest('Organization not found')

        try:
            donation = Donation.objects.create(
                quantity=bags,
                institution=organization,
                address=address,
                phone_number=phone,
                city=city,
                zip_code=postcode,
                pick_up_date=date,
                pick_up_time=time,
                pick_up_comment=more_info,
                user=request.user,
            )
            donation.categories.add(*categories_ids)
            return redirect('form-confirmation')

        except Exception as e:
            return render(request, 'form.html', {'error_message': str(e)})


class FormConfirmationView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'form-confirmation.html')


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
