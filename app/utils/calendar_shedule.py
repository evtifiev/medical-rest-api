# -*- coding: utf-8 -*-

from business_calendar import Calendar, MO, TU, WE, TH, FR
import datetime

from app.model.schedule import Schedule


def f_workday(x):
    try:
        return {
            'MO': MO,
            'TU': TU,
            'WE': WE,
            'TH': TH,
            'FR': FR,
        }[x]
    except KeyError:
        print('KeyError')


# Преобразование списка рабочих дней
def _workdays(workdays=[]):
    list_wordays = []
    if workdays:
        for day in workdays:
            list_wordays.append(f_workday(day))
        return list_wordays
    else:
        return [MO, TU, WE, TH, FR]


# Получение списка праздничных дней
def _holidays(days=[]):
    if not days:
        return []


# Один день, временной интервал(для создания расписания)
def schedule(date_start, date_end, interval, doctor, creator, session):
    while date_start < date_end:
        date_start_i = date_start
        date_start += datetime.timedelta(minutes=interval)
        print('{0} {1}'.format(date_start_i.strftime("%Y-%m-%d %H:%M:%S"), date_start.strftime("%Y-%m-%d %H:%M:%S")))

        schedule = Schedule(date_start=date_start_i, date_end=date_start, doctor_id=doctor, creator_id=creator)
        session.add(schedule)

    session.commit()


# Создание полного списка и запись в БД
def generate(start_date=None, end_date=None, holidays_list=[], workdays_list=[],
             start_time='', end_time='', interval=0, doctor=None, creator=None, session=None):
    # Если дата одна, поставляем дату окончания сегодня
    if not end_date:
        # Дата окончания периода + 1 день(сутки)
        end_date = datetime.datetime.strptime(start_date, "%d.%m.%Y") + datetime.timedelta(days=1)

    # Дата начала периода
    start_date = datetime.datetime.strptime(start_date, '%d.%m.%Y')

    # Праздничные дни
    holidays = _holidays(holidays_list)

    # Список рабочих дней
    workdays = _workdays(workdays_list)

    # Время начала работы
    start_time = datetime.datetime.strptime(start_time, '%H:%M')
    # Время окончания работы
    end_time = datetime.datetime.strptime(end_time, '%H:%M')

    # Интервал приема
    interval = int(interval)

    # Объявление экземпляра класса календарь
    cal = Calendar(workdays=workdays, holidays=holidays)

    for x in cal.range(start_date, end_date):
        schedule(x + datetime.timedelta(hours=start_time.hour, minutes=start_time.minute),
                 x + datetime.timedelta(hours=end_time.hour, minutes=end_time.minute),
                 interval=interval,
                 doctor=doctor,
                 creator=creator,
                 session=session)


if __name__ == "__main__":
    generate(start_date='3.04.2019')
    # func worksdays = true
