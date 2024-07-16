from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class AddDonationView(View):
    def get(self, request):
        return render(request, 'form.html')
