
from enum import Enum
class AccountStatus(str,Enum):
    ACTIVE="active"
    DISABLED="disabled"
class UserRole(str,Enum):
    ADMIN="admin"
    LEARNER="learner"
    MENTOR="mentor"
