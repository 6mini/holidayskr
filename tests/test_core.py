import pytest
from datetime import datetime
from holidayskr.core import download_holiday_data, convert_lunar_to_solar, get_holidays, is_holiday, today_is_holiday, year_holidays

# 1. 공휴일 데이터 다운로드 테스트
def test_download_holiday_data():
    url = "https://raw.githubusercontent.com/6mini/holidayskr/main/holidayskr.json"
    data = download_holiday_data(url)
    assert data is not None, "다운로드 받은 데이터가 없습니다."
    assert 'solar_holidays' in data, "'solar_holidays' 키가 데이터에 없습니다."
    assert 'lunar_holidays' in data, "'lunar_holidays' 키가 데이터에 없습니다."
    assert 'year_specific_holidays' in data, "'year_specific_holidays' 키가 데이터에 없습니다."

# 2. 음력에서 양력으로의 변환 테스트
@pytest.mark.parametrize("year, month, day, expected", [
    (2024, 1, 1, "2024-02-10"),
    (2025, 1, 1, "2025-01-29"),
    (2026, 1, 1, "2026-02-17"),
])
def test_convert_lunar_to_solar(year, month, day, expected):
    result = convert_lunar_to_solar(year, month, day)
    assert result.strftime('%Y-%m-%d') == expected, f"예상 결과와 다릅니다: {expected}, 받은 결과: {result}"

# 3. 특정 날짜가 공휴일인지 확인하는 테스트
@pytest.mark.parametrize("date_str, expected", [
    ("2024-01-01", True),  # 신정
    ("2024-02-10", True),  # 설날
    ("2024-05-01", True),  # 근로자의 날
    ("2024-12-25", True),  # 크리스마스
    ("2024-06-06", True),  # 현충일
    ("2024-04-10", True),  # 22대 국회의원선거
    ("2024-04-22", False)  # 공휴일이 아닌 날
])
def test_is_holiday(date_str, expected):
    assert is_holiday(date_str) == expected, f"{date_str}의 공휴일 여부가 예상과 다릅니다."

# 4. 연도별 공휴일 리스트 테스트
def test_year_holidays():
    year = "2024"
    holidays = year_holidays(year)
    assert holidays is not None, "반환된 공휴일 리스트가 없습니다."
    assert len(holidays) > 0, "공휴일 리스트가 비어있습니다."

# 5. 현재 날짜가 공휴일인지 확인하는 테스트
def test_today_is_holiday():
    # 이 테스트는 현재 날짜에 따라 결과가 달라질 수 있으므로, 실제 사용 시에는 적절히 수정이 필요합니다.
    # 예를 들어, 실제 공휴일 날짜를 설정하여 테스트하거나, 테스트 환경에서 날짜를 조작하는 방법을 고려할 수 있습니다.
    is_holiday = today_is_holiday()
    assert isinstance(is_holiday, bool), "반환된 값이 bool 타입이 아닙니다."

# 6. 연도별 특정 공휴일 테스트
@pytest.mark.parametrize("year, date, expected_name", [
    (2024, "2024-02-12", "대체 공휴일(설날)"),
    (2024, "2024-04-10", "제22대 국회의원 선거일"),
    (2025, "2025-03-03", "대체 공휴일(3·1절)"),
    (2026, "2026-05-25", "대체 공휴일(석가탄신일)"),
])
def test_year_specific_holidays(year, date, expected_name):
    holidays = year_holidays(str(year))
    assert any(holiday for holiday in holidays if holiday[0].strftime('%Y-%m-%d') == date and holiday[1] == expected_name), \
        f"{year}년에 {date}({expected_name})가 공휴일 리스트에 없습니다."


# 7. 음력 공휴일의 양력 변환과 연속된 날짜 테스트
@pytest.mark.parametrize("year, lunar_date, expected_dates", [
    (2024, "01-01", ["2024-02-09", "2024-02-10", "2024-02-11"]),  # 설날과 전날, 다음날
    (2024, "08-15", ["2024-09-16", "2024-09-17", "2024-09-18"]),  # 추석과 전날, 다음날
])
def test_lunar_holidays_with_surrounding_days(year, lunar_date, expected_dates):
    holidays = year_holidays(str(year))
    for expected_date in expected_dates:
        assert any(holiday for holiday in holidays if holiday[0].strftime('%Y-%m-%d') == expected_date), \
            f"{year}년 {lunar_date}의 변환된 날짜 {expected_date}가 공휴일 리스트에 없습니다."


# 8. 잘못된 입력에 대한 예외 처리 테스트
def test_invalid_date_format():
    with pytest.raises(ValueError):
        is_holiday("2024-02-30")  # 잘못된 날짜 형식

def test_invalid_year_format():
    with pytest.raises(ValueError):
        year_holidays("20XX")  # 잘못된 연도 형식


# 9. 비공휴일 확인 테스트
@pytest.mark.parametrize("date_str", [
    "2024-01-02",  # 신정 다음 날
    "2024-07-01",  # 중간의 평일
])
def test_not_a_holiday(date_str):
    assert not is_holiday(date_str), f"{date_str}는 공휴일이 아닙니다."