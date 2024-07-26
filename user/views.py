from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.contrib import messages

from user.tokens import account_activation_token

User = get_user_model()


def verify_email(request):
    if request.method == 'POST':
        if request.user.email_is_verified != True:
            current_site = get_current_site(request)
            user = request.user
            email = request.user.email
            subject = 'Potwierdź Email'
            message = render_to_string('user/verify_email_message.html', {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email = EmailMessage(
                subject, message, to=[email]
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('verify_email_done')
        else:
            return redirect('register')
    return render(request, 'user/verify_email.html')


def verify_email_done(request):
    return render(request, 'user/verify_email_done.html')


def verify_email_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        messages.success(request, 'Email został zweryfikowany')
        return redirect('verify_email_complete')
    else:
        messages.warning(request, 'Link jest nieprawidłowy')
    return render(request, 'user/verify_email_confirm.html')


def verify_email_complete(request):
    return render(request, 'user/verify_email_complete.html')


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
        user = User.objects.create_user(email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('verify_email')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'index')
            return redirect(redirect_url)
        else:
            if not User.objects.filter(email=email).exists():
                return redirect('register')
            error = 'Nieprawidłowa nazwa użytkownika lub hasło'
            return render(request, 'login.html', {'error': error})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')
