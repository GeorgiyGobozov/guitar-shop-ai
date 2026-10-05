"""generate_dataset.py — генерирует сбалансированный data/training_data.csv.

Запускается автоматически в Dockerfile перед train.py.
Локально:  python generate_dataset.py
"""
import csv
import random
from pathlib import Path
from collections import Counter

random.seed(42)
OUT = Path(__file__).parent / "data" / "training_data.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

# ---------- Словари ----------
ELECTRIC_BRANDS = ["Fender", "Gibson", "Ibanez", "Schecter", "PRS",
                   "Epiphone", "Squier", "Jackson", "ESP", "Cort", "Charvel"]
ELECTRIC_MODELS = ["Stratocaster", "Telecaster", "Les Paul", "SG", "RG",
                   "Superstrat", "Mustang", "Jazzmaster", "Explorer",
                   "Flying V", "Dinky", "SoCal", "American Pro"]
ACOUSTIC_BRANDS = ["Yamaha", "Taylor", "Martin", "Takamine", "Fender",
                   "Epiphone", "Guild", "Sigma", "Alvarez"]
ACOUSTIC_MODELS = ["F310", "114e", "D-28", "CD-60", "GD-10", "FG800",
                   "DR-100", "D-15", "D-18", "D-35"]
CLASSICAL_BRANDS = ["Cordoba", "Alhambra", "Yamaha", "Admira",
                    "Martinez", "La Mancha"]
CLASSICAL_MODELS = ["C5", "C7", "Iberia", "3C", "FC-10", "1C",
                    "Estudio", "C40"]
BASS_BRANDS = ["Ibanez", "Fender", "Music Man", "Warwick", "Squier",
               "Yamaha", "Cort", "Schecter"]
BASS_MODELS = ["SR300E", "Precision", "Jazz Bass", "StingRay",
               "Corvette", "RBX170", "B4", "Action", "TRBX"]
ACC_BRANDS = ["Dunlop", "Ernie Ball", "D'Addario", "Elixir", "Fender",
              "Planet Waves", "Jim Dunlop", "Snark", "Korg"]
ACC_ITEMS = ["Tortex", "Slinky", "EXL110", "Nanoweb", "Polyweb",
             "каподастр", "чехол", "тюнер", "медиаторы", "ремень",
             "кабель", "стойка", "струны"]

SYMPTOMS = ["фонит", "хрипит", "трещит", "гудит", "шумит", "щёлкает",
            "не строит", "хрустит", "шипит", "дребезжит", "скрипит"]
PARTS = ["звукосниматель", "переключатель", "потенциометр", "бридж",
         "колок", "джек", "анкер", "флойд", "тумблер", "порожек",
         "ручка громкости", "ручка тона", "бриджевый датчик",
         "нековый датчик", "предусилитель"]
CITIES = ["Москву", "Казань", "Санкт-Петербург", "Новосибирск",
          "Екатеринбург", "Краснодар", "Сочи", "Нижний Новгород",
          "Самару", "Уфу", "Пермь", "Воронеж"]
GENRES = ["металла", "рока", "джаза", "блюза", "фанка",
          "инди", "панка", "фламенко", "поп-музыки", "хард-рока"]
PRICES = ["10000", "15000", "20000", "30000", "40000",
          "50000", "80000", "120000", "200000"]


def pick(lst):
    return random.choice(lst)


def fmt(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace("{" + k + "}", v)
    return tpl


# ---------- ELECTRIC ----------

def gen_electric():
    rows = []
    tp = [
        # обычные проблемы
        ("Электрогитара {brand} {model} {sym}", ["medium", "high"]),
        ("{brand} {model}: {part} {sym}", ["medium", "high"]),
        ("{brand} {model} {sym} на репетиции", ["medium"]),
        ("Электрогитара {brand}: {sym} при касании струн", ["medium", "high"]),
        ("Купил {brand} {model} — {sym} при игре", ["medium", "high"]),
        ("{brand} {model} {sym} после смены струн", ["medium"]),
        ("Электрогитара {brand} {model}: сломался {part}", ["high"]),
        ("{brand} {model}: {part} не работает", ["high"]),
        ("Электрогитара {brand} {model} {sym} на чистом канале", ["medium"]),
        ("{brand} {model} {sym} на перегрузе", ["medium"]),
        ("Фонит электрогитара {brand} при прикосновении к струнам", ["high"]),
        ("Электрогитара {brand} {model}: трещит ручка громкости", ["medium"]),
        ("{brand} {model} — не работает {part}", ["high"]),
        ("Электрогитара {brand} {model} гудит только на одном датчике", ["medium"]),
        ("{brand} {model}: не держит строй после bend", ["medium"]),
        ("Электрогитара {brand} {model} — тумблер работает через раз", ["medium"]),
        ("{brand} {model} {sym} при переключении датчиков", ["medium"]),
        ("{brand} {model} — хрустит {part}", ["medium"]),
        # ВАЖНО: электрические гитары через комбик/усилитель
        ("Электрогитара {brand} {model} {sym} при подключении к комбику", ["high"]),
        ("{brand} {model} {sym} через комбик", ["high"]),
        ("{brand} {model}: фон через усилитель", ["high"]),
        ("Электрогитара {brand} {model} гудит при подключении к усилителю", ["high"]),
        ("{brand} {model} фон через комбик на перегрузе", ["high"]),
        ("Электрогитара {brand}: хрип через усилитель", ["high"]),
        ("Электрогитара {brand} {model} {sym} даже без подключения", ["medium"]),
        ("{brand} {model}: фон через комбик только на клине", ["medium"]),
        ("Купил электрогитару {brand}, при подключении к комбику идёт сильный фон", ["high"]),
        ("{brand} {model}: при подключении к комбику идёт хрип", ["high"]),
        ("Электрогитара {brand} {model} фонит через комбик и педалборд", ["high"]),
        ("{brand} {model}: сильный фон через комбик, что делать?", ["high"]),
        ("Электрогитара {brand} {model} — гул через усилитель", ["high"]),
        ("{brand} {model}: при игре через комбик фонит и хрипит", ["high"]),
    ]
    for _ in range(45):
        tpl, prios = pick(tp)
        rows.append((fmt(tpl,
                         brand=pick(ELECTRIC_BRANDS),
                         model=pick(ELECTRIC_MODELS),
                         sym=pick(SYMPTOMS),
                         part=pick(PARTS)),
                     "electric", pick(prios), "technical_problem"))

    pi = [
        "Хочу электрогитару {brand} для {genre}",
        "Посоветуйте электрогитару до {price} рублей",
        "Сравните {brand} {model} и аналоги",
        "{brand} {model} — есть в наличии?",
        "Сколько стоит {brand} {model}?",
        "Характеристики {brand} {model}",
        "Электрогитара {brand} {model} — обзор и отзывы",
        "Подойдёт ли {brand} {model} для {genre}?",
        "{brand} {model}: какого года выпуска?",
        "Какая мензура у {brand} {model}?",
        "Хочу электрогитару с активными датчиками",
        "Чем отличается {brand} {model} от других?",
        "Лучшая электрогитара для {genre} до {price}",
    ]
    for _ in range(18):
        tpl = pick(pi)
        rows.append((fmt(tpl,
                         brand=pick(ELECTRIC_BRANDS),
                         model=pick(ELECTRIC_MODELS),
                         genre=pick(GENRES),
                         price=pick(PRICES)),
                     "electric", "low", "product_info"))

    for _ in range(10):
        tpl = pick([
            "Электрогитара {brand} {model} пришла с браком",
            "{brand} {model} поцарапана при доставке",
            "Пришла {brand} {model} не того цвета",
            "{brand} {model}: сборка ужасная",
            "Электрогитара {brand} не соответствует описанию",
            "Электрогитара {brand} {model} пришла с трещиной",
        ])
        rows.append((fmt(tpl,
                         brand=pick(ELECTRIC_BRANDS),
                         model=pick(ELECTRIC_MODELS)),
                     "electric", pick(["medium", "high"]), "complaint"))

    for _ in range(8):
        tpl = pick([
            "Где мой заказ {brand} {model}?",
            "Заказ {brand} {model} задерживается",
            "Не пришло уведомление о доставке",
            "Статус заказа {brand} {model} не меняется",
            "Купил {brand} {model}, не могу отследить доставку",
            "Заказ электрогитары задерживается",
        ])
        rows.append((fmt(tpl,
                         brand=pick(ELECTRIC_BRANDS),
                         model=pick(ELECTRIC_MODELS)),
                     "electric", "medium", "order_issue"))

    for _ in range(8):
        tpl = pick([
            "Хочу вернуть электрогитару {brand} {model}",
            "Верните деньги за {brand} {model}",
            "Отменяю заказ на {brand} — нужен возврат",
            "{brand} {model} не подошла, хочу возврат",
            "Возврат средств за {brand} {model}",
            "Хочу отказаться от заказа электрогитары",
        ])
        rows.append((fmt(tpl,
                         brand=pick(ELECTRIC_BRANDS),
                         model=pick(ELECTRIC_MODELS)),
                     "electric", "high", "refund"))

    return rows


# ---------- ACOUSTIC ----------

def gen_acoustic():
    rows = []
    for _ in range(24):
        tpl = pick([
            "Акустика {brand} {model} {sym}",
            "{brand} {model}: {part} {sym}",
            "Акустическая гитара {brand} {model} {sym} при игре",
            "{brand} {model} — сломался {part}",
            "Акустика {brand}: {sym} через усилитель",
            "{brand} {model} {sym} после смены струн",
            "Электроакустика {brand} {model}: не работает пьезо",
            "Акустика {brand} {model}: {sym} в районе бриджа",
            "Акустика {brand} {model} {sym} на басовых струнах",
            "Акустика {brand} {model} — отклеилась подставка",
            "Электроакустика {brand}: шумит предусилитель",
            "Акустика {brand} {model}: треснула дека",
        ])
        rows.append((fmt(tpl,
                         brand=pick(ACOUSTIC_BRANDS),
                         model=pick(ACOUSTIC_MODELS),
                         sym=pick(SYMPTOMS),
                         part=pick(PARTS)),
                     "acoustic", pick(["medium", "high"]), "technical_problem"))

    for _ in range(16):
        tpl = pick([
            "Посоветуйте акустику до {price} рублей",
            "Акустика {brand} {model} — есть в наличии?",
            "Сравните {brand} {model} и аналоги",
            "Акустика для новичка — что выбрать?",
            "Акустика для {genre} — что посоветуете?",
            "Характеристики {brand} {model}",
            "{brand} {model} — обзор",
            "Акустика с вырезом до {price} рублей",
            "Сколько стоит {brand} {model}?",
            "Акустика для фингерстайла — что выбрать?",
            "Какая акустика лучше для сцены?",
        ])
        rows.append((fmt(tpl,
                         brand=pick(ACOUSTIC_BRANDS),
                         model=pick(ACOUSTIC_MODELS),
                         price=pick(PRICES),
                         genre=pick(GENRES)),
                     "acoustic", "low", "product_info"))

    for _ in range(10):
        rows.append((fmt(pick([
            "Акустика {brand} {model} пришла с трещиной",
            "Акустика {brand}: отклеилась подставка",
            "{brand} {model} поцарапана при доставке",
            "Акустика пришла не того цвета",
            "Акустика {brand} {model} — ужасная упаковка",
            "Акустика {brand} {model}: треснула дека",
        ]), brand=pick(ACOUSTIC_BRANDS), model=pick(ACOUSTIC_MODELS)),
                     "acoustic", pick(["medium", "high"]), "complaint"))

    for _ in range(7):
        rows.append((fmt(pick([
            "Где мой заказ акустики {brand}?",
            "Заказ {brand} {model} задерживается",
            "Не пришло уведомление о доставке",
            "Заказ акустической гитары задерживается",
        ]), brand=pick(ACOUSTIC_BRANDS), model=pick(ACOUSTIC_MODELS)),
                     "acoustic", "medium", "order_issue"))

    for _ in range(7):
        rows.append((fmt(pick([
            "Хочу вернуть акустику {brand} {model}",
            "Верните деньги за {brand} {model}",
            "Акустика {brand} не подошла — возврат",
            "Возврат средств за акустику",
        ]), brand=pick(ACOUSTIC_BRANDS), model=pick(ACOUSTIC_MODELS)),
                     "acoustic", "high", "refund"))

    return rows


# ---------- CLASSICAL ----------

def gen_classical():
    rows = []
    for _ in range(22):
        rows.append((fmt(pick([
            "Классика {brand} {model} {sym}",
            "Классическая гитара {brand} {model} {sym} при смене аккордов",
            "Классика {brand} {model}: сломался {part}",
            "{brand} {model} {sym} после транспортировки",
            "Классика {brand} {model} — не строит",
            "Классическая гитара {brand} {model}: {part} {sym}",
            "Классика {brand} {model} {sym} на басовых струнах",
            "Классическая гитара {brand} {model}: скрипит порожек",
            "Классика {brand} {model} — треснула дека",
        ]), brand=pick(CLASSICAL_BRANDS), model=pick(CLASSICAL_MODELS),
            sym=pick(SYMPTOMS), part=pick(PARTS)),
                     "classical", pick(["medium", "high"]), "technical_problem"))

    for _ in range(15):
        rows.append((fmt(pick([
            "Классика для ребёнка — что посоветуете?",
            "Классика для {genre} — что выбрать?",
            "Характеристики {brand} {model}",
            "Классика до {price} рублей",
            "{brand} {model} — есть в наличии?",
            "Сколько стоит {brand} {model}?",
            "Классическая гитара с мензурой 3/4",
            "Какую мензуру выбрать для ребёнка 8 лет?",
            "Классика для фламенко — что выбрать?",
            "Какая классика подойдёт для обучения?",
        ]), brand=pick(CLASSICAL_BRANDS), model=pick(CLASSICAL_MODELS),
            genre=pick(GENRES), price=pick(PRICES)),
                     "classical", "low", "product_info"))

    for _ in range(10):
        rows.append((fmt(pick([
            "Классика {brand} {model} пришла с трещиной",
            "Классическая гитара поцарапана при доставке",
            "Классика пришла не того цвета",
            "Классика {brand} {model} с браком на деке",
            "Классика {brand} {model} — не соответствует описанию",
        ]), brand=pick(CLASSICAL_BRANDS), model=pick(CLASSICAL_MODELS)),
                     "classical", pick(["medium", "high"]), "complaint"))

    for _ in range(6):
        rows.append((fmt(pick([
            "Где мой заказ классики {brand}?",
            "Заказ {brand} {model} задерживается",
            "Заказ классической гитары задерживается",
        ]), brand=pick(CLASSICAL_BRANDS), model=pick(CLASSICAL_MODELS)),
                     "classical", "medium", "order_issue"))

    for _ in range(6):
        rows.append((fmt(pick([
            "Хочу вернуть классику {brand} {model}",
            "Верните деньги за {brand} {model}",
            "Возврат средств за классическую гитару",
        ]), brand=pick(CLASSICAL_BRANDS), model=pick(CLASSICAL_MODELS)),
                     "classical", "high", "refund"))

    return rows


# ---------- BASS ----------

def gen_bass():
    rows = []
    for _ in range(24):
        rows.append((fmt(pick([
            "Бас {brand} {model} {sym}",
            "Бас-гитара {brand} {model} {sym} при подключении к комбику",
            "{brand} {model}: {part} {sym}",
            "Бас {brand} {model} — сломался {part}",
            "Бас-гитара {brand}: {sym} при касании струн",
            "Бас {brand} {model}: не работает {part}",
            "Бас-гитара {brand} {model} {sym} после смены струн",
            "Бас {brand} {model} — активный темброблок {sym}",
            "Бас-гитара {brand} {model} гудит при подключении к басовому комбику",
            "Бас {brand} {model}: не строит по ладам",
            "Бас-гитара {brand} {model} — фон на активной электронике",
            "Бас {brand} {model}: батарейка садится за день",
        ]), brand=pick(BASS_BRANDS), model=pick(BASS_MODELS),
            sym=pick(SYMPTOMS), part=pick(PARTS)),
                     "bass", pick(["medium", "high"]), "technical_problem"))

    for _ in range(15):
        rows.append((fmt(pick([
            "Бас-гитара для {genre} до {price} рублей",
            "Сравните {brand} {model} и аналоги",
            "Бас-гитара 5 струн — что посоветуете?",
            "Характеристики {brand} {model}",
            "Бас-гитара для новичка — что выбрать?",
            "{brand} {model} — есть в наличии?",
            "Сколько стоит {brand} {model}?",
            "Активный бас или пассивный — что лучше?",
            "Бас-гитара с короткой мензурой — что посоветуете?",
            "Какие струны для баса 5 струн?",
        ]), brand=pick(BASS_BRANDS), model=pick(BASS_MODELS),
            genre=pick(GENRES), price=pick(PRICES)),
                     "bass", "low", "product_info"))

    for _ in range(10):
        rows.append((fmt(pick([
            "Бас {brand} {model} пришёл с браком",
            "Бас-гитара поцарапана при доставке",
            "Бас пришёл не того цвета",
            "Бас {brand} {model}: ужасная сборка",
            "Бас-гитара {brand} не соответствует описанию",
        ]), brand=pick(BASS_BRANDS), model=pick(BASS_MODELS)),
                     "bass", pick(["medium", "high"]), "complaint"))

    for _ in range(7):
        rows.append((fmt(pick([
            "Где мой заказ баса {brand}?",
            "Заказ {brand} {model} задерживается",
            "Не пришло уведомление о доставке",
            "Заказ бас-гитары задерживается",
        ]), brand=pick(BASS_BRANDS), model=pick(BASS_MODELS)),
                     "bass", "medium", "order_issue"))

    for _ in range(7):
        rows.append((fmt(pick([
            "Хочу вернуть бас {brand} {model}",
            "Верните деньги за {brand} {model}",
            "Возврат средств за бас-гитару",
        ]), brand=pick(BASS_BRANDS), model=pick(BASS_MODELS)),
                     "bass", "high", "refund"))

    return rows


# ---------- ACCESSORIES ----------

def gen_accessories():
    rows = []
    for _ in range(14):
        rows.append((fmt(pick([
            "Струны {brand} {item} быстро ржавеют",
            "{item} {brand} — {sym}",
            "Кабель {brand} {sym}",
            "{item} {brand}: сломался через неделю",
            "Медиаторы {brand} стёрлись за неделю",
            "Каподастр {brand} не фиксируется",
            "Тюнер {brand} не ловит ноты",
            "Чехол {brand}: порвалась молния",
            "Струны {brand} порвались на первой неделе",
            "Ремень {brand} расстегивается",
        ]), brand=pick(ACC_BRANDS), item=pick(ACC_ITEMS), sym=pick(SYMPTOMS)),
                     "accessories", pick(["low", "medium", "high"]),
                     "technical_problem"))

    for _ in range(20):
        rows.append((fmt(pick([
            "Какие струны для {genre}?",
            "Струны {brand} {item} — подойдут для {genre}?",
            "Посоветуйте медиаторы до {price} рублей",
            "{item} {brand} — есть в наличии?",
            "Чем отличаются струны 10-46 от 11-49?",
            "Каподастр для акустики — какой выбрать?",
            "Сколько стоит {item} {brand}?",
            "Струны для 7-струнной гитары",
            "Чехол для электрогитары — что посоветуете?",
            "Стойка для гитары — какая лучше?",
            "Тюнер-прищепка — какой выбрать?",
            "Кабель 6 метров — что посоветуете?",
            "Струны для акустики 12-53 — какие?",
            "Струны Elixir стоят своих денег?",
        ]), brand=pick(ACC_BRANDS), item=pick(ACC_ITEMS),
            genre=pick(GENRES), price=pick(PRICES)),
                     "accessories", "low", "product_info"))

    for _ in range(12):
        rows.append((fmt(pick([
            "Струны {brand} пришли не того калибра",
            "Медиаторы пришли мягкие вместо жёстких",
            "Заказ медиаторов: количество не совпало",
            "Струны {brand} порвались на первой неделе",
            "Каподастр {brand} поцарапан при доставке",
            "Пришёл чехол не того размера",
            "Струны пришли не того бренда",
            "Медиаторы пришли разных толщин в одной упаковке",
        ]), brand=pick(ACC_BRANDS)),
                     "accessories", pick(["low", "medium", "high"]),
                     "complaint"))

    for _ in range(9):
        rows.append((fmt(pick([
            "Где мой заказ струн {brand}?",
            "Заказ медиаторов не пришёл",
            "{item} в пути уже 2 недели",
            "Не пришло уведомление о заказе",
            "Заказ {item} задерживается",
            "Заказ кабеля потерялся",
        ]), brand=pick(ACC_BRANDS), item=pick(ACC_ITEMS)),
                     "accessories", "medium", "order_issue"))

    for _ in range(7):
        rows.append((fmt(pick([
            "Хочу вернуть струны {brand}",
            "Медиаторы не подошли — возврат",
            "Верните деньги за {item}",
            "Струны не подошли — обмен или возврат",
        ]), brand=pick(ACC_BRANDS), item=pick(ACC_ITEMS)),
                     "accessories", "high", "refund"))

    return rows


# ---------- DELIVERY ----------

def gen_delivery():
    rows = []
    for _ in range(12):
        rows.append((pick([
            "Курьер не может найти адрес",
            "Трек-номер не отслеживается",
            "Сайт доставки не работает",
            "Не приходит SMS с кодом получения",
            "ПВЗ закрыт, не могу забрать заказ",
            "Курьер не приехал в назначенное время",
        ]), "delivery", "medium", "technical_problem"))

    for _ in range(18):
        rows.append((fmt(pick([
            "Сколько стоит доставка в {city}?",
            "Доставка за город доступна?",
            "Есть ли доставка в {city}?",
            "Сроки доставки в {city}",
            "Можно ли изменить адрес доставки после оплаты?",
            "Доставка крупногабарита — условия?",
            "Работаете ли с СДЭК?",
            "Есть ли бесплатная доставка?",
            "Доставка до двери или до ПВЗ?",
            "Доставка в {city} — сколько дней?",
            "Можно ли забрать самовывозом?",
            "Работаете в выходные с доставкой?",
        ]), city=pick(CITIES)),
                     "delivery", "low", "product_info"))

    for _ in range(16):
        rows.append((pick([
            "Курьер задерживается, доставка не пришла",
            "Заказ не привезли в оговорённое время",
            "Курьер не позвонил и уехал",
            "Посылка потерялась на складе",
            "Изменить адрес доставки — можно?",
            "Статус доставки не меняется",
            "Курьер опоздал на 3 часа",
            "Не приходит уведомление о доставке",
        ]), "delivery", "medium", "order_issue"))

    for _ in range(10):
        rows.append((pick([
            "Упаковка повреждена при доставке",
            "Курьер нагрубил",
            "Привезли не мой заказ",
            "Доставка в грязи и без упаковки",
            "Курьер опоздал, пришлось переносить встречу",
        ]), "delivery", pick(["medium", "high"]), "complaint"))

    for _ in range(6):
        rows.append((pick([
            "Заказ не пришёл — хочу возврат",
            "Оплатил доставку, но посылка не пришла",
            "Курьер потерял заказ — верните деньги",
        ]), "delivery", "high", "refund"))

    return rows


# ---------- PAYMENT ----------

def gen_payment():
    rows = []
    for _ in range(16):
        rows.append((pick([
            "Оплата картой не проходит, ошибка 500",
            "Не могу оплатить через СБП",
            "Платёж завис в статусе 'обработка'",
            "Оплата частями не работает",
            "Чек не пришёл на email",
            "Двойное списание с карты",
            "Ошибка валидации карты",
            "Промокод не применяется при оплате",
            "Оплата через ЮKassa не работает",
            "Не проходит оплата МИР",
            "Не работает оплата при получении",
            "Платёж отклонён банком",
        ]), "payment", pick(["medium", "high"]), "technical_problem"))

    for _ in range(16):
        rows.append((pick([
            "Какие способы оплаты доступны?",
            "Оплата частями — возможно?",
            "Работаете ли с картой МИР?",
            "Можно ли оплатить при получении?",
            "Как применить промокод?",
            "Оплата через ЮKassa — как?",
            "Оплата СБП — есть ли?",
            "Как оформить возврат на карту?",
            "Оплата в рассрочку — условия?",
            "Принимаете ли оплату от юрлиц?",
            "Есть ли оплата по QR-коду?",
        ]), "payment", "low", "product_info"))

    for _ in range(10):
        rows.append((pick([
            "Оплата прошла, но заказ не подтверждён",
            "Чек не пришёл, нужен для отчётности",
            "Заказ не создался после оплаты",
            "Не приходит подтверждение оплаты",
        ]), "payment", "medium", "order_issue"))

    for _ in range(10):
        rows.append((pick([
            "Верните деньги за отменённый заказ",
            "Двойное списание — верните разницу",
            "Отменил заказ — когда вернутся деньги?",
            "Платёж прошёл дважды, оформите возврат",
        ]), "payment", "high", "refund"))

    for _ in range(10):
        rows.append((pick([
            "Списали деньги, а заказ не оформился",
            "Платёж прошёл дважды",
            "При оплате вылетела ошибка, деньги списались",
            "Списали деньги, но заказ не создан",
        ]), "payment", "high", "complaint"))

    return rows


# ---------- WARRANTY ----------

def gen_warranty():
    rows = []
    for _ in range(12):
        rows.append((fmt(pick([
            "Гарантийный ремонт: сломался {part}",
            "Хочу заменить по гарантии {part}",
            "Погнулся {part} — гарантийный случай?",
            "Гарантийный случай: треснула дека",
            "Гарантийная замена {part}",
            "По гарантии должен замениться {part}",
        ]), part=pick(PARTS)),
                     "warranty", "medium", "technical_problem"))

    for _ in range(18):
        rows.append((fmt(pick([
            "Гарантия на электронику — что входит?",
            "Гарантийный случай или моя вина?",
            "Сколько составляет гарантия на гитару?",
            "Что входит в гарантийное обслуживание?",
            "Гарантия на фурнитуру гитары",
            "Гарантия покрывает замену {part}?",
            "Как оформить гарантию?",
            "Гарантия на бас-гитару — срок?",
            "Гарантия на акустику — срок?",
            "Гарантия на Floyd Rose — что покрывает?",
            "Гарантия на пьезо в электроакустике",
            "Гарантия на электронику — 1 год или больше?",
            "Заводской брак или износ — как определить?",
        ]), part=pick(PARTS)),
                     "warranty", "low", "product_info"))

    for _ in range(7):
        rows.append((pick([
            "Гарантийный ремонт — как отследить статус?",
            "Не приходит ответ по гарантийной заявке",
            "Статус гарантийного ремонта не меняется",
        ]), "warranty", "medium", "order_issue"))

    for _ in range(10):
        rows.append((pick([
            "Хочу вернуть гитару по гарантии",
            "Гарантийный возврат средств — как оформить?",
            "Возврат по гарантии — возможно?",
        ]), "warranty", "high", "refund"))

    for _ in range(12):
        rows.append((pick([
            "По гарантии отказали без объяснений",
            "Гарантийный ремонт затянулся на месяц",
            "Гарантия не покрывает заводской брак?",
            "Отказали в гарантии без причины",
            "Гарантийный ремонт — уже 2 месяца",
        ]), "warranty", "high", "complaint"))

    return rows


# ---------- MAIN ----------

def main():
    all_rows = []
    all_rows += gen_electric()
    all_rows += gen_acoustic()
    all_rows += gen_classical()
    all_rows += gen_bass()
    all_rows += gen_accessories()
    all_rows += gen_delivery()
    all_rows += gen_payment()
    all_rows += gen_warranty()

    # Убираем точные дубликаты по тексту
    seen, unique = set(), []
    for r in all_rows:
        if r[0] in seen:
            continue
        seen.add(r[0])
        unique.append(r)

    random.shuffle(unique)

    # QUOTE_ALL — оборачиваем каждое поле в кавычки,
    # чтобы запятые внутри текста не ломали CSV.
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["text", "category", "priority", "problem_type"])
        w.writerows(unique)

    cats = Counter(r[1] for r in unique)
    prios = Counter(r[2] for r in unique)
    pts = Counter(r[3] for r in unique)
    print(f"Записано {len(unique)} строк → {OUT}")
    print(f"  category:     {dict(cats)}")
    print(f"  priority:     {dict(prios)}")
    print(f"  problem_type: {dict(pts)}")


if __name__ == "__main__":
    main()