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

def _get_next_weekday(date, occupied_dates):
    while date.weekday() >= 5 or date in occupied_dates:
        date += timedelta(days=1)
    return date

def get_substitute_holiday(fixed_holidays:list, lunar_holidays:list, original_holidays:dict) -> list:
    result_holidays = []
    occupied_dates = set(original_holidays)
    # 양력 대체 휴무부터 추가
    for holiday in fixed_holidays:
        holi_date, name, sub_rule = holiday
        result_holidays.append((holi_date, name))
        if not (sub_rule and (holi_date.weekday() >= 5 or original_holidays.get(holi_date, 0) > 1)): continue

        substitute_date = _get_next_weekday(holi_date, occupied_dates)
        result_holidays.append((substitute_date, f"대체 공휴일({name})"))
        occupied_dates.add(substitute_date)

    # 음력 대체 휴무 추가
    for holiday in lunar_holidays:
        holi_date, name, sub_rule = holiday
        result_holidays.append((holi_date, name))
        if holi_date.weekday() < 5 and original_holidays.get(holi_date, 0) > 1:
            continue
        if name.startswith(("설날", "추석")):
            if holi_date.weekday() >= 6:
                name = "설날" if name.startswith("설날") else "추석"
                substitute_date = _get_next_weekday(holi_date, occupied_dates)
                result_holidays.append((substitute_date, f"대체 공휴일({name})"))
                occupied_dates.add(substitute_date)
        else:
            if holi_date.weekday() >= 5:
                substitute_date = _get_next_weekday(holi_date, occupied_dates)
                result_holidays.append((substitute_date, f"대체 공휴일({name})"))
                occupied_dates.add(substitute_date)


    return result_holidays

def get_holidays(year):
    """해당 연도의 모든 공휴일을 가져옵니다 (양력 고정, 음력 고정, 연도별 특정)."""
    dict_holidays = {}
    # 양력 고정 공휴일
    fixed_holidays = []
    for holiday in HOLIDAY_DATA['solar_holidays']:
        holi_date = datetime.strptime(f"{year}-{holiday['date']}", '%Y-%m-%d').date()

        fixed_holidays.append((holi_date, holiday['name'], holiday.get('sub_rule', False)))
        dict_holidays[holi_date] = dict_holidays.get(holi_date, 0) + 1
    
    # 음력 고정 공휴일을 양력으로 변환
    lunar_holidays = []
    for holiday in HOLIDAY_DATA['lunar_holidays']:
        month, day = holiday['date'].split('-')
        solar_date = convert_lunar_to_solar(year, month, day)
        lunar_holidays.append((solar_date, holiday['name'], holiday.get('sub_rule', True)))
        dict_holidays[solar_date] = dict_holidays.get(solar_date, 0) + 1
        if month in ['01', '08']:  # 설날과 추석은 전날, 다음날도 공휴일 처리
            prev_date = solar_date - timedelta(days=1)
            lunar_holidays.append((prev_date, holiday['name'] + " 전날", holiday.get('sub_rule', True)))
            dict_holidays[prev_date] = dict_holidays.get(prev_date, 0) + 1
            next_date = solar_date + timedelta(days=1)
            lunar_holidays.append((next_date, holiday['name'] + " 다음날", holiday.get('sub_rule', True)))
            dict_holidays[next_date] = dict_holidays.get(next_date, 0) + 1

    all_holidays = get_substitute_holiday(fixed_holidays, lunar_holidays, dict_holidays)

    # 연도별 특정 공휴일
    specific_holidays = [
        (datetime.strptime(f"{year}-{holiday['date']}", '%Y-%m-%d').date(), holiday['name'])
        for holiday in HOLIDAY_DATA['year_specific_holidays'].get(str(year), [])
    ]
    
    # 모든 공휴일을 날짜 기준으로 정렬
    all_holidays = sorted(all_holidays + specific_holidays, key=lambda x: x[0])
    
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

def reset_holiday_data():
    """서버에서 휴일 데이터를 재 다운로드하여 최신화 합니다."""
    global HOLIDAY_DATA, CONVERSION_HOLIDAY_DATA
    HOLIDAY_DATA = download_holiday_data(URL)