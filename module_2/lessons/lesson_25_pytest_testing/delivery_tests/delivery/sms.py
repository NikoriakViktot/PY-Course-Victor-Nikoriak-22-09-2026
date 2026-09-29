"""Модульна функція відправки SMS — її ми підмінюємо через patch."""


def send_sms(phone, text):
    raise ConnectionError("справжня мережа недоступна в навчальному проєкті")
