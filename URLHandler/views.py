from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShortURL, ClickEvent
from home_shorty.models import short_url

import random
import string
import uuid   # ✅ for visitor_id
from .utils import is_url_safe, get_country_from_ip
from django.utils import timezone
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

            # ✅ Assign visitor_id cookie
            visitor_id = request.COOKIES.get('visitor_id')
            if not visitor_id:
                visitor_id = str(uuid.uuid4())

            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            referrer = request.META.get('HTTP_REFERER', 'Direct')
            source = request.GET.get("src", None)
            final_referrer = source if source else referrer
            country = get_country_from_ip(request.META.get('REMOTE_ADDR'))

            # Always increment visits
            check.visits += 1
            check.updated_at = timezone.now()
            check.save()

            ClickEvent.objects.create(
                short_url=check,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=user_agent,
                referrer=final_referrer,
                country=country,
                visitor_id=visitor_id   # ✅ new field in model
            )

            response = redirect(check.originalURL)
            response.set_cookie('visitor_id', visitor_id, max_age=60*60*24*365)  # 1 year
            return response

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

    # ✅ Total clicks = number of events
    total_clicks = events.count()

    # ✅ Unique visitors: deduplicate only by visitor_id
    visitor_ids = {e.visitor_id for e in events if e.visitor_id}
    unique_visitors = len(visitor_ids)

    # ✅ Top URL by visits
    top_url = urls.order_by('-visits').first() if urls else None

    # ✅ Bounce rate: visitors who clicked only once across ALL URLs
    visitor_counts = Counter([e.visitor_id for e in events if e.visitor_id])
    single_click_visitors = sum(1 for c in visitor_counts.values() if c == 1)
    bounce_rate = (single_click_visitors / unique_visitors * 100) if unique_visitors else 0

    # ✅ Grouping stats
    clicks_by_day = dict(Counter([e.clicked_at.strftime('%a') for e in events]))
    top_countries = dict(Counter([e.country if e.country else 'Unknown' for e in events]))
    device_counts = dict(Counter([get_device_type(e.user_agent) for e in events]))
    referrers = dict(Counter([e.referrer if e.referrer else 'Direct' for e in events]))

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