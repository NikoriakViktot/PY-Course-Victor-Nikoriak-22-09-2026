"""
selectors.py — SELECT queries only (no mutations).

Скопійовано з notes_project (там — детальна документація ORM оптимізацій, hello_app/selectors.py).

Auth lesson additions:
  - get_user_notes: includes group notes (Q filter)
  - get_user_shopping_lists: includes group lists
  - get_user_groups, get_group_members: group management selectors

Урок 44 — правила доступу в одному місці:
  - «хто що бачить» і «хто що змінює» — функції *_visible_to / *_owned_by, які повертають QuerySet;
    views (FBV і CBV) і API більше не будують свої фільтри `Q(user=...) | Q(...)` — лише беруть їх звідси;
  - M2M у фільтрі з OR (`shared_with`) дає по рядку на кожного, з ким поділено, → `.distinct()`;
  - що видно у списку, те відкривається й на сторінці: одна функція для обох.
"""
from django.contrib.auth.models import Group, User
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Prefetch, Sum
from django.utils import timezone

from .models import Note, Notebook, Tag, TodoList, TodoItem, ShopItem, ShoppingList, Reminder


# ── Правила доступу: хто що бачить і хто що змінює ─────────────────────────────

def notes_visible_to(user):
    """Свої нотатки + нотатки груп користувача (group — FK: дублікатів рядків немає)."""
    return Note.objects.filter(Q(user=user) | Q(group__in=user.groups.all()))


def notes_owned_by(user):
    """Змінювати й видаляти — лише автор."""
    return Note.objects.filter(user=user)


def notebooks_owned_by(user):
    return Notebook.objects.filter(user=user)


def tags_owned_by(user):
    return Tag.objects.filter(user=user)


def todo_lists_visible_to(user):
    """Свої + ті, якими поділились. shared_with — M2M: без distinct() список, поділений з двома,
    повернувся б двічі, і .get() кинув би MultipleObjectsReturned."""
    return TodoList.objects.filter(Q(user=user) | Q(shared_with=user)).distinct()


def todo_lists_owned_by(user):
    return TodoList.objects.filter(user=user)


def todo_items_visible_to(user):
    """Пункт видно (і його можна відмітити), якщо видно його список."""
    return TodoItem.objects.filter(todo_list__in=todo_lists_visible_to(user)).select_related('todo_list')


def todo_items_owned_by(user):
    return TodoItem.objects.filter(todo_list__user=user)


def shopping_lists_visible_to(user):
    """Свої + поділені + списки груп користувача — те саме правило для списку й сторінки списку."""
    return ShoppingList.objects.filter(
        Q(user=user) | Q(shared_with=user) | Q(group__in=user.groups.all())
    ).distinct()


def shopping_lists_owned_by(user):
    return ShoppingList.objects.filter(user=user)


def shop_items_visible_to(user):
    return ShopItem.objects.filter(
        shopping_list__in=shopping_lists_visible_to(user)
    ).select_related('shopping_list')


def shop_items_owned_by(user):
    return ShopItem.objects.filter(shopping_list__user=user)


def reminders_owned_by(user):
    return Reminder.objects.filter(note__user=user)


def groups_of(user):
    return user.groups.all()


def get_user_notes(user, *, archived=False, notebook=None, tag=None, search=None):
    qs = notes_visible_to(user).filter(
        is_archived=archived
    ).select_related('notebook', 'group').prefetch_related('tags')

    if notebook is not None:
        qs = qs.filter(notebook=notebook)
    if tag is not None:
        qs = qs.filter(tags=tag)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))

    return qs.order_by('-is_pinned', '-priority', '-updated_at')


def get_note_detail(user, note_id):
    return notes_visible_to(user).select_related(
        'notebook', 'user'
    ).prefetch_related(
        'tags',
        Prefetch(
            'reminders',
            queryset=Reminder.objects.filter(
                remind_at__gte=timezone.now()
            ).order_by('remind_at'),
            to_attr='upcoming_reminders'
        )
    ).get(id=note_id)


def get_pinned_notes(user, limit=5):
    return Note.objects.filter(
        user=user, is_pinned=True, is_archived=False
    ).select_related('notebook').prefetch_related('tags')[:limit]


def get_user_notebooks(user):
    return notebooks_owned_by(user).annotate(
        note_count=Count('notes', filter=Q(notes__is_archived=False))
    ).order_by('-is_default', 'title')


def notebooks_with_note_total(user):
    """Для сторінки видалення: скільки нотаток (і архівних теж) стануть «без записника»."""
    return notebooks_owned_by(user).annotate(note_count=Count('notes'))


def get_user_tags(user):
    return tags_owned_by(user).annotate(
        note_count=Count('notes', filter=Q(notes__is_archived=False))
    ).order_by('name')


def get_user_todo_lists(user):
    return TodoList.objects.filter(user=user).annotate(
        total_items=Count('items'),
        done_items=Count('items', filter=Q(items__is_done=True))
    ).order_by('is_completed', '-created_at')


def get_shared_todo_lists(user):
    return TodoList.objects.filter(shared_with=user).annotate(
        total_items=Count('items'),
        done_items=Count('items', filter=Q(items__is_done=True))
    ).select_related('user').order_by('is_completed', '-created_at')


def get_todo_list_detail(user, pk):
    try:
        return todo_lists_visible_to(user).prefetch_related('items', 'shared_with').get(pk=pk)
    except TodoList.DoesNotExist:
        return None


def get_user_shopping_lists(user):
    user_groups = user.groups.all()
    return ShoppingList.objects.filter(
        Q(user=user) | Q(group__in=user_groups)
    ).distinct().annotate(
        total_items=Count('items'),
        pending_items=Count('items', filter=Q(items__is_purchased=False))
    ).select_related('group').order_by('-created_at')


def get_shared_shopping_lists(user):
    return ShoppingList.objects.filter(shared_with=user).annotate(
        total_items=Count('items'),
        pending_items=Count('items', filter=Q(items__is_purchased=False))
    ).select_related('user').order_by('-created_at')


def get_shopping_list_detail(user, pk):
    """Список + орієнтовна сума некуплених позицій (рахує база, а не цикл у view)."""
    pending_cost = ExpressionWrapper(F('items__estimated_price') * F('items__quantity'),
                                     output_field=DecimalField(max_digits=18, decimal_places=4))
    try:
        return ShoppingList.objects.filter(
            pk__in=shopping_lists_visible_to(user).values('pk')
        ).annotate(
            pending_total=Sum(pending_cost, filter=Q(items__is_purchased=False))
        ).prefetch_related('items', 'shared_with').get(pk=pk)
    except ShoppingList.DoesNotExist:
        return None


def get_pending_reminders():
    return Reminder.objects.filter(
        is_sent=False, remind_at__lte=timezone.now()
    ).select_related('note__user')


# ── Group selectors ───────────────────────────────────────────────────────────

def get_user_groups(user):
    """Groups the user belongs to, annotated with member count."""
    return user.groups.annotate(
        member_count=Count('user')
    ).order_by('name')


def get_group_with_members(group_id, user):
    """Returns group if user is a member, else None."""
    try:
        return groups_of(user).prefetch_related('user_set').get(pk=group_id)
    except Group.DoesNotExist:
        return None


def get_group_member(group, user_pk):
    """Учасник групи за id або None (не будь-який користувач сайту)."""
    try:
        return group.user_set.get(pk=user_pk)
    except (User.DoesNotExist, ValueError):
        return None


def find_owned(queryset_fn, user, pk):
    """Об'єкт з QuerySet правила доступу або None: find_owned(tags_owned_by, user, '3')."""
    queryset = queryset_fn(user)
    try:
        return queryset.get(pk=int(pk))
    except (queryset.model.DoesNotExist, ValueError, TypeError):
        return None
