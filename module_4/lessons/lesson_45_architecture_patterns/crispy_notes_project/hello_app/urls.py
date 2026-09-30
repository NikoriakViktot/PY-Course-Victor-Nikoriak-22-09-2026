"""Маршрути застосунку. Урок 44: нотатки, записники й теги — CBV (`.as_view()`), імена маршрутів ті самі."""
from django.urls import path
from . import views

app_name = "hello_app"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    # ── Notes (main CRUD) ──────────────────────────────────────────────────────
    path('notes/', views.NoteListView.as_view(), name='note_list'),
    path('notes/new/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('notes/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),

    # ── Notebooks ──────────────────────────────────────────────────────────────
    path('notebooks/', views.NotebookListView.as_view(), name='notebook_list'),
    path('notebooks/new/', views.NotebookCreateView.as_view(), name='notebook_create'),
    path('notebooks/<int:pk>/edit/', views.NotebookUpdateView.as_view(), name='notebook_edit'),
    path('notebooks/<int:pk>/delete/', views.NotebookDeleteView.as_view(), name='notebook_delete'),

    # ── Tags ───────────────────────────────────────────────────────────────────
    path('tags/new/', views.TagCreateView.as_view(), name='tag_create'),

    # ── Registration ───────────────────────────────────────────────────────────
    path('register/', views.register, name='register'),

    # ── TodoList ───────────────────────────────────────────────────────────────
    path('todo/',                             views.todo_list_list,    name='todo_list'),
    path('todo/new/',                         views.todo_list_create,  name='todo_create'),
    path('todo/<int:pk>/',                    views.todo_list_detail,  name='todo_detail'),
    path('todo/<int:pk>/edit/',               views.todo_list_edit,    name='todo_edit'),
    path('todo/<int:pk>/delete/',             views.todo_list_delete,  name='todo_delete'),
    path('todo/<int:pk>/share/',              views.todo_list_share,   name='todo_share'),
    path('todo/<int:list_pk>/items/add/',     views.todo_item_add,     name='todo_item_add'),
    path('todo/items/<int:pk>/toggle/',       views.todo_item_toggle,  name='todo_item_toggle'),
    path('todo/items/<int:pk>/delete/',       views.todo_item_delete,  name='todo_item_delete'),

    # ── ShoppingList ────────────────────────────────────────────────────────────
    path('shopping/',                              views.shopping_list_list,    name='shopping_list'),
    path('shopping/new/',                          views.shopping_list_create,  name='shopping_create'),
    path('shopping/<int:pk>/',                     views.shopping_list_detail,  name='shopping_detail'),
    path('shopping/<int:pk>/edit/',                views.shopping_list_edit,    name='shopping_edit'),
    path('shopping/<int:pk>/delete/',              views.shopping_list_delete,  name='shopping_delete'),
    path('shopping/<int:pk>/share/',               views.shopping_list_share,   name='shopping_share'),
    path('shopping/<int:list_pk>/items/add/',      views.shop_item_add,         name='shop_item_add'),
    path('shopping/items/<int:pk>/toggle/',        views.shop_item_toggle,      name='shop_item_toggle'),
    path('shopping/items/<int:pk>/delete/',        views.shop_item_delete,      name='shop_item_delete'),

    # ── Reminders ──────────────────────────────────────────────────────────────
    path('notes/<int:note_pk>/reminders/add/', views.reminder_create, name='reminder_create'),
    path('reminders/<int:pk>/delete/',         views.reminder_delete,  name='reminder_delete'),

    # ── Groups ─────────────────────────────────────────────────────────────────
    path('groups/',                  views.group_list,    name='group_list'),
    path('groups/new/',              views.group_create,  name='group_create'),
    path('groups/<int:pk>/',         views.group_detail,  name='group_detail'),
    path('groups/<int:pk>/delete/',  views.group_delete,  name='group_delete'),
]
