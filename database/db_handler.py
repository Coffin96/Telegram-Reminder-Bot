from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    reminder_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_reminder(self, user_id: int, text: str, reminder_time: datetime) -> Reminder:
        """Add new reminder to database"""
        reminder = Reminder(
            user_id=user_id,
            text=text,
            reminder_time=reminder_time
        )
        self.session.add(reminder)
        self.session.commit()
        return reminder

    def get_active_reminders(self, user_id: int) -> list:
        """Get all active reminders for user"""
        return self.session.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.is_active == True,
            Reminder.reminder_time > datetime.utcnow()
        ).all()

    def get_due_reminders(self) -> list:
        """Get all due reminders"""
        return self.session.query(Reminder).filter(
            Reminder.is_active == True,
            Reminder.reminder_time <= datetime.utcnow()
        ).all()

    def deactivate_reminder(self, reminder_id: int):
        """Deactivate reminder after it's done"""
        reminder = self.session.query(Reminder).get(reminder_id)
        if reminder:
            reminder.is_active = False
            self.session.commit()

    def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """Delete reminder"""
        reminder = self.session.query(Reminder).filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        ).first()
        if reminder:
            self.session.delete(reminder)
            self.session.commit()
            return True
        return False

    def close(self):
        """Close database session"""
        self.session.close()