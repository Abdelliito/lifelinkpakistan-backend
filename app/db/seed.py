"""
Seeds the database with demo data matching the frontend's mock dataset,
so both layers demo consistently out of the box. Safe to run multiple
times — it no-ops if users already exist.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.blood_request import BloodRequest
from app.models.donor import Donor
from app.models.enums import (
    BloodGroup,
    City,
    DonorAvailability,
    RequestStatus,
    UrgencyLevel,
    UserRole,
)
from app.models.user import User

_DEMO_ADMIN = {"name": "Admin User", "email": "admin@lifelink.pk", "password": "admin123"}
_DEMO_USER = {"name": "Demo User", "email": "user@lifelink.pk", "password": "user123"}

_DONOR_USERS = [
    {"name": "Ahmed Raza", "email": "ahmed@example.com", "blood_group": BloodGroup.O_POS, "city": City.LAHORE, "phone": "+92-300-1234567"},
    {"name": "Sara Khan", "email": "sara@example.com", "blood_group": BloodGroup.A_POS, "city": City.KARACHI, "phone": "+92-321-7654321"},
    {"name": "Bilal Hussain", "email": "bilal@example.com", "blood_group": BloodGroup.B_POS, "city": City.ISLAMABAD, "phone": "+92-333-9876543", "availability": DonorAvailability.UNAVAILABLE},
    {"name": "Fatima Malik", "email": "fatima@example.com", "blood_group": BloodGroup.AB_POS, "city": City.LAHORE, "phone": "+92-311-2233445"},
    {"name": "Usman Ali", "email": "usman@example.com", "blood_group": BloodGroup.O_NEG, "city": City.FAISALABAD, "phone": "+92-345-1122334"},
    {"name": "Zainab Sheikh", "email": "zainab@example.com", "blood_group": BloodGroup.A_NEG, "city": City.KARACHI, "phone": "+92-312-9988776"},
    {"name": "Hassan Mirza", "email": "hassan@example.com", "blood_group": BloodGroup.B_NEG, "city": City.RAWALPINDI, "phone": "+92-315-4455667", "availability": DonorAvailability.UNAVAILABLE},
    {"name": "Ayesha Noor", "email": "ayesha@example.com", "blood_group": BloodGroup.O_POS, "city": City.MULTAN, "phone": "+92-316-5566778"},
]

_DEFAULT_PASSWORD = "donor123"


def seed(db: Session) -> None:
    if db.query(User).count() > 0:
        return  # already seeded

    admin = User(
        name=_DEMO_ADMIN["name"],
        email=_DEMO_ADMIN["email"],
        hashed_password=hash_password(_DEMO_ADMIN["password"]),
        role=UserRole.ADMIN,
    )
    demo_user = User(
        name=_DEMO_USER["name"],
        email=_DEMO_USER["email"],
        hashed_password=hash_password(_DEMO_USER["password"]),
        role=UserRole.USER,
    )
    db.add_all([admin, demo_user])

    donor_users: list[User] = []
    for entry in _DONOR_USERS:
        user = User(
            name=entry["name"],
            email=entry["email"],
            hashed_password=hash_password(_DEFAULT_PASSWORD),
            role=UserRole.DONOR,
            is_donor=True,
        )
        db.add(user)
        donor_users.append(user)

    db.flush()  # assign IDs before creating donor rows

    for entry, user in zip(_DONOR_USERS, donor_users):
        initials = "".join(p[0] for p in entry["name"].split()[:2]).upper()
        donor = Donor(
            user_id=user.id,
            name=entry["name"],
            initials=initials,
            blood_group=entry["blood_group"],
            city=entry["city"],
            phone=entry["phone"],
            availability=entry.get("availability", DonorAvailability.AVAILABLE),
            last_donation_date=date(2026, 3, 1),
        )
        db.add(donor)

    db.flush()

    sample_requests = [
        BloodRequest(
            user_id=demo_user.id,
            patient_name="Mohammad Farooq",
            blood_group=BloodGroup.O_POS,
            hospital="Mayo Hospital",
            city=City.LAHORE,
            urgency=UrgencyLevel.CRITICAL,
            status=RequestStatus.OPEN,
            contact_number="+92-300-1234567",
        ),
        BloodRequest(
            user_id=demo_user.id,
            patient_name="Nadia Siddiqui",
            blood_group=BloodGroup.A_POS,
            hospital="Aga Khan Hospital",
            city=City.KARACHI,
            urgency=UrgencyLevel.URGENT,
            status=RequestStatus.MATCHING_DONORS_FOUND,
            contact_number="+92-321-7654321",
        ),
    ]
    db.add_all(sample_requests)

    db.commit()
