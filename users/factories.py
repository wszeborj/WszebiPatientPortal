import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .models import Doctor, Patient, Specialization, User

fake = Faker("pl_PL")


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


class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient

    user = factory.SubFactory(UserFactory, role=User.Role.PATIENT)


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
    description = factory.Faker("paragraph")


class DoctorFactory(DjangoModelFactory):
    class Meta:
        model = Doctor

    user = factory.SubFactory(UserFactory, role=User.Role.DOCTOR)
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
