from django.shortcuts import redirect, render


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'landing/index.html')


def pricing_page(request):
    return render(request, 'landing/pricing.html')
