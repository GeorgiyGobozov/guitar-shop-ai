# StringTheory — ИС гитарного магазина с ML-классификацией обращений

Учебный проект по дисциплине **«Проектирование и интеграция интеллектуальных информационных систем»**.
Лабораторная работа №1: *«Интеллектуальный поиск и классификация объектов информационной системы (ML-классификация)»*.

Информационная система интернет-магазина гитар **StringTheory**: принимает обращения клиентов, хранит их в реляционной БД и автоматически размечает по трём осям с помощью внешнего ML-сервиса.

---

## Содержание

- [Что делает система](#что-делает-система)
- [Архитектура](#архитектура)
- [Стек](#стек)
- [Структура проекта](#структура-проекта)
- [Быстрый старт (Docker)](#быстрый-старт-docker)
- [Запуск без Docker](#запуск-без-docker)
- [API](#api)
- [ML-модель](#ml-модель)
- [Данные](#данные)
- [Проверка работы](#проверка-работы)
- [Отказоустойчивость](#отказоустойчивость)
- [Ограничения и направления развития](#ограничения-и-направления-развития)

---

## Что делает система

**Предметная область** — интернет-магазин гитар. В системе регистрируются клиентские обращения: вопросы по товарам, проблемы с доставкой, оплатой, гарантией.

**Возможности:**

| Возможность | Реализация |
|---|---|
| Регистрация обращений с текстовым описанием | `POST /api/tickets`, форма в UI |
| Хранение в реляционной БД | PostgreSQL, таблица `tickets` |
| Каталог товаров магазина | PostgreSQL, таблица `products` |
| Автоматическая классификация по 3 осям | ML-сервис `POST /predict` |
| Просмотр списка обращений | `GET /api/tickets`, UI |
| Фильтр по ML-категории | `GET /api/tickets?category=...`, выпадашка в UI |
| Назначение исполнителя | `PATCH /api/tickets/{id}/assign` |
| Изменение статуса `NEW → IN_PROGRESS → CLOSED` | `assign` / `close` |
| Веб-интерфейс оператора | `backend/static/index.html` |
| Мониторинг здоровья сервисов | `/health`, `/ml-health` |
| Работа при недоступном ML | graceful degradation |

**Три оси ML-классификации:**

| Ось | Классы |
|---|---|
| `category` | `electric`, `acoustic`, `classical`, `bass`, `accessories`, `delivery`, `payment`, `warranty` |
| `priority` | `low`, `medium`, `high` |
| `problem_type` | `product_info`, `order_issue`, `technical_problem`, `refund`, `complaint` |

---

## Архитектура

Три независимых компонента. ML — **отдельный микросервис**, не модуль внутри backend'а.

```
┌─────────────────────────────────────────────────────────────┐
│                    Клиент (браузер / curl)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND  (порт 8080) — ядро ИС                 │
│  • REST API (FastAPI)          — CRUD тикетов               │
│  • Бизнес-логика (service.py)  — создание, назначение       │
│  • ORM (SQLAlchemy)            — работа с БД                │
│  • ML-клиент (ml_client.py)    — вызов ML по HTTP           │
│  • Раздача статики             — UI оператора               │
└────────┬─────────────────────────────────────┬──────────────┘
         │ SQL                                 │ HTTP
         ▼                                     ▼
┌────────────────────┐              ┌─────────────────────────┐
│   PostgreSQL       │              │  ML-SERVICE (порт 8000) │
│  • tickets         │              │  • TF-IDF + LogReg      │
│  • products        │              │  • 3 классификатора     │
│                    │              │  • POST /predict        │
└────────────────────┘              └─────────────────────────┘
```

**Поток данных при создании обращения:**

```
Клиент
  → POST /api/tickets
  → backend: создать объект Ticket
  → backend: HTTP POST → ml-service /predict
  → ml-service: TF-IDF → LogReg → {category, priority, problem_type}
  → backend: заполнить ml_* поля, сохранить в PostgreSQL
  → ответ JSON с ML-метками
  → UI: рендер карточки с бейджами
```

---

## Стек

| Слой | Технология |
|---|---|
| БД | PostgreSQL 16 |
| ML-сервис | Python 3.11, FastAPI, scikit-learn, pandas |
| Backend | Python 3.11, FastAPI, SQLAlchemy, httpx |
| UI | HTML + Tailwind CSS (CDN) + vanilla JS |
| Контейнеризация | Docker, Docker Compose |

---

## Структура проекта

```
guitar-shop-ai/
├── docker-compose.yml
├── README.md
├── .gitignore
├── db/
│   └── init.sql                    # схема БД + seed товаров
├── ml-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── generate_dataset.py         # генератор обучающей выборки
│   ├── data/
│   │   └── training_data.csv       # создаётся автоматически
│   ├── model.py                    # TicketClassifier (TF-IDF + LogReg)
│   ├── train.py                    # обучение, метрики, сохранение .joblib
│   ├── schemas.py                  # Pydantic-схемы запроса/ответа
│   └── app.py                      # FastAPI, /predict, /health
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    ├── .env                        # DATABASE_URL, ML_SERVICE_URL
    ├── database.py                 # SQLAlchemy engine, session
    ├── models.py                   # ORM-модель Ticket
    ├── schemas.py                  # Pydantic-схемы
    ├── ml_client.py                # HTTP-клиент ML-сервиса
    ├── service.py                  # create_ticket с ML-разметкой
    ├── main.py                     # FastAPI, REST-ручки
    └── static/
        └── index.html              # UI оператора
```

---

## Быстрый старт (Docker)

**Требования:** Docker Desktop запущен.

```bash
docker compose up --build
```

Через 20–40 секунд:

- **UI оператора:** http://localhost:8080/
- **ML-сервис:** http://localhost:8000/health
- **PostgreSQL:** `localhost:5432`, БД `stringtheory`, юзер `shop` / пароль `shop`

Остановка:

```bash
docker compose down          # остановить контейнеры, сохранить данные БД
docker compose down -v       # остановить и удалить volume с БД
```

Полная пересборка ML (например, после правки датасета):

```bash
docker compose build --no-cache ml-service
docker compose up
```

---

## Запуск без Docker

### 1. PostgreSQL

```bash
docker compose up -d postgres
```

### 2. ML-сервис

```bash
cd ml-service
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python generate_dataset.py          # сгенерировать data/training_data.csv
python train.py                     # обучить, сохранить artifacts/*.joblib
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

UI: http://localhost:8080/

---

## API

### Backend (`:8080`)

| Метод | URL | Описание |
|---|---|---|
| `GET` | `/` | UI оператора |
| `GET` | `/health` | статус backend |
| `GET` | `/ml-health` | статус ML-сервиса (проксируется) |
| `POST` | `/api/tickets` | создать обращение (с ML-разметкой) |
| `GET` | `/api/tickets` | список всех обращений |
| `GET` | `/api/tickets?category=electric` | фильтр по ML-категории |
| `GET` | `/api/tickets/{id}` | одно обращение |
| `PATCH` | `/api/tickets/{id}/assign?assignee=Пётр` | назначить исполнителя |
| `PATCH` | `/api/tickets/{id}/close` | закрыть обращение |

**Пример `POST /api/tickets`:**

```bash
curl -X POST http://localhost:8080/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Иван",
    "customer_email": "ivan@example.com",
    "subject": "Проблема с комбиком",
    "description": "Купил электрогитару Fender, при подключении к комбику идёт сильный фон и хрип."
  }'
```

Ответ:

```json
{
  "id": 1,
  "customer_name": "Иван",
  "customer_email": "ivan@example.com",
  "subject": "Проблема с комбиком",
  "description": "Купил электрогитару Fender, при подключении к комбику идёт сильный фон и хрип.",
  "ml_category": "electric",
  "ml_priority": "high",
  "ml_problem_type": "technical_problem",
  "ml_confidence": 0.78,
  "status": "NEW",
  "assignee": null,
  "created_at": "2026-10-04T17:11:26"
}
```

### ML-сервис (`:8000`)

| Метод | URL | Описание |
|---|---|---|
| `GET` | `/health` | статус + загружена ли модель |
| `POST` | `/predict` | классифицировать текст |

**Пример `POST /predict`:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Бас Ibanez SR300E, активный темброблок хрипит на репетиции"}'
```

Ответ:

```json
{
  "category":     {"label": "bass",              "confidence": 0.85},
  "priority":     {"label": "high",              "confidence": 0.72},
  "problem_type": {"label": "technical_problem", "confidence": 0.91}
}
```

---

## ML-модель

**Подход:** мульти-таргетная классификация — три независимых пайплайна, по одному на каждый таргет.

**Признаки** (`sklearn.pipeline.FeatureUnion`):

| Компонент | Параметры | Зачем |
|---|---|---|
| Слово-ngram'ы | `analyzer="word"`, `ngram_range=(1, 2)`, `sublinear_tf=True` | Базовые смысловые признаки |
| Символьные ngram'ы | `analyzer="char_wb"`, `ngram_range=(3, 5)`, `sublinear_tf=True` | Устойчивость к морфологии русского |

**Классификатор:** `LogisticRegression(max_iter=2000, class_weight="balanced", C=3.0, solver="liblinear")`.

**Предобработка** (`preprocess`): приведение к нижнему регистру, удаление пунктуации, схлопывание пробелов.

**Обучение:**

```bash
cd ml-service
python generate_dataset.py    # создать data/training_data.csv (~600 строк)
python train.py               # обучить 3 модели, вывести метрики, сохранить .joblib
```

`train.py` выводит `classification_report` по каждому таргету — accuracy, precision, recall, F1.

**Типичные метрики** на сгенерированной выборке:

| Таргет | Accuracy |
|---|---|
| `category` | 0.85–0.95 |
| `priority` | 0.70–0.85 |
| `problem_type` | 0.85–0.95 |

---

## Данные

Обучающая выборка **генерируется программно** скриптом `ml-service/generate_dataset.py`.

- Шаблонные конструкции с подстановкой брендов, моделей, симптомов, городов.
- 8 категорий × 5 типов проблем × 3 приоритета.
- Дедупликация по тексту.
- Формат CSV: `text,category,priority,problem_type`, все поля в кавычках (`QUOTE_ALL`).

Скрипт запускается автоматически при сборке Docker-образа ML-сервиса:

```dockerfile
RUN python generate_dataset.py && python train.py
```

**Почему генератор, а не статический CSV:** ручной CSV ломается на запятых внутри текстов, тяжело балансируется по классам и не масштабируется. Генератор даёт сбалансированную выборку нужного объёма и легко расширяется.

---

## Проверка работы

### 1. UI

Открыть http://localhost:8080/. В шапке — индикаторы `● backend · ● ml` (оба должны быть зелёными). Форма слева, список обращений справа.

### 2. Прогнать тестовые кейсы

Сохранить как `test.ps1` и запустить `.\test.ps1`:

```powershell
$cases = @(
    @{ name = "electric/комбик";     text = "Купил электрогитару Fender, при подключении к комбику идёт сильный фон и хрип." },
    @{ name = "electric/для металла";text = "Посоветуйте электрогитару для металла до 50000 рублей" },
    @{ name = "acoustic/дребезг";    text = "Акустика Yamaha F310 дребезжит струна при игре" },
    @{ name = "classical/ребёнок";   text = "Какая классическая гитара подойдёт ребёнку 8 лет?" },
    @{ name = "bass/темброблок";     text = "Бас Ibanez SR300E, активный темброблок хрипит на репетиции" },
    @{ name = "accessories/заказ";   text = "Где мой заказ струн Elixir? Уже неделю не приходит" },
    @{ name = "delivery/сроки";      text = "Сколько дней идёт доставка в Новосибирск?" },
    @{ name = "payment/двойное";     text = "При оплате картой деньги списались дважды, верните разницу" },
    @{ name = "warranty/колок";      text = "Сломался колок на электрогитаре, гарантийный случай?" },
    @{ name = "complaint/царапина";  text = "Заказал Fender Stratocaster, пришёл с царапиной на деке и в мятой коробке" }
)

foreach ($c in $cases) {
    $body = @{ text = $c.text } | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
    Write-Host ("{0,-22} → {1,-12} / {2,-8} / {3,-18} (conf {4:P0})" -f `
        $c.name, $r.category.label, $r.priority.label, $r.problem_type.label, $r.category.confidence)
}
```

Ожидаемый вывод — таблица предсказаний по всем 8 категориям.

### 3. Заглянуть в БД

```bash
docker compose exec postgres psql -U shop -d stringtheory -c \
  "SELECT id, subject, ml_category, ml_priority, ml_problem_type, status FROM tickets ORDER BY id;"
```

### 4. Логи

```bash
docker compose logs -f ml-service    # метрики обучения
docker compose logs -f backend       # запросы и ошибки ML-клиента
docker compose logs -f postgres      # SQL
```

---

## Отказоустойчивость

**Ключевая демонстрация того, что ML — отдельный компонент ИС.**

Сценарий:

```bash
docker compose stop ml-service
```

Создать обращение через UI или `POST /api/tickets`. Тикет **всё равно создастся**, но с пустыми ML-полями:

```json
{
  "id": 2,
  "ml_category": null,
  "ml_priority": null,
  "ml_problem_type": null,
  "ml_confidence": null
}
```

В логах backend появится `[ml_client] ML-сервис недоступен: ...`.

Вернуть ML:

```bash
docker compose start ml-service
```

Следующее обращение снова получит ML-метки.

**Реализация:** `MlClient.predict()` ловит любое исключение и возвращает `None`; `service.create_ticket()` проверяет `if pred:` перед заполнением `ml_*` полей. Backend не знает, доступен ли ML — он просто продолжает работать.

---

## Ограничения и направления развития

**Чего в системе нет:**

- Аутентификации и авторизации — любой может создавать и закрывать тикеты.
- Разграничения ролей (оператор / клиент / администратор).
- Ручного редактирования ML-меток через UI — оператор не может исправить ошибку модели.
- Feedback loop — исправления оператора не попадают в обучающую выборку.
- Порога автоматизации — тикет с `confidence=0.3` уходит в БД так же, как `confidence=0.95`.
- Асинхронной обработки — backend ждёт ML синхронно (timeout 3 с).
- Полнотекстового поиска по обращениям.
- Связи `ticket ↔ product` — обращение не привязано к конкретному товару.

**Направления развития:**

1. **Эмбеддинги вместо TF-IDF** — `sentence-transformers` / `rubert-tiny2` дают заметно лучше на маленьких выборках и понимают морфологию без char-ngram'ов.
2. **Активное обучение** — оператор правит `ml_category` через UI, правка сохраняется и уходит в датасет для следующего переобучения.
3. **Порог автоматизации** — при `confidence < 0.5` тикет помечается флагом «требует ревью».
4. **Асинхронная классификация** — вынести ML-вызов в очередь (Celery / RabbitMQ), backend не блокируется.
5. **Мониторинг дрейфа** — сравнение распределений предсказаний по неделям, алерт при деградации.
6. **A/B-тестирование моделей** — держать две версии ML-сервиса, роутить трафик 90/10.
7. **Связь обращений с товарами** — привязка `ticket.product_id` для аналитики проблемных партий.
8. **Роли и аутентификация** — JWT + RBAC.
