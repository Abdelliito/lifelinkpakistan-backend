"""
Reusable ABO/Rh blood-compatibility logic.

Kept isolated from the rest of the app so matching rules live in exactly
one place and can be unit tested or swapped independently of the donor
and request services that consume it.
"""

from app.models.enums import BloodGroup

# Maps a recipient's blood group to the donor blood groups compatible with it
# (i.e. which groups can safely donate TO this group).
_COMPATIBLE_DONORS: dict[BloodGroup, list[BloodGroup]] = {
    BloodGroup.A_POS: [BloodGroup.A_POS, BloodGroup.A_NEG, BloodGroup.O_POS, BloodGroup.O_NEG],
    BloodGroup.A_NEG: [BloodGroup.A_NEG, BloodGroup.O_NEG],
    BloodGroup.B_POS: [BloodGroup.B_POS, BloodGroup.B_NEG, BloodGroup.O_POS, BloodGroup.O_NEG],
    BloodGroup.B_NEG: [BloodGroup.B_NEG, BloodGroup.O_NEG],
    BloodGroup.AB_POS: list(BloodGroup),  # universal recipient
    BloodGroup.AB_NEG: [BloodGroup.A_NEG, BloodGroup.B_NEG, BloodGroup.AB_NEG, BloodGroup.O_NEG],
    BloodGroup.O_POS: [BloodGroup.O_POS, BloodGroup.O_NEG],
    BloodGroup.O_NEG: [BloodGroup.O_NEG],  # universal donor, but can only receive O-
}


def get_compatible_donor_groups(recipient_group: BloodGroup) -> list[BloodGroup]:
    """Blood groups that may safely donate to `recipient_group`."""
    return _COMPATIBLE_DONORS.get(recipient_group, [])


def is_compatible(donor_group: BloodGroup, recipient_group: BloodGroup) -> bool:
    """True if `donor_group` may safely donate to a patient needing `recipient_group`."""
    return donor_group in get_compatible_donor_groups(recipient_group)


def get_compatible_recipient_groups(donor_group: BloodGroup) -> list[BloodGroup]:
    """Reverse lookup: blood groups that `donor_group` is able to donate to."""
    return [recipient for recipient, donors in _COMPATIBLE_DONORS.items() if donor_group in donors]
