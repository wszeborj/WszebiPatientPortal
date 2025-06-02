import factory
from django.contrib.auth.models import Group
from factory.django import DjangoModelFactory
from faker import Faker

from .models import Department, Doctor, Patient, Specialization, User

fake = Faker("pl_PL")


def add_permissions_to_group(group, role):
    from django.contrib.auth.models import Permission

    if role == User.Role.DOCTOR:
        doctor_permissions = [
            "add_scheduleday",
            "change_scheduleday",
            "delete_scheduleday",
            "view_scheduleday",
            "add_specialization",
            "view_scheduleday",
            "view_appointment",
            "change_appointment",
            "delete_appointment",
        ]

        for perm_code in doctor_permissions:
            try:
                # app_label, codename = perm_code.split('.')
                codename = perm_code
                perm = Permission.objects.get(
                    # content_type__app_label=app_label
                    codename=codename
                )
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username", "pesel")

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    is_active = True

    role = factory.Iterator([User.Role.PATIENT, User.Role.DOCTOR, User.Role.ADMIN])
    phone_number = factory.Sequence(lambda n: f"{n:09d}")
    pesel = factory.Sequence(lambda n: f"{n:011d}")
    street = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    postal_code = factory.Faker("postcode")
    avatar = factory.django.ImageField(color="blue")

    @factory.post_generation
    def confirm_user(self, create, extracted, **kwargs):
        if not create:
            return
        self.is_staff = self.role == User.Role.ADMIN
        self.save()

    @factory.post_generation
    def assign_group(self, create, extracted, **kwargs):
        if not create:
            return

        role_to_group = {
            User.Role.PATIENT: "patient_group",
            User.Role.DOCTOR: "doctor_group",
            User.Role.ADMIN: "staff_group",
        }

        group_name = role_to_group.get(self.role)
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.add(group)

            if created:
                add_permissions_to_group(group, self.role)

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        if not create:
            return

        password = extracted if extracted else "password123"
        self.set_password(password)
        self.save()


class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient

    user = factory.SubFactory(UserFactory, role=User.Role.PATIENT)


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ("name",)

    name = factory.Iterator(
        [
            "Surgery Department",
            "Cardiology Department",
            "Pediatrics Department",
            "Neurology Department",
            "Oncology Department",
            "Internal Medicine Department",
            "Mental Health Department",
            "Imaging Department",
            "Women's Health Department",
            "Dentistry Department",
            "Urology Department",
            "Emergency Department",
            "General Department",
        ]
    )
    description = factory.Faker("text", max_nb_chars=200)
    photo = factory.django.ImageField(color="green")


class SpecializationFactory(DjangoModelFactory):
    class Meta:
        model = Specialization
        django_get_or_create = ("name",)

    name = factory.Iterator(
        [
            "Cardiology",
            "Dermatology",
            "Gastroenterology",
            "Neurology",
            "Oncology",
            "Pediatrics",
            "Psychiatry",
            "Radiology",
            "Surgery",
            "Allergology",
            "Anesthesiology",
            "Angiology",
            "Audiology",
            "Balneology",
            "Pediatric Surgery",
            "Thoracic Surgery",
            "Vascular Surgery",
            "Oncological Surgery",
            "Plastic Surgery",
            "Maxillofacial Surgery",
            "Pulmonology",
            "Internal Medicine",
            "Infectious Diseases",
            "Diabetology",
            "Laboratory Diagnostics",
            "Endocrinology",
            "Epidemiology",
            "Clinical Pharmacology",
            "Physiotherapy",
            "Phthisiology",
            "Clinical Genetics",
            "Geriatrics",
            "Gynecologic Oncology",
            "Obstetrics and Gynecology",
            "Hematology",
            "Hypertensiology",
            "Clinical Immunology",
            "Cardiac Surgery",
            "Pediatric Cardiology",
            "Laryngology",
            "Nuclear Medicine",
            "Occupational Medicine",
            "Emergency Medicine",
            "Family Medicine",
            "Forensic Medicine",
            "Sports Medicine",
            "Medical Microbiology",
            "Nephrology",
            "Neonatology",
            "Neurosurgery",
            "Pediatric Neurology",
            "Ophthalmology",
            "Pediatric Oncology and Hematology",
            "Orthopedics and Traumatology",
            "Otorhinolaryngology",
            "Pathomorphology",
            "Medical Rehabilitation",
            "Rheumatology",
            "Sexology",
            "Dentistry",
            "Clinical Toxicology",
            "Clinical Transfusiology",
            "Clinical Transplantology",
            "Urology",
            "Pediatric Urology",
        ]
    )
    description = factory.Faker("text", max_nb_chars=200)
    department = factory.SubFactory(DepartmentFactory)


class DoctorFactory(DjangoModelFactory):
    class Meta:
        model = Doctor

    user = factory.SubFactory(UserFactory, role=User.Role.DOCTOR, is_active=True)
    title = factory.Iterator(["Dr", "Prof.", "Dr hab.", "lek."])
    description = factory.Faker("paragraph")
    confirmed = True

    @factory.post_generation
    def specialization(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for spec in extracted:
                self.specialization.add(spec)
        else:
            specs_count = fake.random_int(min=1, max=3)
            specs = [SpecializationFactory() for _ in range(specs_count)]
            self.specialization.add(*specs)
