import csv
import io

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.decorators import school_required

from .models import Contact, ContactGroup
from .utils import normalize_phone


@school_required
def contacts_list(request):
    school = request.user.school
    query = request.GET.get('q', '').strip()
    group_id = request.GET.get('group', '')

    contacts = Contact.objects.filter(school=school).select_related('group')
    if query:
        contacts = contacts.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    if group_id:
        contacts = contacts.filter(group_id=group_id)

    groups = ContactGroup.objects.filter(school=school)

    return render(request, 'contacts/list.html', {
        'contacts': contacts.order_by('-created_at'),
        'groups': groups,
        'query': query,
        'active_group': group_id,
    })


@school_required
@require_POST
def contact_add(request):
    school = request.user.school
    name = request.POST.get('name', '').strip()
    raw_phone = request.POST.get('phone', '').strip()
    group_id = request.POST.get('group') or None

    if not name or not raw_phone:
        return JsonResponse({'success': False, 'error': 'Name and phone are required.'}, status=400)

    phone = normalize_phone(raw_phone)
    if not phone:
        return JsonResponse({'success': False, 'error': 'Invalid Tanzanian phone number.'}, status=400)

    if Contact.objects.filter(school=school, phone=phone).exists():
        return JsonResponse({'success': False, 'error': 'This phone number is already a contact.'}, status=400)

    group = None
    if group_id:
        group = ContactGroup.objects.filter(school=school, pk=group_id).first()

    contact = Contact.objects.create(school=school, name=name, phone=phone, group=group)

    return JsonResponse({
        'success': True,
        'contact': {
            'id': contact.id,
            'name': contact.name,
            'phone': contact.phone,
            'group': group.name if group else '',
            'created_at': contact.created_at.strftime('%d %b %Y'),
        }
    })


@school_required
@require_POST
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, school=request.user.school)
    contact.delete()
    return JsonResponse({'success': True})


@school_required
def contacts_import(request):
    school = request.user.school
    groups = ContactGroup.objects.filter(school=school)

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        name_col = request.POST.get('name_column', '').strip()
        phone_col = request.POST.get('phone_column', '').strip()
        group_id = request.POST.get('group') or None

        group = ContactGroup.objects.filter(school=school, pk=group_id).first() if group_id else None

        try:
            decoded = csv_file.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            messages.error(request, 'Could not read file. Please upload a valid CSV.')
            return redirect('contacts:contacts_import')

        reader = csv.DictReader(io.StringIO(decoded))
        imported, skipped, failed = 0, 0, 0

        for row in reader:
            raw_name = (row.get(name_col) or '').strip()
            raw_phone = (row.get(phone_col) or '').strip()

            phone = normalize_phone(raw_phone)
            if not raw_name or not phone:
                failed += 1
                continue

            _, created = Contact.objects.get_or_create(
                school=school, phone=phone,
                defaults={'name': raw_name, 'group': group},
            )
            if created:
                imported += 1
            else:
                skipped += 1

        messages.success(
            request,
            f'Import complete: {imported} imported, {skipped} skipped (duplicates), {failed} failed (invalid).'
        )
        return redirect('contacts:contacts_list')

    return render(request, 'contacts/import.html', {'groups': groups})


@school_required
def groups_list(request):
    school = request.user.school
    groups = ContactGroup.objects.filter(school=school)
    return render(request, 'contacts/groups.html', {'groups': groups})


@school_required
@require_POST
def group_add(request):
    school = request.user.school
    name = request.POST.get('name', '').strip()
    if not name:
        messages.error(request, 'Group name is required.')
        return redirect('contacts:groups_list')

    _, created = ContactGroup.objects.get_or_create(school=school, name=name)
    if created:
        messages.success(request, f'Group "{name}" created.')
    else:
        messages.warning(request, f'Group "{name}" already exists.')
    return redirect('contacts:groups_list')
