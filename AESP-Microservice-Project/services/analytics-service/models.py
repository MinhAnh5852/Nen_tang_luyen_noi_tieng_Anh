from database import db

class SystemStat(db.Model):
    __tablename__ = 'system_stats'
    key = db.Column(db.String(50), primary_key=True) # VD: 'total_users', 'total_mentors'
    value = db.Column(db.Integer, default=0)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())