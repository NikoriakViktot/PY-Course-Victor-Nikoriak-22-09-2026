"""Навчальний HTTP API диспетчерської «Смачно + Таксі» для уроку 31.

Лише стандартна бібліотека: працює локально, у Jupyter і в Colab без інтернету.
Як влаштовано сервер, розберемо в уроках 32–38; зараз він — «той бік» для клієнта.

    from smachno_api import start_server
    base_url = start_server()          # http://127.0.0.1:8031, сервер у фоновому потоці

Ендпоінти:
    GET  /restaurants                  список ресторанів (?district=Поділ — фільтр)
    GET  /restaurants/<id>             один ресторан або 404
    GET  /restaurants/<id>/status      «відкрито?» з затримкою ?delay=0.5 (секунди)
    POST /orders                       створити замовлення: JSON {restaurant_id, customer, total};
                                       потрібен заголовок Authorization: Bearer smachno-token
    GET  /flaky                        перші 2 запити — 503, далі — 200 (для повторних спроб)
    GET  /slow                         відповідає через 3 секунди (для тайм-аутів)
    POST /reset                        скинути замовлення й лічильник /flaky
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

TOKEN = "smachno-token"
RESTAURANTS = [
    {"id": 1, "name": "Борщ і Ко", "district": "Поділ"},
    {"id": 2, "name": "Піца Поділ", "district": "Поділ"},
    {"id": 3, "name": "Суші Оболонь", "district": "Оболонь"},
    {"id": 4, "name": "Вареники 24/7", "district": "Центр"},
    {"id": 5, "name": "Шаурма Центр", "district": "Центр"},
]

_state = {"orders": [], "flaky_calls": 0}
_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server_version = "SmachnoAPI/1.0"
    protocol_version = "HTTP/1.1"          # з'єднання можна перевикористати (keep-alive)
    disable_nagle_algorithm = True         # не чекати, поки TCP «назбирає» пакет

    def log_message(self, *args):          # не засмічувати вивід ноутбука
        pass

    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):   # клієнт не дочекався (тайм-аут)
            pass

    def do_GET(self):
        url = urlparse(self.path)
        parts = [p for p in url.path.split("/") if p]
        query = parse_qs(url.query)

        if parts == ["restaurants"]:
            district = query.get("district", [None])[0]
            items = [r for r in RESTAURANTS if district is None or r["district"] == district]
            return self._send(200, items)

        if len(parts) >= 2 and parts[0] == "restaurants":
            restaurant = next((r for r in RESTAURANTS if str(r["id"]) == parts[1]), None)
            if restaurant is None:
                return self._send(404, {"error": f"ресторан {parts[1]} не знайдено"})
            if parts[2:] == ["status"]:
                time.sleep(float(query.get("delay", ["0"])[0]))
                return self._send(200, {"id": restaurant["id"], "name": restaurant["name"], "open": True})
            if len(parts) == 2:
                return self._send(200, restaurant)

        if parts == ["flaky"]:
            with _lock:
                _state["flaky_calls"] += 1
                calls = _state["flaky_calls"]
            if calls <= 2:
                return self._send(503, {"error": "сервіс тимчасово недоступний", "attempt": calls})
            return self._send(200, {"ok": True, "attempt": calls})

        if parts == ["slow"]:
            time.sleep(3)
            return self._send(200, {"ok": True})

        return self._send(404, {"error": "невідомий шлях"})

    def do_POST(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        raw_body = self.rfile.read(int(self.headers.get("Content-Length", 0)))   # тіло читаємо завжди
        if parts == ["reset"]:
            with _lock:
                _state["orders"].clear()
                _state["flaky_calls"] = 0
            return self._send(200, {"ok": True})

        if parts != ["orders"]:
            return self._send(404, {"error": "невідомий шлях"})
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            return self._send(401, {"error": "потрібен заголовок Authorization: Bearer <токен>"})
        try:
            data = json.loads(raw_body or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "тіло запиту — не JSON"})
        if not isinstance(data, dict):
            return self._send(400, {"error": "тіло запиту — має бути JSON-об'єкт"})

        errors = []
        if not any(r["id"] == data.get("restaurant_id") for r in RESTAURANTS):
            errors.append("restaurant_id: такого ресторану немає")
        if not data.get("customer"):
            errors.append("customer: обов'язкове поле")
        if not isinstance(data.get("total"), (int, float)) or data["total"] <= 0:
            errors.append("total: число більше за 0")
        if errors:
            return self._send(422, {"errors": errors})

        with _lock:
            order = {"id": 100 + len(_state["orders"]) + 1, "status": "new", **data}
            _state["orders"].append(order)
        return self._send(201, order)


_server = None


def start_server(port=8031):
    """Запустити сервер у фоновому потоці (один раз) і повернути його адресу."""
    global _server
    if _server is None:
        _server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}"


if __name__ == "__main__":
    print("Smachno API:", start_server(), "— Ctrl+C, щоб зупинити")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
