"""
consumers.py — WebSocket Consumer для групового чату.

Код — notes_app/consumers.py з notes_chat_app = крок 7B Django-книги.
Урок 45 курсу — consumer як ще один ТРАНСПОРТ над тими самими selectors і services (урок 44):
  - членство — selectors.is_group_member, історія — selectors.recent_chat_messages,
    запис — services.post_chat_message; у цьому файлі немає ORM (перевіряє tests_architecture.py);
  - право писати перевіряє service на КОЖНЕ повідомлення, а не лише connect();
  - учасника вилучили з групи / групу видалили → services надсилає подію, consumer закриває з'єднання (4403);
  - з'єднання лише з наших сторінок: AllowedHostsOriginValidator в asgi.py.

ЩО ТАКЕ CONSUMER?
──────────────────
Consumer — це аналог view, але для WebSocket-з'єднань.

View:     обробляє ОДИН HTTP запит → повертає відповідь → завершується.
Consumer: живе ВЕСЬ ЧАС поки відкрито WebSocket-з'єднання.

    HTTP flow:
    Browser ──── GET /groups/7/chat/ ────► view() → HttpResponse → з'єднання закрито

    WebSocket flow:
    Browser ══ ws://host/ws/groups/7/chat/ ════► consumer.connect()    ← відкрито
    Browser ══════ {content: "Привіт!"} ══════► consumer.receive()    ← повідомлення
    Browser ══════ {content: "Як справи?"} ═══► consumer.receive()    ← повідомлення
    Browser ══════════════════════════════════► consumer.disconnect()  ← закрито

Async event loop обслуговує ТИСЯЧІ таких з'єднань одночасно.
Кожне з'єднання — це окремий Consumer об'єкт в пам'яті.

ЯК CHANNEL LAYER ДОСТАВЛЯЄ ПОВІДОМЛЕННЯ?
─────────────────────────────────────────
  Consumer Viktor:              Consumer Оля:
    scope['user'] = Viktor       scope['user'] = Оля

    connect():                   connect():
      group_add(                   group_add(
        "chat_group_7",              "chat_group_7",
        self.channel_name            self.channel_name
      )   ↓                        )   ↓
          └──── Channel Layer: підписники групи "chat_group_7" ────┘

    receive("Привіт"):
      group_send(
        "chat_group_7",
        {"type": "chat_message", "content": "Привіт"}
      )
          │
          ▼ Channel Layer доставляє всім підписникам
      chat_message()    chat_message()
          │                 │
      send("Привіт")   send("Привіт")
          │                 │
      Browser Viktor   Browser Оля

ЧОМУ database_sync_to_async?
─────────────────────────────
AsyncWebsocketConsumer працює в asyncio event loop.
Django ORM — синхронний (не може виконуватись в event loop напряму).
database_sync_to_async запускає ORM в окремому потоці Django thread pool.
Це аналог sync_to_async, але оптимізований для Django ORM.
"""

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import PermissionDenied, ValidationError

from . import selectors, services

# Коди закриття 4000–4999 — «наші»: JS не перепідключається (див. static/hello_app/js/group_chat.js)
CLOSE_NOT_ALLOWED = 4403


class GroupChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer для групового чату.

    Lifecycle:
        1. connect()    — браузер відкрив з'єднання
        2. receive()    — браузер надіслав повідомлення (викликається багато разів)
        3. disconnect() — браузер закрив з'єднання

    Channel layer handlers (type у group_send → ім'я методу, крапка → підкреслення):
        4. chat_message()   — нове повідомлення від будь-якого учасника
        5. member_removed() — учасника вилучили з групи
        6. group_deleted()  — групу видалили
    """

    async def connect(self):
        """
        Викликається коли браузер відкриває WebSocket-з'єднання.

        scope — dict з метаданими з'єднання (аналог request у view):
          scope['user']                    — User (заповнений AuthMiddlewareStack)
          scope['url_route']['kwargs']     — URL параметри (group_pk з routing.py)
          scope['headers']                 — HTTP заголовки WebSocket handshake
        """
        self.user = self.scope['user']
        self.group_pk = int(self.scope['url_route']['kwargs']['group_pk'])

        # close() до accept() — відмова в handshake: браузер навіть не отримає з'єднання
        if not await database_sync_to_async(selectors.is_group_member)(self.user, self.group_pk):
            await self.close()
            return

        self.room_group_name = services.chat_group_name(self.group_pk)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        history = await database_sync_to_async(selectors.recent_chat_messages)(self.group_pk)
        for msg in history:
            await self.send(text_data=json.dumps({
                'type': 'history',
                'message_id': msg['id'],
                'author': msg['author__username'],
                'content': msg['content'],
                'timestamp': msg['timestamp'].isoformat(),
            }))

    async def disconnect(self, close_code):
        """Обов'язково відписатись від групи channel layer (інакше доставка йтиме закритому з'єднанню)."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Викликається коли браузер надсилає WebSocket-повідомлення.

        text_data — рядок (зазвичай JSON) від JS клієнта.
        JS надсилає: socket.send(JSON.stringify({content: "Привіт!"}))
        """
        try:
            content = json.loads(text_data).get('content', '')
        except (json.JSONDecodeError, AttributeError):
            return

        try:
            msg = await database_sync_to_async(services.post_chat_message)(
                group_pk=self.group_pk, author=self.user, content=content)
        except ValidationError:
            return                                   # порожнє чи задовге — ігноруємо, як і раніше
        except PermissionDenied:
            await self.close(code=CLOSE_NOT_ALLOWED)  # уже не учасник групи
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': msg.id,
                'author': self.user.username,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        """Обробник повідомлень від channel layer: переслати JSON нашому браузеру."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'author': event['author'],
            'content': event['content'],
            'timestamp': event['timestamp'],
        }))

    async def member_removed(self, event):
        """services.remove_user_from_group: якщо вилучили саме нас — закрити з'єднання."""
        if event['user_id'] == self.user.pk:
            await self.close(code=CLOSE_NOT_ALLOWED)

    async def group_deleted(self, event):
        """services.delete_group: чату більше немає."""
        await self.close(code=CLOSE_NOT_ALLOWED)
