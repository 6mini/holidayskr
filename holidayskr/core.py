import requests
from datetime import datetime, timedelta
from korean_lunar_calendar import KoreanLunarCalendar


def download_holiday_data(url, retries=50):
    """GitHub에서 공휴일 데이터를 다운로드합니다. 실패 시 재시도."""
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()  # 성공 시 JSON 데이터 반환
        except Exception as e:
            print(f"Request error occurred: {e}, retrying {attempt + 1}/{retries}")
    raise Exception("Reached maximum retry attempts. Data download failed.")



# GitHub에서 공휴일 데이터를 다운로드
URL = "https://raw.githubusercontent.com/6mini/holidayskr/main/holidayskr.json"
HOLIDAY_DATA = download_holiday_data(URL)


def convert_lunar_to_solar(year, month, day, adjust=0):
    """음력 날짜를 양력 날짜로 변환합니다."""
    calendar = KoreanLunarCalendar()
    calendar.setLunarDate(year, int(month), int(day), False)
    solar_date = datetime.strptime(calendar.SolarIsoFormat(), '%Y-%m-%d').date()
    return solar_date + timedelta(days=adjust)


def get_holidays(year):
    """해당 연도의 모든 공휴일을 가져옵니다 (양력 고정, 음력 고정, 연도별 특정)."""
    # 양력 고정 공휴일
    fixed_holidays = [
        (datetime.strptime(f"{year}-{holiday['date']}", '%Y-%m-%d').date(), holiday['name'])
        for holiday in HOLIDAY_DATA['solar_holidays']
    ]
    
    # 음력 고정 공휴일을 양력으로 변환
    lunar_holidays = []
    for holiday in HOLIDAY_DATA['lunar_holidays']:
        month, day = holiday['date'].split('-')
        solar_date = convert_lunar_to_solar(year, month, day)
        lunar_holidays.append((solar_date, holiday['name']))
        if month in ['01', '08']:  # 설날과 추석은 전날, 다음날도 공휴일 처리
            lunar_holidays.append((solar_date - timedelta(days=1), holiday['name'] + " 전날"))
            lunar_holidays.append((solar_date + timedelta(days=1), holiday['name'] + " 다음날"))
    
    # 연도별 특정 공휴일
    specific_holidays = [
        (datetime.strptime(f"{year}-{holiday['date']}", '%Y-%m-%d').date(), holiday['name'])
        for holiday in HOLIDAY_DATA['year_specific_holidays'].get(str(year), [])
    ]
    
    # 모든 공휴일을 날짜 기준으로 정렬
    all_holidays = sorted(fixed_holidays + lunar_holidays + specific_holidays, key=lambda x: x[0])
    
    return all_holidays


def is_holiday(date_str):
    """지정된 날짜가 공휴일인지 확인합니다."""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")

    year = date.year
    all_holidays = get_holidays(year)
    
    return any(holiday[0] == date for holiday in all_holidays)


def today_is_holiday():
    """현재 날짜가 공휴일인지 확인합니다."""
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_str = kst_now.strftime('%Y-%m-%d')
    return is_holiday(date_str)


def year_holidays(year_str):
    """지정된 연도의 모든 공휴일을 반환합니다."""
    try:
        year = int(year_str)
    except ValueError:
        raise ValueError("Invalid year format. Use 'YYYY'.")

    return get_holidays(year)