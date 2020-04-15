from datetime import datetime, timedelta

def get_monday() -> datetime:
    """
    Get nearest monday

    Returns:
        datetime.datetime: Nearest monday (with current hour)
    """

    # Check today's weekday and hour
    now = datetime.now()
    weekday = now.weekday()

    return now - timedelta(days=weekday)

def format_date(date) -> str:
    """
    Format date in server's format (eg. 2018-05-02)

    Params:
        date (datetime || date): object to format
    
    Returns:
        string: Formatted string
    """

    return date.strftime('%Y-%m-%d')