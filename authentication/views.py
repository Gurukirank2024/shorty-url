from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser   # your custom user model



# Login view (using email instead of username)
def loginPage(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            login_email = request.POST.get('email')   # use email field
            login_password = request.POST.get('password')

            if login_email and login_password:
                # authenticate with email instead of username
                user = authenticate(email=login_email, password=login_password)
                if user is not None:
                    login(request, user)
                    return redirect('/')
                else:
                    return render(request, 'login.html', {'error': 'Email or Password is incorrect.'})
            else:
                return render(request, 'login.html', {'error': 'Empty Fields.'})
        else:
            return render(request, 'login.html')
    else:
        return redirect('/')



# Signup view
# Signup view
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match.'})

        if not username or not email or not password:
            return render(request, 'signup.html', {'error': 'Empty fields.'})

        # Check email uniqueness only
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered.'})

        # Create user
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        messages.success(request, "Signup Successful, Login Here.")
        return redirect('loginPage')

    return render(request, 'signup.html')



# Logout view (fixed to return HttpResponse)
def logout_view(request):
    logout(request)   # clears the session
    messages.success(request, "You have been logged out.")  # optional feedback
    return redirect('loginPage')   # redirect to login page after logout


# Password change view
@login_required(login_url='/loginPage/')
def passwordChange(request):
    if request.method == 'POST':
        current = request.POST.get('oldPassword')
        newpass = request.POST.get('newPassword')
        conpass = request.POST.get('confirmPassword')

        if newpass == conpass:
            user = CustomUser.objects.get(id=request.user.id)
            if user.check_password(current):
                user.set_password(newpass)
                user.save()
                messages.success(request, "Password Changed. Please log in again.")
                return redirect('loginPage')
            else:
                return render(request, 'passwordChange.html', {'error': 'Current password is incorrect.'})
        else:
            return render(request, 'passwordChange.html', {'error': 'New Password and Confirm password don\'t match.'})
    return render(request, 'passwordChange.html')
