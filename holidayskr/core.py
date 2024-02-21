from datetime import datetime, timedelta
from korean_lunar_calendar import KoreanLunarCalendar

# 양력 고정 휴일
FIXED_HOLIDAYS = [
    '01-01', # 신정
    '03-01', # 3·1절
    '05-05', # 어린이날
    '06-06', # 현충일
    '08-15', # 광복절
    '10-03', # 개천절
    '10-09', # 한글날
    '12-25', # 크리스마스
]

# 음력 고정 휴일 (월, 일)
LUNAR_HOLIDAYS = [
    ('01', '01'), # 설날
    ('04', '08'), # 석가탄신일
    ('08', '15'), # 추석
]

# 특정 연도의 휴일(대체 휴일, 선거일 등): 매년 생기는 휴일을 이곳에 추가합니다.
YEAR_SPECIFIC_HOLIDAYS = {
    2024: [
        '02-12', # 대체 휴일(설날)
        '05-06', # 대체 휴일(어린이날)
    ],
    2025: [
        '03-03', # 대체 휴일(3·1절)
        '05-06', # 대체 휴일(어린이날, 석가탄신일 중복 공휴일)
    ],
    2026: [
        '03-02', # 대체 휴일(3·1절)
        '05-25', # 대체 휴일(석가탄신일)
        '06-08', # 대체 휴일(현충일)
        '08-17', # 대체 휴일(광복절) 
        '10-05', # 대체 휴일(한글날)
    ]
}

def convert_lunar_to_solar(year, month, day, adjust=0):
    """음력 날짜를 양력 날짜로 변환합니다."""
    calendar = KoreanLunarCalendar()
    calendar.setLunarDate(year, int(month), int(day), False)
    solar_date = datetime.strptime(calendar.SolarIsoFormat(), '%Y-%m-%d').date()
    return solar_date + timedelta(days=adjust)

def get_fixed_and_specific_holidays(year):
    """고정된 양력 휴일과 연도별 특정 휴일을 가져옵니다."""
    fixed_holidays = [datetime(year, int(m), int(d)).date() for m, d in (md.split('-') for md in FIXED_HOLIDAYS)]
    specific_holidays = [datetime.strptime(f"{year}-{md}", '%Y-%m-%d').date() for md in YEAR_SPECIFIC_HOLIDAYS.get(year, [])]
    return fixed_holidays + specific_holidays

def get_lunar_holidays(year):
    """해당 연도의 음력 휴일을 양력으로 변환하여 가져옵니다."""
    holidays = []
    for month, day in LUNAR_HOLIDAYS:
        holidays.append(convert_lunar_to_solar(year, month, day))
        if month in ['01', '08']:
            holidays.extend([
                convert_lunar_to_solar(year, month, day, adjust=-1),
                convert_lunar_to_solar(year, month, day, adjust=1)
            ])
    return holidays

def is_holiday(date_str):
    """지정된 날짜가 휴일인지 확인합니다."""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")

    year = date.year
    all_holidays = set(get_fixed_and_specific_holidays(year) + get_lunar_holidays(year))
    
    return date in all_holidays

def today_is_holiday():
    """현재 날짜가 휴일인지 확인합니다."""
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_str = kst_now.strftime('%Y-%m-%d')
    return is_holiday(date_str)

def year_holidays(year_str):
    """지정된 연도의 모든 휴일을 반환합니다."""
    try:
        year = int(year_str)
    except ValueError:
        raise ValueError("Invalid year format. Use 'YYYY'.")

    all_holidays = sorted(set(get_fixed_and_specific_holidays(year) + get_lunar_holidays(year)))
    return all_holidays