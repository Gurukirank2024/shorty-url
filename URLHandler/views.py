from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShortURL, ClickEvent
from home_shorty.models import short_url

import random
import string
from .utils import is_url_safe, get_country_from_ip   # ✅ helper
from django.utils import timezone
from datetime import timedelta
from collections import Counter

# Dashboard view
@login_required(login_url='/loginPage/')
def dashboard(request):
    usr = request.user
    urls = ShortURL.objects.filter(user=usr)

    for u in urls:
        u.shortURL = request.build_absolute_uri(f"/{u.shortQuery}")

    return render(request, 'dashboard.html', {'urls': urls})

def randomGenerator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

@login_required(login_url='/loginPage/')
def generate(request):
    if request.method == 'POST':
        usr = request.user
        original = request.POST.get('original')
        short = request.POST.get('short')

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
            while True:
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

def home(request, query=None):
    if not query:
        return render(request, 'home.html')
    else:
        try:
            check = ShortURL.objects.get(shortQuery=query)

            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
            if ',' in ip:
                ip = ip.split(',')[0].strip()

            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            referrer = request.META.get('HTTP_REFERER', 'Direct')

            # ✅ Capture src parameter if present
            source = request.GET.get("src", None)
            final_referrer = source if source else referrer

            country = get_country_from_ip(ip)

            # ✅ Always count every request as a visit (no time-based deduplication here)
            check.visits += 1
            check.updated_at = timezone.now()
            check.save()

            ClickEvent.objects.create(
                short_url=check,
                ip_address=ip,
                user_agent=user_agent,
                referrer=final_referrer,
                country=country
            )

            return redirect(check.originalURL)
        except ShortURL.DoesNotExist:
            try:
                check = short_url.objects.get(short_Query=query)
                return redirect(check.original_URL)
            except short_url.DoesNotExist:
                return render(request, 'home.html', {'error': 'Error'})
        except Exception:
            return render(request, 'home.html', {'error': 'Error'})

@login_required(login_url='/loginPage/')
def deleteurl(request):
    if request.method == "POST":
        short = request.POST.get('delete')
        ShortURL.objects.filter(shortQuery=short).delete()
        return redirect(dashboard)
    else:
        return redirect(home)

# ✅ Improved device detection
def get_device_type(user_agent):
    ua = (user_agent or "").lower()
    if "mobile" in ua and "tablet" not in ua:
        return "Mobile"
    elif "tablet" in ua or "ipad" in ua:
        return "Tablet"
    else:
        return "Desktop"

@login_required(login_url='/loginPage/')
def analytics_dashboard(request):
    usr = request.user
    urls = ShortURL.objects.filter(user=usr)
    events = ClickEvent.objects.filter(short_url__in=urls)

    # Raw total clicks (every request logged)
    total_clicks = len(events)

    # ✅ Unique visitors: deduplicate by IP + user agent
    visitor_pairs = [(e.ip_address, e.user_agent) for e in events]
    unique_visitors = len(set(visitor_pairs)) if events else 0

    top_url = urls.order_by('-visits').first() if urls else None

    # ✅ Bounce rate: based on unique visitors
    visitor_counts = Counter(visitor_pairs) if events else {}
    single_click_visitors = sum(1 for c in visitor_counts.values() if c == 1)
    bounce_rate = (single_click_visitors / unique_visitors * 100) if unique_visitors else 0

    clicks_by_day = dict(Counter([e.clicked_at.strftime('%a') for e in events])) if events else {}
    top_countries = dict(Counter([e.country if e.country else 'Unknown' for e in events])) if events else {}

    # ✅ More accurate device classification
    device_counts = dict(Counter([
        get_device_type(e.user_agent)
        for e in events
    ])) if events else {}

    referrers = dict(Counter([e.referrer if e.referrer else 'Direct' for e in events])) if events else {}

    context = {
        'total_clicks': total_clicks,          # raw clicks
        'unique_visitors': unique_visitors,    # deduplicated visitors
        'top_url': top_url,
        'bounce_rate': round(bounce_rate, 2),  # based on unique visitors
        'clicks_by_day': clicks_by_day,
        'top_countries': top_countries,
        'device_counts': device_counts,
        'referrers': referrers,
        'urls': urls,
    }
    return render(request, 'analytics_dashboard.html', context)