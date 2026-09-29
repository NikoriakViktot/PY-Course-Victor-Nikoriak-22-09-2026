# Часті проблеми

## Не бачу нові уроки

```bash
git checkout main
git pull upstream main
```

Якщо команда каже, що `upstream` не налаштований — див. розділ «Додай upstream» у [Fork і Clone](github/fork_and_clone.md).

## Зробив домашку в main

```bash
git checkout -b homework-XX
git checkout main
git pull upstream main
```

## Colab: «Could not find … .ipynb» / «There was an error loading this notebook»

Кнопка Colab веде на шлях, де файлу вже немає (ноутбук перенесли або кнопка веде на інший репозиторій). Відкрий ноутбук через книгу курсу або заміни в адресі GitHub `https://github.com/` на `https://colab.research.google.com/github/`. Докладно: [Ноутбуки в Google Colab](colab.md).

## Permission denied

Найімовірніше, ти клонував repo викладача замість свого fork. Переклонуй свій fork — див. [Fork і Clone](github/fork_and_clone.md).

## Проблеми з SSH / GitHub просить пароль щоразу

Див. [GitHub → SSH-ключі](github/ssh_keys.md).

## 🧰 Git шпаргалка

```bash
git status
git branch
git checkout branch_name
git log --oneline
```

Повніша версія: [Git шпаргалка](../git-cheatsheet.md).

## 🆘 Якщо нічого не допомогло

Надішли викладачу:

- скрін помилки
- вивід `git status`
- вивід `git remote -v`

І проблема вирішиться швидко 🙂
