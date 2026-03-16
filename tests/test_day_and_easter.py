import datetime
import zoneinfo

def get_mst_time():
    mst = zoneinfo.ZoneInfo('America/Denver') # MST/MDT
    return datetime.datetime.now(mst)

def get_easter_date(year):
    # Computus for Easter date (Anonymous Gregorian algorithm)
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def days_until_easter():
    # ALWAYS evaluate based on TODAY (MST/MDT) to prevent passing an arbitrary date
    current_date = get_mst_time().date()
    easter_this_year = get_easter_date(current_date.year)

    if current_date > easter_this_year:
        easter_next_year = get_easter_date(current_date.year + 1)
        delta = easter_next_year - current_date
        return delta.days, easter_next_year
    else:
        delta = easter_this_year - current_date
        return delta.days, easter_this_year

def test_day_of_week():
    now_mst = get_mst_time()
    day_name = now_mst.strftime("%A")
    days_left, next_easter = days_until_easter()

    print(f"Current MST/MDT Time: {now_mst}")
    print(f"Day of the week: {day_name}")
    print(f"Next Easter is on: {next_easter.strftime('%B %d, %Y')}")
    print(f"Days until Easter: {days_left}")

if __name__ == "__main__":
    test_day_of_week()
