import pytest
from datetime import datetime
from holidayskr.core import is_holiday, year_holidays, convert_lunar_to_solar

# 픽스처를 사용하여 반복되는 테스트 데이터를 관리합니다.
@pytest.fixture(scope="module")
def lunar_new_year_dates():
    return [
        ("2024", "2024-02-10"),  # 음력 설날
        ("2025", "2025-01-29"),
        ("2026", "2026-02-17"),
    ]

@pytest.mark.parametrize("year,expected_date", [
    ("2024", "2024-01-01"),  # 신정
    ("2025", "2025-03-01"),  # 3·1절
    ("2026", "2026-05-05"),  # 어린이날
])
def test_fixed_holidays(year, expected_date):
    """고정된 양력 휴일이 정확히 계산되는지 확인합니다."""
    holidays = year_holidays(year)
    assert datetime.strptime(expected_date, '%Y-%m-%d').date() in holidays

def test_lunar_new_year_dates(lunar_new_year_dates):
    """음력 설날이 양력으로 정확히 변환되는지 확인합니다."""
    for year, expected_date in lunar_new_year_dates:
        converted_date = convert_lunar_to_solar(int(year), 1, 1)  # 설날은 항상 음력 1월 1일
        assert converted_date == datetime.strptime(expected_date, '%Y-%m-%d').date()

@pytest.mark.parametrize("date_str,expected", [
    ("2024-02-09", True),   # 설날 전날
    ("2024-02-10", True),   # 설날
    ("2024-02-11", True),   # 설날 다음날
    ("2024-02-12", True),   # 대체 공휴일 (설날)
    ("2024-05-06", True),   # 대체 공휴일 (어린이날 다음날)
])
def test_is_holiday_various_cases(date_str, expected):
    """다양한 날짜에 대해 휴일 여부를 정확히 판단합니다."""
    assert is_holiday(date_str) == expected

def test_year_holidays_includes_substitute_holidays():
    """대체 공휴일이 포함되어 있는지 확인합니다."""
    holidays_2026 = year_holidays('2026')
    substitute_holidays = [
        datetime.strptime("2026-03-02", '%Y-%m-%d').date(),  # 3·1절 대체 휴일
        datetime.strptime("2026-05-25", '%Y-%m-%d').date(),  # 석가탄신일 대체 휴일
    ]
    for holiday in substitute_holidays:
        assert holiday in holidays_2026

# 에러 핸들링 테스트
@pytest.mark.parametrize("invalid_date", [
    "2024-02-30",  # 존재하지 않는 날짜
    "abcd-ef-gh",  # 잘못된 형식
])
def test_is_holiday_with_invalid_dates(invalid_date):
    """잘못된 날짜 형식이 제공되었을 때 적절한 에러를 반환하는지 확인합니다."""
    with pytest.raises(ValueError):
        is_holiday(invalid_date)

# 추가적인 테스트 케이스와 엣지 케이스를 고려하여 테스트를 확장할 수 있습니다.