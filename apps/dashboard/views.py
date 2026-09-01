from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.accounts.models import OnboardingProgress
from apps.contacts.models import Contact
from apps.messaging.models import Message, Transaction
from apps.schools.models import School


@login_required
def index(request):
    if request.user.is_platform_admin():
        return redirect('dashboard:admin_dashboard')
    return redirect('dashboard:school_dashboard')


@login_required
def school_dashboard(request):
    if not request.user.is_school_admin() or request.user.school_id is None:
        return redirect('dashboard:admin_dashboard')

    school = request.user.school
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    messages_this_month = Message.objects.filter(
        school=school, sent_at__gte=month_start
    ).count()
    contacts_total = Contact.objects.filter(school=school).count()
    recent_messages = Message.objects.filter(school=school)[:10]

    onboarding, _ = OnboardingProgress.objects.get_or_create(user=request.user)

    if contacts_total > 0:
        onboarding.step_contacts_done = True
    if Message.objects.filter(school=school).exists():
        onboarding.step_sms_done = True
    if onboarding.step_contacts_done and onboarding.step_sms_done:
        onboarding.step_welcome_done = True

    just_completed = False
    if onboarding.all_done() and not onboarding.completed:
        onboarding.completed = True
        onboarding.completed_at = timezone.now()
        just_completed = True

    onboarding.save()

    show_welcome_modal = not request.session.get('welcome_modal_shown') and not onboarding.completed
    if show_welcome_modal:
        request.session['welcome_modal_shown'] = True

    return render(request, 'dashboard/school_dashboard.html', {
        'school': school,
        'messages_this_month': messages_this_month,
        'contacts_total': contacts_total,
        'recent_messages': recent_messages,
        'low_balance': school.sms_balance < 50,
        'onboarding': onboarding,
        'show_onboarding': not onboarding.completed,
        'just_completed_onboarding': just_completed,
        'show_welcome_modal': show_welcome_modal,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_platform_admin():
        return redirect('dashboard:school_dashboard')

    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_schools = School.objects.count()
    active_schools = School.objects.filter(is_active=True).count()
    total_sms_this_month = Message.objects.filter(sent_at__gte=month_start).count()
    total_credits_sold = sum(
        t.amount for t in Transaction.objects.filter(type='credit_added')
    )

    schools = School.objects.all()[:10]
    recent_transactions = Transaction.objects.select_related('school').all()[:10]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_schools': total_schools,
        'active_schools': active_schools,
        'total_sms_this_month': total_sms_this_month,
        'total_credits_sold': total_credits_sold,
        'schools': schools,
        'recent_transactions': recent_transactions,
    })
