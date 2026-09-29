"""Конвеєр подій кур'єрів з уроку 24: кожна стадія — «ітерабельне → ітерабельне»."""

from itertools import dropwhile


def minutes(hhmm):
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


def parse(lines, rejected):
    for line in lines:
        parts = line.split()
        if len(parts) != 4 or not parts[2].isdigit():
            rejected.append(line)
            continue
        time, courier, order, kind = parts
        yield {"time": minutes(time), "courier": courier, "order": int(order), "kind": kind}


def in_shift(events, start):
    return dropwhile(lambda event: event["time"] < start, events)


def durations(events):
    picked = {}
    for event in events:
        if event["kind"] == "picked":
            picked[event["order"]] = event["time"]
        elif event["kind"] == "delivered" and event["order"] in picked:
            yield event["courier"], event["time"] - picked.pop(event["order"])


def report(pairs):
    by_courier = {}
    for courier, spent in pairs:
        by_courier.setdefault(courier, []).append(spent)
    return {courier: round(sum(spent) / len(spent), 1) for courier, spent in sorted(by_courier.items())}


def read_log(path):
    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                yield line
