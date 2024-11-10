from datetime import datetime, timedelta
import re
import pytz
from config import DEFAULT_TIMEZONE

def parse_specific_time(time_str: str) -> datetime:
    """
    Parse specific time string (HH:MM) and return datetime object
    """
    try:
        # Get current date
        tz = pytz.timezone(DEFAULT_TIMEZONE)
        current_time = datetime.now(tz)
        
        # Parse hours and minutes
        hours, minutes = map(int, time_str.split(':'))
        
        # Create new datetime object
        reminder_time = current_time.replace(
            hour=hours,
            minute=minutes,
            second=0,
            microsecond=0
        )
        
        # If the time is already passed today, set it for tomorrow
        if reminder_time <= current_time:
            reminder_time += timedelta(days=1)
            
        return reminder_time
    except (ValueError, TypeError):
        raise ValueError("Invalid time format")

def parse_delay_time(delay_str: str) -> datetime:
    """
    Parse delay time string (e.g., "1г 30хв" or "2 години") and return datetime object
    """
    try:
        tz = pytz.timezone(DEFAULT_TIMEZONE)
        current_time = datetime.now(tz)
        
        # Convert Ukrainian time units to hours and minutes
        hours = 0
        minutes = 0
        
        # Pattern for hours
        hours_pattern = r'(\d+)\s*(?:г|год|година|години|годин)'
        hours_match = re.search(hours_pattern, delay_str, re.IGNORECASE)
        if hours_match:
            hours = int(hours_match.group(1))
            
        # Pattern for minutes
        minutes_pattern = r'(\d+)\s*(?:хв|хвилина|хвилини|хвилин)'
        minutes_match = re.search(minutes_pattern, delay_str, re.IGNORECASE)
        if minutes_match:
            minutes = int(minutes_match.group(1))
            
        if hours == 0 and minutes == 0:
            raise ValueError("No valid time units found")
            
        # Calculate reminder time
        reminder_time = current_time + timedelta(hours=hours, minutes=minutes)
        return reminder_time
        
    except (ValueError, TypeError):
        raise ValueError("Invalid delay format")

def format_reminder_time(dt: datetime) -> str:
    """
    Format datetime object to readable string
    """
    tz = pytz.timezone(DEFAULT_TIMEZONE)
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt).astimezone(tz)
    return dt.strftime("%d.%m.%Y %H:%M")