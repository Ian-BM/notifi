from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.decorators import school_required
from apps.contacts.models import Contact, ContactGroup

from . import beem
from .models import Message, MessageTemplate, Transaction


@school_required
def send_sms(request):
    school = request.user.school
    groups = ContactGroup.objects.filter(school=school)
    templates = MessageTemplate.objects.filter(is_global=True) | MessageTemplate.objects.filter(school=school)

    return render(request, 'messaging/send_sms.html', {
        'groups': groups,
        'templates': templates.distinct(),
        'school': school,
        'sender_id': school.get_sender_id(),
    })


@school_required
@require_POST
def send_sms_submit(request):
    school = request.user.school
    group_id = request.POST.get('group', '')
    content = request.POST.get('message', '').strip()

    if not content:
        messages.error(request, 'Message content cannot be empty.')
        return redirect('messaging:send_sms')

    if group_id == 'all':
        contacts = Contact.objects.filter(school=school)
        group = None
        group_name = 'All Contacts'
    else:
        group = get_object_or_404(ContactGroup, pk=group_id, school=school)
        contacts = Contact.objects.filter(school=school, group=group)
        group_name = group.name

    recipient_count = contacts.count()
    if recipient_count == 0:
        messages.error(request, 'The selected group has no contacts.')
        return redirect('messaging:send_sms')

    sms_count = beem.calculate_sms_count(content)
    credits_needed = sms_count * recipient_count

    if school.sms_balance < credits_needed:
        messages.error(
            request,
            f'Insufficient balance. This message needs {credits_needed} credits, '
            f'but you only have {school.sms_balance}.'
        )
        return redirect('messaging:send_sms')

    sender_id = school.get_sender_id()
    recipients = [
        {'recipient_id': str(c.id), 'dest_addr': c.phone}
        for c in contacts
    ]

    result = beem.send_bulk_sms(sender_id, content, recipients)

    balance_before = school.sms_balance
    message_obj = Message.objects.create(
        school=school,
        content=content,
        sender_id_used=sender_id,
        group=group,
        group_name_snapshot=group_name,
        recipient_count=recipient_count,
        delivered_count=recipient_count if result.get('success') else 0,
        failed_count=0 if result.get('success') else recipient_count,
        credits_used=credits_needed,
        status='sent' if result.get('success') else 'failed',
        beem_request_id=result.get('request_id', ''),
    )

    if result.get('success'):
        school.sms_balance = balance_before - credits_needed
        school.save(update_fields=['sms_balance'])

        Transaction.objects.create(
            school=school,
            type='sms_sent',
            amount=-credits_needed,
            balance_before=balance_before,
            balance_after=school.sms_balance,
            description=f'SMS sent to {group_name} ({recipient_count} recipients)',
            reference=message_obj.beem_request_id,
        )
        return render(request, 'messaging/send_success.html', {
            'message_obj': message_obj,
            'school': school,
        })

    messages.error(
        request,
        f"Failed to send message: {result.get('error') or result.get('data')}"
    )
    return redirect('messaging:send_sms')


@school_required
def templates_list(request):
    school = request.user.school
    templates = MessageTemplate.objects.filter(is_global=True) | MessageTemplate.objects.filter(school=school)
    return render(request, 'messaging/templates_list.html', {
        'templates': templates.distinct(),
    })


@school_required
@require_POST
def template_add(request):
    school = request.user.school
    name = request.POST.get('name', '').strip()
    content = request.POST.get('content', '').strip()

    if not name or not content:
        messages.error(request, 'Template name and content are required.')
    else:
        MessageTemplate.objects.create(school=school, name=name, content=content, is_global=False)
        messages.success(request, f'Template "{name}" created.')

    return redirect('messaging:templates_list')


@school_required
@require_POST
def template_delete(request, pk):
    template = get_object_or_404(MessageTemplate, pk=pk, school=request.user.school, is_global=False)
    template.delete()
    messages.success(request, 'Template deleted.')
    return redirect('messaging:templates_list')


@school_required
def reports(request):
    school = request.user.school
    message_list = Message.objects.filter(school=school)
    return render(request, 'messaging/reports.html', {
        'message_list': message_list,
    })


@csrf_exempt
def sms_callback(request):
    """Beem delivery report webhook."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    request_id = request.POST.get('request_id') or request.GET.get('request_id')
    dest_addr = request.POST.get('dest_addr') or request.GET.get('dest_addr')
    status = (request.POST.get('status') or request.GET.get('status') or '').upper()

    if request_id:
        message_obj = Message.objects.filter(beem_request_id=request_id).first()
        if message_obj:
            if status == 'DELIVRD':
                message_obj.delivered_count = min(
                    message_obj.delivered_count + 1, message_obj.recipient_count
                )
            else:
                message_obj.failed_count = min(
                    message_obj.failed_count + 1, message_obj.recipient_count
                )
            if message_obj.delivered_count + message_obj.failed_count >= message_obj.recipient_count:
                message_obj.status = 'sent' if message_obj.failed_count == 0 else 'partial'
            message_obj.save(update_fields=['delivered_count', 'failed_count', 'status'])

    return JsonResponse({'received': True})
