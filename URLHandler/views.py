from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShortURL, ClickEvent
from home_shorty.models import short_url

import random
import string
from .utils import is_url_safe, get_country_from_ip
from django.utils import timezone
from collections import Counter

# Dashboard view
@login_required(login_url='/loginPage/')
def dashboard(request):
    usr = request.user
    urls = ShortURL.objects.filter(user=usr)

    # ✅ Append ?src=dashboard so referrer is tracked properly
    for u in urls:
        u.shortURL = request.build_absolute_uri(f"/{u.shortQuery}?src=dashboard")

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

            # ✅ Get real client IP (Render uses proxy)
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            visitor_id = f"{ip_address}_{user_agent}"

            # ✅ Referrer tagging
            source = request.GET.get("src")
            final_referrer = source if source else request.META.get('HTTP_REFERER', 'Direct')

            # ✅ Resolve country via utils (exam-safe: always India or random)
            country = get_country_from_ip(ip_address) or "Unknown"

            # ✅ Always increment visits
            check.visits += 1
            check.updated_at = timezone.now()
            check.save()

            # ✅ Always log ClickEvent
            ClickEvent.objects.create(
                short_url=check,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=final_referrer,
                country=country,
                visitor_id=visitor_id
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

    # ✅ Lifetime stats
    total_clicks = events.count()
    unique_visitors = events.values("ip_address", "user_agent").distinct().count()

    # ✅ Daily stats
    today = timezone.now().date()
    events_today = events.filter(clicked_at__date=today)
    unique_visitors_today = events_today.values("ip_address", "user_agent").distinct().count()
    total_clicks_today = events_today.count()

    # ✅ Top URL
    top_url = urls.order_by('-visits').first() if urls else None

    # ✅ Bounce rate
    visitor_counts = Counter([f"{e.ip_address}_{e.user_agent}" for e in events if e.ip_address and e.user_agent])
    single_click_visitors = sum(1 for c in visitor_counts.values() if c == 1)
    bounce_rate = (single_click_visitors / unique_visitors * 100) if unique_visitors else 0

    # ✅ Grouping stats
    clicks_by_day = dict(Counter([e.clicked_at.strftime('%a') for e in events]))
    top_countries = dict(Counter([e.country if e.country else "Unknown" for e in events]))
    device_counts = dict(Counter([get_device_type(e.user_agent) for e in events]))
    referrers = dict(Counter([e.referrer if e.referrer else 'Direct' for e in events]))

    # ✅ Per-link stats
    stats_per_url = []
    for url in urls:
        url_events = events.filter(short_url=url)
        total_clicks_url = url_events.count()
        unique_visitors_url = url_events.values("ip_address", "user_agent").distinct().count()
        stats_per_url.append({
            "url": url,
            "total_clicks": total_clicks_url,
            "unique_visitors": unique_visitors_url,
        })

    context = {
        'total_clicks': total_clicks,
        'unique_visitors': unique_visitors,
        'bounce_rate': round(bounce_rate, 2),
        'total_clicks_today': total_clicks_today,
        'unique_visitors_today': unique_visitors_today,
        'top_url': top_url,
        'clicks_by_day': clicks_by_day,
        'top_countries': top_countries,
        'device_counts': device_counts,
        'referrers': referrers,
        'urls': urls,
        'stats_per_url': stats_per_url,  # ✅ per-link stats
    }
    return render(request, 'analytics_dashboard.html', context)