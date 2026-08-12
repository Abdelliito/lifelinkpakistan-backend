import enum


class BloodGroup(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class City(str, enum.Enum):
    KARACHI = "Karachi"
    LAHORE = "Lahore"
    ISLAMABAD = "Islamabad"
    RAWALPINDI = "Rawalpindi"
    FAISALABAD = "Faisalabad"
    MULTAN = "Multan"
    PESHAWAR = "Peshawar"
    QUETTA = "Quetta"
    SIALKOT = "Sialkot"
    HYDERABAD = "Hyderabad"


class UrgencyLevel(str, enum.Enum):
    CRITICAL = "Critical"
    URGENT = "Urgent"
    NORMAL = "Normal"


class RequestStatus(str, enum.Enum):
    OPEN = "Open"
    MATCHING_DONORS_FOUND = "Matching Donors Found"
    COMPLETED = "Completed"
    CLOSED = "Closed"


class DonorAvailability(str, enum.Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"


class UserRole(str, enum.Enum):
    USER = "USER"
    DONOR = "DONOR"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
