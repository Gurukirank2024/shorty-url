from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import Counter
from .models import CustomUser, ShortURL, ClickEvent   # include your models

# -------------------------------
# Login view (using email instead of username)
# -------------------------------
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

# -------------------------------
# Signup view
# -------------------------------
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

# -------------------------------
# Logout view
# -------------------------------
def logout_view(request):
    logout(request)   # clears the session
    messages.success(request, "You have been logged out.")  # optional feedback
    return redirect('loginPage')   # redirect to login page after logout

# -------------------------------
# Password change view
# -------------------------------
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

# -------------------------------
# Analytics Dashboard view
# -------------------------------
@login_required
def analytics_dashboard(request):
    usr = request.user
    urls = ShortURL.objects.filter(user=usr)
    events = ClickEvent.objects.filter(short_url__in=urls)

    # Total clicks
    total_clicks = events.count()

    # Unique visitors (distinct IPs)
    unique_visitors = events.values('ip_address').distinct().count()

    # Top URL
    top_url = urls.order_by('-visits').first()

    # Bounce rate: % of visitors who clicked only once
    ip_counts = Counter(events.values_list('ip_address', flat=True))
    single_click_ips = sum(1 for c in ip_counts.values() if c == 1)
    bounce_rate = (single_click_ips / unique_visitors * 100) if unique_visitors else 0

    # Clicks grouped by day
    clicks_by_day = Counter(e.clicked_at.strftime('%a') for e in events)

    # Top countries (if you log country in ClickEvent)
    top_countries = Counter(e.country for e in events if e.country)

    # Device breakdown
    device_counts = Counter(['Mobile' if 'Mobile' in e.user_agent else 'Desktop' for e in events])

    # Top referrers
    referrers = Counter(e.referrer for e in events if e.referrer)

    context = {
        'total_clicks': total_clicks,
        'unique_visitors': unique_visitors,
        'top_url': top_url,
        'bounce_rate': round(bounce_rate, 2),
        'clicks_by_day': clicks_by_day,
        'top_countries': top_countries,
        'device_counts': device_counts,
        'referrers': referrers,
        'urls': urls,
    }
    return render(request, 'analytics_dashboard.html', context)