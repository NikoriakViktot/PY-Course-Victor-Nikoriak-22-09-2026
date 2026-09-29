# Bistro Analytics — дашборд ресторану

Міні-проєкт до [уроку 7 «Функції»](../../../../docs/modules/m1/lesson_07.md). Той самий підхід, що в уроці: логіка — окремими чистими функціями, а інтерфейс лише викликає їх.

Дашборд показує 244 реальні чеки ресторану (набір `tips` з seaborn). Фільтри на бічній панелі: день, зміна, курці, стать, кількість гостей, сума рахунку. Після кожної зміни перераховуються KPI, шість графіків і таблиці.

## Запуск

```bash
pip install streamlit plotly seaborn
cd module_1/lessons/lesson_07_functions/restaurant_dashboard
streamlit run app.py
```

Браузер відкриє `http://localhost:8501`. Під час першого запуску seaborn завантажує набір `tips` з інтернету.

## Файли

| Файл | Що всередині |
|---|---|
| `pipeline.py` | дані й чисті функції: predicates `pred_*` і `apply_filters`, transformers `enrich_order` / `enrich_all`, reducers `calc_kpis`, `group_by_*`, `top_by_tip_pct`, оркестратор `run_pipeline` |
| `app.py` | інтерфейс на Streamlit: фільтри → `run_pipeline(...)` → KPI, графіки, таблиці |
| `test_pipeline.py` | перевірки функцій на маленькому наборі чеків: `python test_pipeline.py` |

Докладний розбір алгоритму зі схемами — [`restaurant_dashboard_alg.md`](../restaurant_dashboard_alg.md).

## Як це пов'язано з уроком 7

```text
filtered = apply_filters(orders, days, times, ...)   # predicates: хто входить?
enriched = enrich_all(filtered)                      # transformer: яка форма?
kpis     = calc_kpis(enriched)                       # reducer: яка відповідь?
```

Streamlit після кожної зміни фільтра перезапускає `app.py` згори донизу. Тому весь інтерфейс — це одна «рамка» навколо виклику `run_pipeline(...)`. Функції в `pipeline.py` нічого не малюють і не друкують: їх можна перевірити окремо (`test_pipeline.py`) і підключити до іншого інтерфейсу — ноутбука, вебсторінки чи Telegram-бота.

## Спробуй сам

1. Додай фільтр «лише чеки, де чайові більше за N %»: новий predicate у `pipeline.py`, параметр у `apply_filters`, слайдер у `app.py`.
2. Додай KPI «середня кількість гостей» — значення вже є в `calc_kpis`.
3. Напиши тест для свого predicate в `test_pipeline.py`.
