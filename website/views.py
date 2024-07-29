import json
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views import View
from website.models import Donation, Institution, Category


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
    login_url = '/website/login/'

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
            return HttpResponseBadRequest('Brak wymaganych danych')

        try:
            organization = Institution.objects.get(pk=organization_id)
        except Institution.DoesNotExist:
            return HttpResponseBadRequest('Nie znaleziono organizacji')

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
            return redirect('add_donation_confirmation')

        except Exception as e:
            return render(request, 'form.html', {'error_message': str(e)})


class FormConfirmationView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'form-confirmation.html')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        donations = Donation.objects.filter(user=request.user)
        context = {
            'donations': donations,
        }
        return render(request, 'profile.html', context)

    def post(self, request):
        donations = Donation.objects.filter(user=request.user)
        for donation in donations:
            is_taken_field = f'is_taken_{donation.id}'
            if is_taken_field in request.POST:
                donation.is_taken = True
            else:
                donation.is_taken = False
            donation.save()
        return redirect('user')


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
