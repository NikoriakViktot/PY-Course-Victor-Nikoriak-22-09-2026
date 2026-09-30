from django.db import models


class Note(models.Model):
    PRIORITY_CHOICES = [(1, "Низький"), (2, "Звичайний"), (3, "Високий"), (4, "Терміновий")]

    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Текст", blank=True)
    is_pinned = models.BooleanField("Закріплена", default=False)
    priority = models.PositiveSmallIntegerField("Пріоритет", choices=PRIORITY_CHOICES, default=2)
    created_at = models.DateTimeField("Створено", auto_now_add=True)

    class Meta:
        verbose_name = "нотатка"
        verbose_name_plural = "нотатки"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title
