import datetime

def convert_turkish_date(turkish_date):
    month_dict = {
        'OCA': 1,
        'ŞUB': 2,
        'MAR': 3,
        'NIS': 4,
        'MAY': 5,
        'HAZ': 6,
        'TEM': 7,
        'AĞU': 8,
        'EYL': 9,
        'EKI': 10,
        'KAS': 11,
        'ARA': 12
    }

    parts = turkish_date.split()

    if turkish_date == 'BUGÜN':
        return datetime.date.today()
    elif turkish_date == 'DÜN':
        return datetime.date.today() - datetime.timedelta(days=1)
    elif 'GÜN ÖNCE' in turkish_date.upper():
        days_before = int(parts[0])
        return datetime.date.today() - datetime.timedelta(days=days_before)
    elif len(parts) == 2:
        day, month = parts
        month = month.upper()  # Convert month to uppercase
        return datetime.date(datetime.date.today().year, month_dict[month], int(day))
    else:
        raise ValueError(f"Unexpected date format: {turkish_date}")