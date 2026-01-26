from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    LEARNER = "learner"
    MENTOR = "mentor"
    
    # Mẹo: Thêm hàm này để dễ dàng so sánh hoặc in ra string
    def __str__(self):
        return self.value

class AccountStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    
    def __str__(self):
        return self.value