from django.shortcuts import render, redirect
from django.contrib import messages
import random
import string

from .models import short_url
from URLHandler.models import ShortURL, ClickEvent   # ✅ import both models

# Home shortener view
def home_shortener(request, short=None):
    if not short:
        return render(request, 'form.html')
    else:
        try:
            url = short_url.objects.get(short_Query=short)

            # ✅ Log click into ClickEvent for analytics
            try:
                main_url = ShortURL.objects.get(shortQuery=short)
                ClickEvent.objects.create(
                    short_url=main_url,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    referrer=request.META.get('HTTP_REFERER', '')
                )
                main_url.visits += 1
                main_url.save()
            except ShortURL.DoesNotExist:
                pass

            return render(request, "form.html", {"url": url})
        except short_url.DoesNotExist:
            return render(request, "form.html", {"error": "Not found"})


# Random short code generator
def randomGenerator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


# Short generate view
def short_generate(request):
    if request.method == 'POST':
        original = request.POST.get('original')
        short = request.POST.get('short')

        if original and short:
            check1 = short_url.objects.filter(short_Query=short)
            check2 = ShortURL.objects.filter(shortQuery=short)
            if not check1.exists() and not check2.exists():
                newURL = short_url(original_URL=original, short_Query=short)
                newURL.save()

                # ✅ also create entry in main ShortURL for analytics
                ShortURL.objects.create(
                    user=request.user,
                    originalURL=original,
                    shortQuery=short
                )

                return home_shortener(request, short)
            else:
                messages.error(request, 'Already Exists.')
                return redirect(home_shortener)

        elif original:
            generated = False
            while not generated:
                short = randomGenerator()
                check1 = short_url.objects.filter(short_Query=short)
                check2 = ShortURL.objects.filter(shortQuery=short)
                if not check1.exists() and not check2.exists():
                    newURL = short_url(original_URL=original, short_Query=short)
                    newURL.save()

                    # ✅ also create entry in main ShortURL
                    ShortURL.objects.create(
                        user=request.user,
                        originalURL=original,
                        shortQuery=short
                    )

                    return home_shortener(request, short)

        else:
            messages.error(request, 'Empty Fields.')
            return redirect('/')
    else:
        return redirect('/')