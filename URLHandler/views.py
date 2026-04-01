from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShortURL   # main model
from home_shorty.models import short_url   # secondary model if needed

import random
import string
from .utils import is_url_safe   # ✅ import the VirusTotal helper
from django.utils import timezone
from datetime import timedelta


# Dashboard view
@login_required(login_url='/loginPage/')
def dashboard(request):
    usr = request.user
    urls = ShortURL.objects.filter(user=usr)

    # Attach full short URL dynamically for each object
    for u in urls:
        u.shortURL = request.build_absolute_uri(f"/{u.shortQuery}")

    return render(request, 'dashboard.html', {'urls': urls})


# Random short code generator
def randomGenerator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


# Generate short URL
@login_required(login_url='/loginPage/')
def generate(request):
    if request.method == 'POST':
        usr = request.user
        original = request.POST.get('original')
        short = request.POST.get('short')

        # ✅ Safety check before saving
        if original and not is_url_safe(original):
            messages.error(request, 'Unsafe URL detected. Cannot shorten.')
            return redirect(dashboard)

        if original and short:
            check = ShortURL.objects.filter(shortQuery=short)
            if not check.exists():
                newURL = ShortURL(user=usr, originalURL=original, shortQuery=short)
                newURL.save()
                return redirect(dashboard)
            else:
                messages.error(request, 'Already Exists.')
                return redirect(dashboard)

        elif original:
            generated = False
            while not generated:
                short = randomGenerator()
                check = ShortURL.objects.filter(shortQuery=short)
                if not check.exists():
                    newURL = ShortURL(user=usr, originalURL=original, shortQuery=short)
                    newURL.save()
                    return redirect(dashboard)

        else:
            messages.error(request, 'Empty Fields.')
            return redirect(dashboard)
    else:
        return redirect('/dashboard')


# Home redirect view
def home(request, query=None):
    if not query:
        return render(request, 'home.html')
    else:
        try:
            check = ShortURL.objects.get(shortQuery=query)

            # ✅ Only increment if last visit was > 10 seconds ago
            if not check.updated_at or timezone.now() - check.updated_at > timedelta(seconds=10):
                check.visits += 1
                check.updated_at = timezone.now()
                check.save()

            return redirect(check.originalURL)
        except ShortURL.DoesNotExist:
            try:
                check = short_url.objects.get(short_Query=query)
                return redirect(check.original_URL)
            except short_url.DoesNotExist:
                return render(request, 'home.html', {'error': 'Error'})
        except Exception:
            return render(request, 'home.html', {'error': 'Error'})


# Delete short URL
@login_required(login_url='/loginPage/')
def deleteurl(request):
    if request.method == "POST":
        short = request.POST.get('delete')
        try:
            check = ShortURL.objects.filter(shortQuery=short)
            check.delete()
            return redirect(dashboard)
        except ShortURL.DoesNotExist:
            return redirect(home)
    else:
        return redirect(home)