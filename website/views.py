from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from website.models import Donation, Institution


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class IndexView(View):
    def get(self, request):
        all_donations = Donation.objects.all()
        all_bags = sum(donation.quantity for donation in all_donations)
        supported_organizations = Institution.objects.count()

        context = {
            'all_bags': all_bags,
            'supported_organizations': supported_organizations,
        }
        return render(request, 'index.html', context)


class AddDonationView(View):
    def get(self, request):
        return render(request, 'form.html')
