import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.contacts.models import Contact, ContactGroup
from apps.messaging.models import MessageTemplate
from apps.schools.models import School

User = get_user_model()

TEMPLATES = [
    (
        "Ukumbusho wa Ada",
        "Mzazi mpendwa, ada ya muhula wa {muhula} ni TSh {kiasi}. "
        "Tafadhali lipa kabla ya tarehe {tarehe}. Asante - {shule}",
    ),
    (
        "Mkutano wa Wazazi",
        "Mkutano wa wazazi utafanyika tarehe {tarehe} saa {saa}. "
        "Tafadhali hudhuria. Asante - {shule}",
    ),
    (
        "Matokeo ya Mtihani",
        "Matokeo ya {mtoto} yameandaliwa. Tafadhali fika shuleni kuanzia {tarehe}. "
        "Asante - {shule}",
    ),
    (
        "Taarifa ya Dharura",
        "TAARIFA: {ujumbe}. Tafadhali angalia hali ya mtoto wako. Asante - {shule}",
    ),
    (
        "Ratiba ya Muhula",
        "Muhula wa {muhula} unaanza {tarehe}. Hakikisha mtoto ana sare na vitabu. "
        "Asante - {shule}",
    ),
]

DEMO_CONTACTS = {
    "Darasa la 1": [
        ("Juma Mwakasege", "255712345671"),
        ("Fatuma Rajabu", "255712345672"),
        ("Amina Hassan", "255712345673"),
        ("Zainabu Kilonzo", "255712345674"),
        ("Rashidi Kombo", "255712345675"),
        ("Halima Said", "255712345676"),
        ("Yusuph Mrisho", "255712345677"),
    ],
    "Darasa la 2": [
        ("Grace Mushi", "255713345671"),
        ("Peter Mkumbo", "255713345672"),
        ("Neema Shayo", "255713345673"),
        ("David Massawe", "255713345674"),
        ("Rehema Kimaro", "255713345675"),
        ("John Kilewo", "255713345676"),
        ("Esther Nnko", "255713345677"),
    ],
    "Walimu": [
        ("Mwalimu Salma", "255714345671"),
        ("Mwalimu Godfrey", "255714345672"),
        ("Mwalimu Consolata", "255714345673"),
        ("Mwalimu Ibrahim", "255714345674"),
        ("Mwalimu Rose", "255714345675"),
        ("Mwalimu Hassan", "255714345676"),
    ],
}


class Command(BaseCommand):
    help = "Seed the Notifi database with demo data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Notifi demo data...")

        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@notifi.co.tz",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_password = None
        if created:
            admin_password = secrets.token_urlsafe(12)
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user."))
        else:
            self.stdout.write("Admin user already exists, skipping.")

        stagnes, _ = School.objects.get_or_create(
            name="St. Agnes Primary School",
            defaults={
                "phone": "255712000001",
                "email": "info@stagnes.ac.tz",
                "contact_person": "Sister Agnes Mchome",
                "address": "Moshi, Kilimanjaro",
                "sms_balance": 500,
                "sender_id": "ST-AGNES",
                "sender_id_status": "approved",
            },
        )
        maryhill, _ = School.objects.get_or_create(
            name="Maryhill Secondary School",
            defaults={
                "phone": "255713000001",
                "email": "info@maryhill.ac.tz",
                "contact_person": "Mr. Elias Komba",
                "address": "Arusha",
                "sms_balance": 45,
                "sender_id": "MARYHILL",
                "sender_id_status": "pending",
            },
        )
        self.stdout.write(self.style.SUCCESS("Created demo schools."))

        school_user, created = User.objects.get_or_create(
            username="stagnes",
            defaults={
                "email": "user@stagnes.ac.tz",
                "role": "school",
                "school": stagnes,
            },
        )
        if created:
            school_user.set_password("demo2026")
            school_user.save()
            self.stdout.write(self.style.SUCCESS("Created stagnes school user."))
        else:
            self.stdout.write("School user already exists, skipping.")

        for name, content in TEMPLATES:
            MessageTemplate.objects.get_or_create(
                name=name, is_global=True, defaults={"content": content}
            )
        self.stdout.write(self.style.SUCCESS("Created global templates."))

        for group_name, contacts in DEMO_CONTACTS.items():
            group, _ = ContactGroup.objects.get_or_create(
                school=stagnes, name=group_name
            )
            for name, phone in contacts:
                Contact.objects.get_or_create(
                    school=stagnes, phone=phone,
                    defaults={"name": name, "group": group},
                )
        self.stdout.write(self.style.SUCCESS("Created demo contacts."))

        self.stdout.write(self.style.SUCCESS("\nSeeding complete!"))
        self.stdout.write("Login credentials:")
        if admin_password:
            self.stdout.write(f"  Admin:        admin / {admin_password}")
        else:
            self.stdout.write("  Admin:        admin (already existed — password unchanged)")
        self.stdout.write("  School demo:  stagnes / demo2026")
