from django.shortcuts import render, redirect
from .models import short_url
from URLHandler.models import ShortURL   # fixed import
import random
import string
from django.contrib import messages


def home_shortener(request, short=None):
    if not short:
        return render(request, 'form.html')
    else:
        try:
            url = short_url.objects.get(short_Query=short)
            return render(request, "form.html", {"url": url})
        except short_url.DoesNotExist:
            return render(request, "form.html", {"error": "Not found"})


def randomGenerator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


def short_generate(request):
    if request.method == 'POST':
        original = request.POST.get('original')
        short = request.POST.get('short')

        if original and short:
            check1 = short_url.objects.filter(short_Query=short)
            check2 = ShortURL.objects.filter(shortQuery=short)   # fixed reference
            if not check1.exists() and not check2.exists():
                newURL = short_url(original_URL=original, short_Query=short)
                newURL.save()
                return home_shortener(request, short)
            else:
                messages.error(request, 'Already Exists.')
                return redirect(home_shortener)

        elif original:
            generated = False
            while not generated:
                short = randomGenerator()
                check1 = short_url.objects.filter(short_Query=short)
                check2 = ShortURL.objects.filter(shortQuery=short)   # fixed reference
                if not check1.exists() and not check2.exists():
                    newURL = short_url(original_URL=original, short_Query=short)
                    newURL.save()
                    return home_shortener(request, short)

        else:
            messages.error(request, 'Empty Fields.')
            return redirect('/')
    else:
        return redirect('/')
