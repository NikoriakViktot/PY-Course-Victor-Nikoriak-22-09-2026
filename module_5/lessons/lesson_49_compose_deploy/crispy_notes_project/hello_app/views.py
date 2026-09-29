"""
views.py — HTTP шар (тільки request/response).

Урок 44 (крок 3 Django-книги: CRUD і архітектура) — рефакторинг views уроку 40:
  - нотатки, записники й теги — class-based views зі стартового `notes_project_cbv`
    (hello_app/views.py), адаптовані до цього проєкту:
    групи, `is_pinned`, «змінює лише автор»;
  - списки справ, покупок, нагадування й групи лишаються функціями — CBV не обов'язкові, обов'язкові тонкі views;
  - урок 45: group_chat — сторінка чату; повідомлення йдуть через WebSocket (consumers.py);
  - жодного `Model.objects` і жодного `Q(...)` у цьому файлі: «хто що бачить» і «хто що змінює» —
    функції selectors.*_visible_to / *_owned_by (одне правило для списку, сторінки, редагування й API).
    Перевіряє tests_architecture.py.
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Note
from .forms import (
    NoteForm, NotebookForm, TagForm,
    TodoListForm, TodoItemForm, ShoppingListForm, ShopItemForm,
    ReminderForm, ShareForm, GroupCreateForm, GroupAddMemberForm,
)
from . import selectors, services


# ─────────────────────────────────────────────────────────────────────────────
# МІКСИНИ: доступ до об'єктів — через selectors
# ─────────────────────────────────────────────────────────────────────────────

class SelectorQuerySetMixin:
    """QuerySet для Detail/Update/Delete бере функція selectors — `UserQuerySetMixin` стартового `notes_project_cbv`.

    Старий міксин робив `super().get_queryset().filter(user=self.request.user)` — правило доступу
    жило у view. Тут view лише каже, ЯКЕ правило: `selector = selectors.notes_visible_to`.
    get_object() шукає pk у цьому QuerySet → чужий об'єкт = 404.
    """
    selector = None

    def get_queryset(self):
        return type(self).selector(self.request.user)


class OwnerRequiredMixin(SelectorQuerySetMixin):
    """Бачити можна (група), змінювати — лише автор: повідомлення й повернення на сторінку об'єкта.

    MRO: NoteUpdateView → LoginRequiredMixin → OwnerRequiredMixin → SelectorQuerySetMixin → UpdateView.
    LoginRequiredMixin.dispatch() перевіряє вхід ПЕРШИМ, потім super().dispatch() → цей dispatch().
    """
    denied_message = 'Ти не можеш змінювати чужий об\'єкт.'
    denied_url = None              # куди повернути не-автора
    denied_url_with_pk = False     # True — на сторінку цього об'єкта (…_detail pk=…)

    def get_object(self, queryset=None):
        if not hasattr(self, '_object'):              # dispatch() і get()/post() — один запит до бази
            self._object = super().get_object(queryset)
        return self._object

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()                       # 404, якщо об'єкт навіть не видно
        if obj.user_id != request.user.id:
            messages.error(request, self.denied_message)
            if self.denied_url_with_pk:
                return redirect(self.denied_url, pk=obj.pk)
            return redirect(self.denied_url)
        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC VIEWS
# ─────────────────────────────────────────────────────────────────────────────

class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('hello_app:note_list')
        return render(request, 'hello_app/index.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('hello_app:note_list')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'✅ Акаунт «{user.username}» створено!')
            return redirect('hello_app:note_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# NOTE VIEWS (CBV)
# ─────────────────────────────────────────────────────────────────────────────

class NoteListView(LoginRequiredMixin, ListView):
    template_name = 'hello_app/note_list.html'
    context_object_name = 'notes'

    def get(self, request, *args, **kwargs):
        """Фільтри з ?q=&tag=&notebook= — один раз на запит (потрібні і в get_queryset, і в контексті).

        Саме в get(), а не в setup(): setup() виконується ДО dispatch(), тобто до перевірки
        LoginRequiredMixin, — анонім дійшов би до запиту в базу з AnonymousUser.
        """
        user = request.user
        self.search = request.GET.get('q', '').strip()
        self.active_tag = selectors.find_owned(selectors.tags_owned_by, user, request.GET.get('tag'))
        self.active_notebook = selectors.find_owned(selectors.notebooks_owned_by, user,
                                                    request.GET.get('notebook'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return selectors.get_user_notes(self.request.user, search=self.search or None,
                                        tag=self.active_tag, notebook=self.active_notebook)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            notebooks=selectors.get_user_notebooks(self.request.user),
            tags=selectors.get_user_tags(self.request.user),
            search=self.search, active_tag=self.active_tag, active_notebook=self.active_notebook,
        )
        return ctx


class NoteDetailView(LoginRequiredMixin, DetailView):
    template_name = 'hello_app/note_detail.html'
    context_object_name = 'note'

    def get_object(self, queryset=None):
        """Selector з Prefetch(to_attr='upcoming_reminders') — одна нотатка з найближчими нагадуваннями."""
        try:
            return selectors.get_note_detail(self.request.user, self.kwargs['pk'])
        except Note.DoesNotExist:
            raise Http404('Нотатку не знайдено')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reminder_form = ReminderForm()
        reminder_form.helper.form_action = reverse('hello_app:reminder_create', args=[self.object.pk])
        ctx['reminder_form'] = reminder_form
        return ctx


class NoteFormMixin:
    """NoteForm потребує user= (варіанти записників, тегів і груп — лише свої)."""
    form_class = NoteForm
    template_name = 'hello_app/note_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def note_fields(self, form, *, tags_default):
        tags = form.cleaned_data.get('tags')
        return {
            'title': form.cleaned_data['title'],
            'content': form.cleaned_data.get('content', ''),
            'priority': form.cleaned_data.get('priority', 1),
            'notebook': form.cleaned_data.get('notebook'),
            'is_pinned': form.cleaned_data.get('is_pinned', False),
            'group': form.cleaned_data.get('group'),
            'tag_ids': [t.id for t in tags] if tags else tags_default,
        }


class NoteCreateView(LoginRequiredMixin, NoteFormMixin, CreateView):
    extra_context = {'title': 'Нова нотатка', 'action': 'Створити'}

    def form_valid(self, form):
        """Не form.save(), а service: транзакція й перевірка тегів — у services.create_note."""
        note = services.create_note(user=self.request.user, **self.note_fields(form, tags_default=None))
        messages.success(self.request, f'✅ Нотатку "{note.title}" створено!')
        return redirect('hello_app:note_detail', pk=note.pk)


class NoteUpdateView(LoginRequiredMixin, OwnerRequiredMixin, NoteFormMixin, UpdateView):
    selector = selectors.notes_visible_to
    denied_message = 'Ти не можеш редагувати нотатку іншого користувача.'
    denied_url = 'hello_app:note_detail'
    denied_url_with_pk = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(note=self.object, title=f'Редагувати: {self.object.title}', action='Зберегти зміни')
        return ctx

    def form_valid(self, form):
        note = services.update_note(self.object, **self.note_fields(form, tags_default=[]))
        messages.success(self.request, f'✅ Нотатку "{note.title}" оновлено!')
        return redirect('hello_app:note_detail', pk=note.pk)


class NoteDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    selector = selectors.notes_visible_to
    template_name = 'hello_app/note_confirm_delete.html'
    context_object_name = 'note'
    denied_message = 'Ти не можеш видалити нотатку іншого користувача.'
    denied_url = 'hello_app:note_list'

    def form_valid(self, form):
        title = self.object.title
        services.delete_note(self.object)
        messages.warning(self.request, f'🗑️ Нотатку "{title}" видалено.')
        return redirect('hello_app:note_list')


# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK VIEWS (CBV)
# ─────────────────────────────────────────────────────────────────────────────

class NotebookListView(LoginRequiredMixin, ListView):
    template_name = 'hello_app/notebook_list.html'
    context_object_name = 'notebooks'

    def get_queryset(self):
        return selectors.get_user_notebooks(self.request.user)


class NotebookCreateView(LoginRequiredMixin, CreateView):
    form_class = NotebookForm
    template_name = 'hello_app/notebook_form.html'
    extra_context = {'title': 'Новий записник', 'action': 'Створити'}

    def form_valid(self, form):
        notebook = services.create_notebook(
            user=self.request.user,
            title=form.cleaned_data['title'],
            description=form.cleaned_data.get('description', ''),
            color=form.cleaned_data.get('color', '#4A90E2'),
            is_default=form.cleaned_data.get('is_default', False),
        )
        messages.success(self.request, f'Записник "{notebook.title}" створено!')
        return redirect('hello_app:notebook_list')


class NotebookUpdateView(LoginRequiredMixin, SelectorQuerySetMixin, UpdateView):
    selector = selectors.notebooks_owned_by
    form_class = NotebookForm
    template_name = 'hello_app/notebook_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(notebook=self.object, title=f'Редагувати: {self.object.title}', action='Зберегти')
        return ctx

    def form_valid(self, form):
        services.update_notebook(
            self.object,
            title=form.cleaned_data['title'],
            description=form.cleaned_data.get('description', ''),
            color=form.cleaned_data.get('color', '#4A90E2'),
            is_default=form.cleaned_data.get('is_default', False),
        )
        messages.success(self.request, f'Записник "{self.object.title}" оновлено!')
        return redirect('hello_app:notebook_list')


class NotebookDeleteView(LoginRequiredMixin, SelectorQuerySetMixin, DeleteView):
    selector = selectors.notebooks_with_note_total        # + note_count: скільки нотаток стануть «без записника»
    template_name = 'hello_app/notebook_confirm_delete.html'
    context_object_name = 'notebook'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['note_count'] = self.object.note_count
        return ctx

    def form_valid(self, form):
        title, note_count = self.object.title, self.object.note_count
        services.delete_notebook(self.object)
        messages.warning(self.request, f'Записник "{title}" видалено. {note_count} нотаток стали без записника.')
        return redirect('hello_app:notebook_list')


# ─────────────────────────────────────────────────────────────────────────────
# TAG VIEWS (CBV)
# ─────────────────────────────────────────────────────────────────────────────

class TagCreateView(LoginRequiredMixin, CreateView):
    form_class = TagForm
    template_name = 'hello_app/tag_form.html'
    extra_context = {'title': 'Новий тег', 'action': 'Створити'}

    def get_initial(self):
        return {'name': self.request.GET['name']} if self.request.GET.get('name') else {}

    def next_url(self):
        """Куди повернутись після створення — лише адреса цього ж сайту (інакше ?next= веде на чужий)."""
        target = self.request.GET.get('next') or self.request.POST.get('next')
        if target and url_has_allowed_host_and_scheme(target, allowed_hosts={self.request.get_host()},
                                                      require_https=self.request.is_secure()):
            return target
        return reverse('hello_app:note_create')

    def form_valid(self, form):
        tag, created = services.create_or_get_tag(
            user=self.request.user,
            name=form.cleaned_data['name'],
            color=form.cleaned_data.get('color', '#808080'),
        )
        if created:
            messages.success(self.request, f'✅ Тег "#{tag.name}" створено!')
        else:
            messages.info(self.request, f'ℹ️ Тег "#{tag.name}" вже існує.')
        return redirect(self.next_url())


# ─────────────────────────────────────────────────────────────────────────────
# TODO VIEWS (FBV, тонкі)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def todo_list_list(request):
    return render(request, 'hello_app/todo_list.html', {
        'todo_lists': selectors.get_user_todo_lists(request.user),
        'shared_lists': selectors.get_shared_todo_lists(request.user),
    })


@login_required
def todo_list_create(request):
    if request.method == 'POST':
        form = TodoListForm(request.POST)
        if form.is_valid():
            todo = services.create_todo_list(
                user=request.user,
                title=form.cleaned_data['title'],
                description=form.cleaned_data.get('description', ''),
            )
            messages.success(request, f'✅ Список «{todo.title}» створено!')
            return redirect('hello_app:todo_detail', pk=todo.pk)
    else:
        form = TodoListForm()
    return render(request, 'hello_app/todo_form.html', {
        'form': form, 'title': 'Новий список справ', 'action': 'Створити',
    })


@login_required
def todo_list_detail(request, pk):
    todo = selectors.get_todo_list_detail(request.user, pk)
    if todo is None:
        raise Http404
    return render(request, 'hello_app/todo_detail.html', {
        'todo': todo,
        'item_form': TodoItemForm(),
        'is_owner': todo.user == request.user,
    })


@login_required
def todo_list_edit(request, pk):
    todo = get_object_or_404(selectors.todo_lists_visible_to(request.user), pk=pk)
    if todo.user != request.user:
        messages.error(request, 'Ти не можеш редагувати список іншого користувача.')
        return redirect('hello_app:todo_detail', pk=pk)
    if request.method == 'POST':
        form = TodoListForm(request.POST, instance=todo)
        if form.is_valid():
            services.update_todo_list(
                todo,
                title=form.cleaned_data['title'],
                description=form.cleaned_data.get('description', ''),
            )
            messages.success(request, f'✅ Список «{todo.title}» оновлено!')
            return redirect('hello_app:todo_detail', pk=todo.pk)
    else:
        form = TodoListForm(instance=todo)
    return render(request, 'hello_app/todo_form.html', {
        'form': form, 'todo': todo, 'title': f'Редагувати: {todo.title}', 'action': 'Зберегти',
    })


@login_required
def todo_list_delete(request, pk):
    todo = get_object_or_404(selectors.todo_lists_visible_to(request.user), pk=pk)
    if todo.user != request.user:
        messages.error(request, 'Ти не можеш видалити список іншого користувача.')
        return redirect('hello_app:todo_list')
    if request.method == 'POST':
        title = todo.title
        services.delete_todo_list(todo)
        messages.warning(request, f'🗑️ Список «{title}» видалено.')
        return redirect('hello_app:todo_list')
    return render(request, 'hello_app/todo_confirm_delete.html', {'todo': todo})


@login_required
def todo_item_add(request, list_pk):
    todo = selectors.get_todo_list_detail(request.user, list_pk)
    if todo is None:
        raise Http404
    if request.method == 'POST':
        form = TodoItemForm(request.POST)
        if form.is_valid():
            services.add_todo_item(
                todo,
                text=form.cleaned_data['text'],
                due_date=form.cleaned_data.get('due_date'),
            )
    return redirect('hello_app:todo_detail', pk=list_pk)


@login_required
def todo_item_toggle(request, pk):
    item = get_object_or_404(selectors.todo_items_visible_to(request.user), pk=pk)
    if request.method == 'POST':
        services.toggle_todo_item(item)
    return redirect('hello_app:todo_detail', pk=item.todo_list_id)


@login_required
def todo_item_delete(request, pk):
    item = get_object_or_404(selectors.todo_items_owned_by(request.user), pk=pk)
    list_pk = item.todo_list_id
    if request.method == 'POST':
        services.delete_todo_item(item)
    return redirect('hello_app:todo_detail', pk=list_pk)


@login_required
def todo_list_share(request, pk):
    todo = get_object_or_404(selectors.todo_lists_owned_by(request.user), pk=pk)
    error = None
    if request.method == 'POST':
        form = ShareForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if request.POST.get('action') == 'remove':
                services.unshare_todo_list(todo, username)
                messages.success(request, f'Доступ для «{username}» скасовано.')
            else:
                ok, msg = services.share_todo_list(todo, username)
                if ok:
                    messages.success(request, f'✅ Список поділено з «{username}».')
                else:
                    error = msg
    else:
        form = ShareForm()
    return render(request, 'hello_app/share_form.html', {
        'form': form, 'obj': todo, 'obj_type': 'todo',
        'shared_with': todo.shared_with.all(), 'error': error,
    })


# ─────────────────────────────────────────────────────────────────────────────
# SHOPPING VIEWS (FBV, тонкі)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def shopping_list_list(request):
    return render(request, 'hello_app/shopping_list.html', {
        'shopping_lists': selectors.get_user_shopping_lists(request.user),
        'shared_lists': selectors.get_shared_shopping_lists(request.user),
    })


@login_required
def shopping_list_create(request):
    if request.method == 'POST':
        form = ShoppingListForm(request.POST, user=request.user)
        if form.is_valid():
            sl = services.create_shopping_list(
                user=request.user,
                title=form.cleaned_data['title'],
                store_name=form.cleaned_data.get('store_name', ''),
                group=form.cleaned_data.get('group'),
            )
            messages.success(request, f'✅ Список покупок «{sl.title}» створено!')
            return redirect('hello_app:shopping_detail', pk=sl.pk)
    else:
        form = ShoppingListForm(user=request.user)
    return render(request, 'hello_app/shopping_form.html', {
        'form': form, 'title': 'Новий список покупок', 'action': 'Створити',
    })


@login_required
def shopping_list_detail(request, pk):
    sl = selectors.get_shopping_list_detail(request.user, pk)
    if sl is None:
        raise Http404
    return render(request, 'hello_app/shopping_detail.html', {
        'sl': sl,
        'item_form': ShopItemForm(),
        'total_price': sl.pending_total,             # суму рахує selector (SUM у базі)
        'is_owner': sl.user == request.user,
    })


@login_required
def shopping_list_edit(request, pk):
    sl = get_object_or_404(selectors.shopping_lists_visible_to(request.user), pk=pk)
    if sl.user != request.user:
        messages.error(request, 'Ти не можеш редагувати список іншого користувача.')
        return redirect('hello_app:shopping_detail', pk=pk)
    if request.method == 'POST':
        form = ShoppingListForm(request.POST, instance=sl, user=request.user)
        if form.is_valid():
            services.update_shopping_list(
                sl,
                title=form.cleaned_data['title'],
                store_name=form.cleaned_data.get('store_name', ''),
                group=form.cleaned_data.get('group'),
            )
            messages.success(request, f'✅ Список «{sl.title}» оновлено!')
            return redirect('hello_app:shopping_detail', pk=sl.pk)
    else:
        form = ShoppingListForm(instance=sl, user=request.user)
    return render(request, 'hello_app/shopping_form.html', {
        'form': form, 'sl': sl, 'title': f'Редагувати: {sl.title}', 'action': 'Зберегти',
    })


@login_required
def shopping_list_delete(request, pk):
    sl = get_object_or_404(selectors.shopping_lists_visible_to(request.user), pk=pk)
    if sl.user != request.user:
        messages.error(request, 'Ти не можеш видалити список іншого користувача.')
        return redirect('hello_app:shopping_list')
    if request.method == 'POST':
        title = sl.title
        services.delete_shopping_list(sl)
        messages.warning(request, f'🗑️ Список «{title}» видалено.')
        return redirect('hello_app:shopping_list')
    return render(request, 'hello_app/shopping_confirm_delete.html', {'sl': sl})


@login_required
def shop_item_add(request, list_pk):
    sl = selectors.get_shopping_list_detail(request.user, list_pk)
    if sl is None:
        raise Http404
    if request.method == 'POST':
        form = ShopItemForm(request.POST)
        if form.is_valid():
            services.add_shop_item(
                sl,
                name=form.cleaned_data['name'],
                quantity=form.cleaned_data.get('quantity', 1),
                unit=form.cleaned_data.get('unit', 'шт'),
                estimated_price=form.cleaned_data.get('estimated_price'),
            )
    return redirect('hello_app:shopping_detail', pk=list_pk)


@login_required
def shop_item_toggle(request, pk):
    item = get_object_or_404(selectors.shop_items_visible_to(request.user), pk=pk)
    if request.method == 'POST':
        services.toggle_shop_item_purchased(item)
    return redirect('hello_app:shopping_detail', pk=item.shopping_list_id)


@login_required
def shop_item_delete(request, pk):
    item = get_object_or_404(selectors.shop_items_owned_by(request.user), pk=pk)
    list_pk = item.shopping_list_id
    if request.method == 'POST':
        services.delete_shop_item(item)
    return redirect('hello_app:shopping_detail', pk=list_pk)


@login_required
def shopping_list_share(request, pk):
    sl = get_object_or_404(selectors.shopping_lists_owned_by(request.user), pk=pk)
    error = None
    if request.method == 'POST':
        form = ShareForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if request.POST.get('action') == 'remove':
                services.unshare_shopping_list(sl, username)
                messages.success(request, f'Доступ для «{username}» скасовано.')
            else:
                ok, msg = services.share_shopping_list(sl, username)
                if ok:
                    messages.success(request, f'✅ Список поділено з «{username}».')
                else:
                    error = msg
    else:
        form = ShareForm()
    return render(request, 'hello_app/share_form.html', {
        'form': form, 'obj': sl, 'obj_type': 'shopping',
        'shared_with': sl.shared_with.all(), 'error': error,
    })


# ─────────────────────────────────────────────────────────────────────────────
# REMINDER VIEWS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def reminder_create(request, note_pk):
    note = get_object_or_404(selectors.notes_owned_by(request.user), pk=note_pk)
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            services.create_reminder(
                note=note,
                remind_at=form.cleaned_data['remind_at'],
                message=form.cleaned_data.get('message', ''),
                repeat_pattern=form.cleaned_data.get('repeat_pattern', 'none'),
            )
            messages.success(request, '✅ Нагадування додано!')
    return redirect('hello_app:note_detail', pk=note_pk)


@login_required
def reminder_delete(request, pk):
    reminder = get_object_or_404(selectors.reminders_owned_by(request.user), pk=pk)
    note_pk = reminder.note_id
    if request.method == 'POST':
        services.delete_reminder(reminder)
        messages.warning(request, '🗑️ Нагадування видалено.')
    return redirect('hello_app:note_detail', pk=note_pk)


# ─────────────────────────────────────────────────────────────────────────────
# GROUP VIEWS — Django built-in Group model
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def group_list(request):
    return render(request, 'hello_app/group_list.html', {'groups': selectors.get_user_groups(request.user)})


@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = services.create_group(
                name=form.cleaned_data['name'],
                creator=request.user,
            )
            messages.success(request, f'✅ Групу «{group.name}» створено! Ви перший учасник.')
            return redirect('hello_app:group_detail', pk=group.pk)
    else:
        form = GroupCreateForm()
    return render(request, 'hello_app/group_form.html', {
        'form': form, 'title': 'Нова група', 'action': 'Створити',
    })


@login_required
def group_detail(request, pk):
    group = selectors.get_group_with_members(pk, request.user)
    if group is None:
        raise Http404('Групу не знайдено або у вас немає доступу.')

    add_form = GroupAddMemberForm()
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            add_form = GroupAddMemberForm(request.POST)
            if add_form.is_valid():
                ok, msg = services.add_user_to_group(group, add_form.cleaned_data['username'])
                if ok:
                    messages.success(request, '✅ Користувача додано до групи.')
                    return redirect('hello_app:group_detail', pk=pk)
                error = msg
        elif action == 'remove':
            target = selectors.get_group_member(group, request.POST.get('user_pk'))
            if target == request.user:
                messages.warning(request, 'Вийти з групи можна через кнопку «Покинути групу».')
            elif target is not None:
                services.remove_user_from_group(group, target)
                messages.success(request, f'Користувача «{target.username}» видалено з групи.')
            return redirect('hello_app:group_detail', pk=pk)
        elif action == 'leave':
            services.remove_user_from_group(group, request.user)
            messages.info(request, f'Ви покинули групу «{group.name}».')
            return redirect('hello_app:group_list')

    return render(request, 'hello_app/group_detail.html', {
        'group': group,
        'members': group.user_set.all(),
        'add_form': add_form,
        'error': error,
    })


@login_required
def group_delete(request, pk):
    group = selectors.get_group_with_members(pk, request.user)
    if group is None:
        raise Http404('Групу не знайдено або у вас немає доступу.')
    if request.method == 'POST':
        name = group.name
        services.delete_group(group)
        messages.warning(request, f'Групу «{name}» видалено.')
        return redirect('hello_app:group_list')
    return render(request, 'hello_app/group_confirm_delete.html', {'group': group})


@login_required
def group_chat(request, pk):
    """HTTP: сторінка чату групи (HTML + JS). Сам чат — WebSocket: hello_app/consumers.py (урок 45).

    З notes_chat_app; доступ — той самий selector, що в group_detail (урок 44): не учасник — 404.
    """
    group = selectors.get_group_with_members(pk, request.user)
    if group is None:
        raise Http404('Групу не знайдено або у вас немає доступу.')
    return render(request, 'hello_app/group_chat.html', {'group': group})
