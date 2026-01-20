from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    LEARNER = "learner"
    MENTOR = "mentor"

class AccountStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"