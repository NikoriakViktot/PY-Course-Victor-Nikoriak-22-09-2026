from delivery.events import durations, in_shift, minutes, parse, read_log, report


def test_minutes():
    assert minutes("18:00") == 1080
    assert minutes("00:05") == 5


def test_parse_rejects_broken_lines(log_lines):
    rejected = []
    events = list(parse(log_lines, rejected))
    assert len(events) == 5
    assert rejected == ["18:24 ?? зламаний рядок"]
    assert events[0] == {"time": 1078, "courier": "D-1", "order": 97, "kind": "delivered"}


def test_parse_is_lazy():
    rejected = []
    stream = parse(["зовсім не подія"], rejected)
    assert rejected == []          # генератор ще нічого не читав
    assert list(stream) == []
    assert rejected == ["зовсім не подія"]


def test_in_shift_drops_previous_shift(log_lines):
    events = list(in_shift(parse(log_lines, []), minutes("18:00")))
    assert [event["order"] for event in events] == [101, 102, 101, 102]


def test_durations_pairs_picked_and_delivered(make_event):
    lines = [
        make_event(order=1, kind="picked", time="18:00"),
        make_event(order=2, kind="picked", time="18:05", courier="D-2"),
        make_event(order=1, kind="delivered", time="18:20"),
        make_event(order=3, kind="delivered", time="18:30"),   # без picked — пропускаємо
    ]
    assert list(durations(parse(lines, []))) == [("D-1", 20)]


def test_report_averages_by_courier():
    assert report([("D-2", 24), ("D-1", 18), ("D-1", 21)]) == {"D-1": 19.5, "D-2": 24.0}
    assert report([]) == {}


def test_whole_pipeline(log_lines):
    rejected = []
    result = report(durations(in_shift(parse(log_lines, rejected), minutes("18:00"))))
    assert result == {"D-1": 18.0, "D-2": 24.0}
    assert len(rejected) == 1


def test_read_log_from_file(tmp_path, log_lines):
    path = tmp_path / "shift.log"
    path.write_text("\n".join(log_lines) + "\n\n", encoding="utf-8")
    assert list(read_log(path)) == log_lines
