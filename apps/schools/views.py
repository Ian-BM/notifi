import secrets

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from apps.accounts.decorators import admin_required
from apps.messaging.models import Transaction

from .forms import SchoolForm, SchoolUserForm
from .models import School

User = get_user_model()


@admin_required
def schools_list(request):
    query = request.GET.get('q', '').strip()
    schools = School.objects.all()
    if query:
        schools = schools.filter(
            Q(name__icontains=query) | Q(contact_person__icontains=query)
        )
    return render(request, 'admin_panel/schools_list.html', {
        'schools': schools,
        'query': query,
    })


@admin_required
def school_add(request):
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        user_form = SchoolUserForm(request.POST)
        if form.is_valid() and user_form.is_valid():
            school = form.save()

            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password'] or secrets.token_urlsafe(8)
            User.objects.create_user(
                username=username,
                password=password,
                email=school.email,
                role='school',
                school=school,
            )
            messages.success(
                request,
                f'School "{school.name}" created. Login username: {username}'
                + ('' if user_form.cleaned_data['password'] else f' / password: {password}')
            )
            return redirect('schools:schools_list')
    else:
        form = SchoolForm()
        user_form = SchoolUserForm()

    return render(request, 'admin_panel/school_form.html', {
        'form': form,
        'user_form': user_form,
        'is_edit': False,
    })


@admin_required
def school_edit(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, f'School "{school.name}" updated.')
            return redirect('schools:schools_list')
    else:
        form = SchoolForm(instance=school)

    return render(request, 'admin_panel/school_form.html', {
        'form': form,
        'school': school,
        'is_edit': True,
    })


@admin_required
def school_topup(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == 'POST':
        try:
            credits = int(request.POST.get('credits', 0))
        except ValueError:
            credits = 0
        reference = request.POST.get('reference', '').strip()

        if credits <= 0:
            messages.error(request, 'Enter a valid number of credits.')
            return redirect('schools:school_topup', pk=school.pk)

        balance_before = school.sms_balance
        school.sms_balance = balance_before + credits
        school.save(update_fields=['sms_balance'])

        Transaction.objects.create(
            school=school,
            type='credit_added',
            amount=credits,
            balance_before=balance_before,
            balance_after=school.sms_balance,
            description=f'Top up of {credits} credits',
            reference=reference,
        )
        messages.success(request, f'Added {credits} credits to {school.name}.')
        return redirect('schools:schools_list')

    return render(request, 'admin_panel/topup.html', {'school': school})


@admin_required
def transactions_list(request):
    transactions = Transaction.objects.select_related('school').all()
    return render(request, 'admin_panel/transactions.html', {
        'transactions': transactions,
    })
