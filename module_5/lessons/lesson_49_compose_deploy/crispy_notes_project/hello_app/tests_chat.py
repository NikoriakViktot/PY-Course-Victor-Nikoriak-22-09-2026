"""Урок 45: чат групи — правила, які не покривають тести стартового проєкту (tests_consumers.py).

    python manage.py test hello_app.tests_chat
    REDIS_URL=redis://localhost:6379/0 python manage.py test hello_app.tests_chat   # з RedisChannelLayer

- право писати перевіряється на кожне повідомлення, а не лише при підключенні;
- вилучили з групи / групу видалили → відкрите з'єднання закривається (4403);
- WebSocket лише з наших сторінок (Origin) — захист від Cross-Site WebSocket Hijacking;
- межі тексту, порядок і розмір історії, сторінка чату, XSS на клієнті.
"""
import json
import shutil
import subprocess
from pathlib import Path
from unittest import skipUnless

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.security.websocket import OriginValidator
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, TransactionTestCase, override_settings

from hello_project.asgi import application, websocket_application

from . import selectors, services
from .consumers import CLOSE_NOT_ALLOWED, GroupChatConsumer
from .models import ChatMessage

APP = Path(__file__).resolve().parent


def communicator_for(group_pk, user):
    """Consumer напряму, без AuthMiddlewareStack і URLRouter: scope задаємо самі (як у tests_consumers.py)."""
    communicator = WebsocketCommunicator(GroupChatConsumer.as_asgi(), f'/ws/groups/{group_pk}/chat/')
    communicator.scope['user'] = user
    communicator.scope['url_route'] = {'kwargs': {'group_pk': str(group_pk)}}
    return communicator


class ChatServiceTests(TestCase):
    """services.post_chat_message — одне правило для будь-якого транспорту, без WebSocket."""

    def setUp(self):
        self.olena = User.objects.create_user('olena')
        self.stranger = User.objects.create_user('stranger')
        self.group = services.create_group(name="Сім'я", creator=self.olena)

    def test_text_is_trimmed_and_saved(self):
        msg = services.post_chat_message(group_pk=self.group.pk, author=self.olena, content='  Привіт!  ')
        self.assertEqual((msg.content, msg.author, msg.group), ('Привіт!', self.olena, self.group))

    def test_limits(self):
        services.post_chat_message(group_pk=self.group.pk, author=self.olena,
                                   content='я' * services.CHAT_MESSAGE_MAX_LENGTH)
        for bad in ('', '   ', 'я' * (services.CHAT_MESSAGE_MAX_LENGTH + 1), None, 42, ['текст']):
            with self.subTest(bad=repr(bad)[:20]), self.assertRaises(ValidationError):
                services.post_chat_message(group_pk=self.group.pk, author=self.olena, content=bad)

    def test_only_members_write(self):
        with self.assertRaises(PermissionDenied):
            services.post_chat_message(group_pk=self.group.pk, author=self.stranger, content='Я тут чужий')
        self.assertEqual(ChatMessage.objects.count(), 0)

    def test_history_is_last_50_oldest_first(self):
        for i in range(55):
            ChatMessage.objects.create(group=self.group, author=self.olena, content=f'повідомлення {i}')
        history = selectors.recent_chat_messages(self.group.pk)
        self.assertIsInstance(history, list)                      # не лінивий QuerySet: SQL уже виконано
        self.assertEqual([m['content'] for m in history][:2], ['повідомлення 5', 'повідомлення 6'])
        self.assertEqual((len(history), history[-1]['content']), (50, 'повідомлення 54'))


class ChatPageTests(TestCase):
    def setUp(self):
        self.olena = User.objects.create_user('olena')
        self.stranger = User.objects.create_user('stranger')
        self.group = services.create_group(name="Сім'я", creator=self.olena)

    def test_member_gets_page_stranger_404(self):
        self.client.force_login(self.olena)
        page = self.client.get(f'/groups/{self.group.pk}/chat/')
        self.assertContains(page, f'data-group-pk="{self.group.pk}"')
        self.assertContains(page, 'hello_app/js/group_chat.js')
        self.assertContains(self.client.get(f'/groups/{self.group.pk}/'), f'/groups/{self.group.pk}/chat/')
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get(f'/groups/{self.group.pk}/chat/').status_code, 404)

    def test_template_comments_are_not_rendered(self):
        """{# … #} у Django — лише однорядковий; багаторядковий потрапляє в HTML як текст.

        У коментарі шаблону є «<script> з {{ group.pk }}» — браузер відкрив би справжній <script>,
        і #chat-config опинився б усередині нього: group_chat.js не знайшов би налаштувань.
        """
        self.client.force_login(self.olena)
        page = self.client.get(f'/groups/{self.group.pk}/chat/').content.decode()
        self.assertNotIn('{#', page)
        self.assertNotIn('#}', page)
        self.assertEqual(page.count('<script'), page.count('</script>'))


class ChatAccessWhileConnectedTests(TransactionTestCase):
    """Членство змінюється, поки з'єднання відкрите."""

    def setUp(self):
        self.olena = User.objects.create_user('olena')
        self.ann = User.objects.create_user('ann')
        self.group = services.create_group(name="Сім'я", creator=self.olena)
        services.add_user_to_group(self.group, 'ann')

    async def test_removed_member_is_disconnected(self):
        olena, ann = communicator_for(self.group.pk, self.olena), communicator_for(self.group.pk, self.ann)
        self.assertTrue((await olena.connect())[0])
        self.assertTrue((await ann.connect())[0])
        await database_sync_to_async(services.remove_user_from_group)(self.group, self.ann)
        closed = await ann.receive_output(timeout=1)
        self.assertEqual(closed, {'type': 'websocket.close', 'code': CLOSE_NOT_ALLOWED})
        self.assertTrue(await olena.receive_nothing(timeout=0.3))  # Олені — нічого: подія не для неї
        await olena.send_json_to({'content': 'Анна вже не бачить'})
        self.assertEqual((await olena.receive_json_from())['content'], 'Анна вже не бачить')
        await olena.disconnect()

    async def test_member_removed_behind_the_scenes_cannot_write(self):
        """Навіть якщо подію не доставлено (вилучили в обхід services), service не пустить повідомлення."""
        ann = communicator_for(self.group.pk, self.ann)
        await ann.connect()
        await sync_to_async(self.group.user_set.remove)(self.ann)   # напряму через ORM — без події
        await ann.send_json_to({'content': 'Ще можна?'})
        self.assertEqual(await ann.receive_output(timeout=1), {'type': 'websocket.close', 'code': CLOSE_NOT_ALLOWED})
        self.assertEqual(await ChatMessage.objects.acount(), 0)

    async def test_deleted_group_closes_chat(self):
        olena = communicator_for(self.group.pk, self.olena)
        await olena.connect()
        await database_sync_to_async(services.delete_group)(self.group)
        self.assertEqual(await olena.receive_output(timeout=1), {'type': 'websocket.close', 'code': CLOSE_NOT_ALLOWED})

    async def test_too_long_message_is_ignored(self):
        olena = communicator_for(self.group.pk, self.olena)
        await olena.connect()
        await olena.send_json_to({'content': 'я' * (services.CHAT_MESSAGE_MAX_LENGTH + 1)})
        await olena.send_to(text_data='не JSON')
        await olena.send_json_to(['не', 'словник'])
        self.assertTrue(await olena.receive_nothing(timeout=0.5))
        self.assertEqual(await ChatMessage.objects.acount(), 0)
        await olena.disconnect()

    async def test_xss_text_travels_as_is(self):
        """Сервер не змінює текст: екранує клієнт (escapeHtml перед innerHTML), див. JsEscapeTests."""
        olena = communicator_for(self.group.pk, self.olena)
        await olena.connect()
        payload = '<img src=x onerror="alert(document.cookie)">'
        await olena.send_json_to({'content': payload})
        self.assertEqual((await olena.receive_json_from())['content'], payload)
        await olena.disconnect()


@override_settings(ALLOWED_HOSTS=['localhost'])
class ChatOriginTests(TransactionTestCase):
    """WebSocket-стек з asgi.py: AllowedHostsOriginValidator → AuthMiddlewareStack → URLRouter → consumer.

    Валідатор читає ALLOWED_HOSTS при створенні, тому стек збираємо в тесті — websocket_application().
    """

    def test_application_uses_the_origin_check(self):
        self.assertIsInstance(application.application_mapping['websocket'], OriginValidator)

    def setUp(self):
        self.olena = User.objects.create_user('olena', password='pass-12345')
        self.group = services.create_group(name="Сім'я", creator=self.olena)
        self.client.force_login(self.olena)
        self.cookie = f"sessionid={self.client.cookies['sessionid'].value}".encode()

    async def connect_from(self, origin):
        headers = [(b'host', b'localhost'), (b'cookie', self.cookie)]
        if origin is not None:
            headers.append((b'origin', origin))
        communicator = WebsocketCommunicator(websocket_application(), f'/ws/groups/{self.group.pk}/chat/',
                                             headers=headers)
        connected, _ = await communicator.connect()
        await communicator.disconnect()
        return connected

    async def test_own_page_connects(self):
        self.assertTrue(await self.connect_from(b'http://localhost:8000'))

    async def test_foreign_site_is_rejected(self):
        """Cookie сесії той самий, але сторінка — чужа: без перевірки Origin чат відкрився б."""
        self.assertFalse(await self.connect_from(b'https://evil.example'))
        self.assertFalse(await self.connect_from(b'http://localhost.evil.example'))

    async def test_no_origin_is_rejected(self):
        self.assertFalse(await self.connect_from(None))


@skipUnless(shutil.which('node'), 'потрібен Node.js')
class JsEscapeTests(TestCase):
    """escapeHtml з group_chat.js — справжня функція клієнта, виконана в Node.js."""

    def test_escape_html(self):
        source = (APP / 'static/hello_app/js/group_chat.js').read_text(encoding='utf-8')
        start = source.index('    function escapeHtml(str) {')
        function = source[start:source.index('\n    }\n', start) + 6]
        payload = '<img src=x onerror="alert(\'x\')">&'
        script = f'{function}\nprocess.stdout.write(escapeHtml({json.dumps(payload)}));'
        result = subprocess.run(['node', '-e', script], capture_output=True, text=True, check=True).stdout
        self.assertEqual(result, '&lt;img src=x onerror=&quot;alert(&#039;x&#039;)&quot;&gt;&amp;')

    def test_user_content_is_escaped_before_innerhtml(self):
        source = (APP / 'static/hello_app/js/group_chat.js').read_text(encoding='utf-8')
        self.assertIn('${escapeHtml(data.author)}', source)
        self.assertIn('${escapeHtml(data.content)}', source)

    def test_no_reconnect_after_rejection(self):
        """Код 4403 (вилучили з групи) — не перепідключатися; інакше — не більше MAX_FAILED_ATTEMPTS разів поспіль."""
        source = (APP / 'static/hello_app/js/group_chat.js').read_text(encoding='utf-8')
        self.assertIn('event.code >= 4000 && event.code < 5000', source)
        self.assertIn('failedAttempts > MAX_FAILED_ATTEMPTS', source)

