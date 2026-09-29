"""Урок 40: спільний доступ через групи, права в API, JWT, хешування паролів, throttle, скидання пароля."""
from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from . import services
from .models import Note


class GroupSharingTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("olena", password="Sup3r-secret!")
        self.member = User.objects.create_user("taras", password="Sup3r-secret!")
        self.stranger = User.objects.create_user("ivan", password="Sup3r-secret!")
        self.family = services.create_group(name="Сім'я", creator=self.owner)
        self.family.user_set.add(self.member)
        self.note = services.create_note(user=self.owner, title="Пароль від Wi-Fi", group=self.family)

    def test_member_sees_group_note_stranger_does_not(self):
        self.client.force_login(self.member)
        self.assertContains(self.client.get("/notes/"), "Пароль від Wi-Fi")
        self.assertEqual(self.client.get(f"/notes/{self.note.pk}/").status_code, 200)
        self.client.force_login(self.stranger)
        self.assertNotContains(self.client.get("/notes/"), "Пароль від Wi-Fi")
        self.assertEqual(self.client.get(f"/notes/{self.note.pk}/").status_code, 404)

    def test_member_cannot_edit_or_delete_in_html(self):
        self.client.force_login(self.member)
        self.client.post(f"/notes/{self.note.pk}/delete/")
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_api_member_reads_but_cannot_write(self):
        api = APIClient()
        api.force_authenticate(self.member)
        self.assertEqual(api.get(f"/api/notes/{self.note.pk}/").status_code, 200)
        self.assertEqual(api.patch(f"/api/notes/{self.note.pk}/", {"title": "Зламано"}, format="json").status_code, 403)
        self.assertEqual(api.post(f"/api/notes/{self.note.pk}/pin/").status_code, 403)
        self.assertEqual(api.delete(f"/api/notes/{self.note.pk}/").status_code, 403)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Пароль від Wi-Fi")

    def test_api_stranger_gets_404_owner_can_write(self):
        api = APIClient()
        api.force_authenticate(self.stranger)
        self.assertEqual(api.delete(f"/api/notes/{self.note.pk}/").status_code, 404)
        api.force_authenticate(self.owner)
        self.assertEqual(api.patch(f"/api/notes/{self.note.pk}/", {"title": "Новий пароль"}, format="json").status_code, 200)

    def test_note_form_offers_only_own_groups(self):
        services.create_group(name="Чужа команда", creator=self.stranger)
        self.client.force_login(self.member)
        page = self.client.get("/notes/new/")
        self.assertContains(page, "Сім&#x27;я")
        self.assertNotContains(page, "Чужа команда")


class JWTTests(TestCase):
    def setUp(self):
        cache.clear()                                       # лічильники throttle живуть у кеші
        self.user = User.objects.create_user("olena", password="Sup3r-secret!")
        services.create_note(user=self.user, title="Купити квитки")
        self.api = APIClient()

    def obtain(self, password="Sup3r-secret!"):
        return self.api.post("/api/token/", {"username": "olena", "password": password}, format="json")

    def test_obtain_and_use_access_token(self):
        tokens = self.obtain().json()
        self.assertEqual(set(tokens), {"access", "refresh"})
        anonymous = self.api.get("/api/notes/")
        self.assertEqual((anonymous.status_code, anonymous["WWW-Authenticate"]), (401, 'Bearer realm="api"'))
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        self.assertEqual([n["title"] for n in self.api.get("/api/notes/").json()], ["Купити квитки"])

    def test_wrong_password_401(self):
        self.assertEqual(self.obtain("wrong").status_code, 401)

    def test_refresh_gives_new_access(self):
        refresh = self.obtain().json()["refresh"]
        response = self.api.post("/api/token/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_tampered_forged_and_expired_tokens_are_401(self):
        access = self.obtain().json()["access"]
        header, payload, signature = access.split(".")
        tampered = f"{header}.{payload}.{signature[:-4]}AAAA"
        forged = jwt.encode({"token_type": "access", "user_id": str(self.user.id), "exp": 9999999999, "jti": "x"},
                            "зовсім-не-той-ключ-підпису-довжиною-понад-32-байти", algorithm="HS256")
        expired = AccessToken.for_user(self.user)
        expired.set_exp(lifetime=-timedelta(seconds=1))
        for token in (tampered, forged, str(expired)):
            self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
            self.assertEqual(self.api.get("/api/notes/").status_code, 401, token[:20])

    def test_token_signed_with_secret_key_is_accepted(self):
        """Хто знає SECRET_KEY, той підробить будь-який токен — тому ключ не може лежати в git для production."""
        forged = jwt.encode({"token_type": "access", "user_id": str(self.user.id), "exp": 9999999999, "jti": "x"},
                            settings.SECRET_KEY, algorithm="HS256")
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {forged}")
        self.assertEqual(self.api.get("/api/notes/").status_code, 200)

    def test_login_throttled_after_5_attempts(self):
        statuses = [self.obtain("wrong").status_code for _ in range(6)]
        self.assertEqual(statuses, [401] * 5 + [429])
        self.assertEqual(self.obtain().status_code, 429)         # навіть правильний пароль — зачекай


class PasswordTests(TestCase):
    def test_password_is_salted_hash(self):
        first = User.objects.create_user("a", password="Sup3r-secret!")
        second = User.objects.create_user("b", password="Sup3r-secret!")
        self.assertTrue(first.password.startswith("pbkdf2_sha256$"))
        self.assertNotEqual(first.password, second.password)       # той самий пароль — різна сіль
        self.assertNotIn("Sup3r-secret!", first.password)
        self.assertTrue(check_password("Sup3r-secret!", first.password))

    def test_password_reset_sends_link_without_revealing_accounts(self):
        User.objects.create_user("olena", email="olena@example.com", password="Sup3r-secret!")
        known = self.client.post("/accounts/password_reset/", {"email": "olena@example.com"})
        unknown = self.client.post("/accounts/password_reset/", {"email": "nobody@example.com"})
        self.assertEqual((known.status_code, unknown.status_code), (302, 302))    # однакова відповідь
        self.assertEqual(known["Location"], unknown["Location"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)
