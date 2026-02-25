 # ruphonetic

Модуль для **фонетического анализа русского текста**:

- **автоматическая расстановка ударений** (через `spaCy` и словарные данные);
- **фонетическая транскрипция** по правилам русской фонетики;
- построение **частотного спектра звуков (фонем)**;
- группировка звуков по классам (свистящие, шипящие, твёрдые, мягкие);
- **динамика спектра** по тексту (скользящее окно / нарастающая длина);
- приближённая **идентификация автора** по звуковому спектру.

Библиотека пригодится для лингвистических исследований, анализа поэзии и прозы, учебных задач и экспериментов с русской фонетикой.

## Установка

```bash
pip install ruphonetic
```

При первом запуске модуль автоматически скачает модель `ru_core_news_md` для `spaCy`, если она ещё не установлена. Это может занять несколько минут.

## Быстрый старт

```python
import ruphonetic

text = (
    "У лукоморья дуб зелёный;\n"
    "Златая цепь на дубе том:\n"
    "И днём и ночью кот учёный\n"
    "Всё ходит по цепи кругом\n"
)

# 1. Транскрипция
phonetic = ruphonetic.transcribe(text, simplify=False)
print(phonetic)

# 2. Упрощённая транскрипция (только допустимые фонемы)
phonetic_simple = ruphonetic.transcribe(text, simplify=True)
print(phonetic_simple)

# 3. Спектр звуков (фонем)
spectre = ruphonetic.sound_spectre(text, show_plot=False)
print(spectre)
```

## Основные функции

Все публичные функции доступны прямо из пакета `ruphonetic` (см. `ruphonetic/__init__.py`).

### `transcribe(text: str, simplify: bool = False, verbose: bool = False) -> str`

Транскрибирует текст по правилам русской фонетики.

- **`text`** – исходный русский текст;
- **`simplify`** – если `True`, применяется упрощённая транскрипция (оставляются только допустимые фонемы и служебные символы);
- **`verbose`** – если `True`, по шагам выводятся промежуточные стадии обработки.

```python
from ruphonetic import transcribe

print(transcribe("гравитационное поле"))
```

### `sound_spectre(text: str, input_is_transcribed: bool = False, show_plot: bool = False, show_pie_plot: bool = False, show_bar_plot: bool = False) -> dict[str, float]`

Строит **частотный спектр фонем** в тексте.

- если `input_is_transcribed=False`, текст сначала транскрибируется с `simplify=True`;
- результат — словарь `{фонема: относительная_частота}`;
- при `show_plot / show_pie_plot / show_bar_plot = True` строятся соответствующие графики (через `matplotlib`).

```python
from ruphonetic import sound_spectre

spectre = sound_spectre("У лукоморья дуб зелёный", show_bar_plot=True)
```

### `sound_spectre_grouped(...) -> dict[str, float]`

Группирует спектр по классам звуков:

- «свистящие»,
- «шипящие»,
- «твёрдые»,
- «мягкие».

Интерфейс аналогичен `sound_spectre`, но на выходе — спектр по **классам**, а не по отдельным фонемам.

### `sound_spectre_grouped_custom(...) -> dict[str, float]`

Интерактивная версия: пользователь вводит группы фонем через консоль (например, `п|б|м`), а функция считает их суммарные частоты и, при желании, строит графики.

### Динамика спектра

- **`sound_spectre_dynamic_position(text: str, word_amount: int, input_is_transcribed: bool = False)`**

  Строит спектры по «скользящему окну» из `word_amount` слов, двигающемуся по тексту.

- **`sound_spectre_dynamic_length(text: str, input_is_transcribed: bool = False)`**

  Строит спектры для нарастающих префиксов текста (от первых слов к более длинным отрезкам).

Обе функции возвращают словари вида:

```python
{
    index: {
        "substring": "<фрагмент текста>",
        "result": { "<фонема>": <частота>, ... }
    },
    ...
}
```

### `identify_author_by_sound_spectre(text: str, grouped: bool = False) -> dict[str, float]`

Сравнивает звуковой спектр входного текста со спектрами авторов, сохранёнными в поддиректории `ruphonetic/authors`, и возвращает словарь:

```python
{
    "Имя_автора": коэффициент_сходства,
    ...
}
```

Используется **косинусное сходство** между спектрами. Если `grouped=True`, сравнение происходит по групповому спектру (`sound_spectre_grouped`), иначе — по обычному (`sound_spectre`).

## Зависимости

Основные зависимости (см. `setup.py`):

- `numpy`
- `spacy` (модель `ru_core_news_md`)
- `matplotlib`

`spaCy`‑модель будет автоматически загружена при первом использовании модуля акцентуации.

## Лицензия

Проект распространяется по лицензии **MIT**. См. файл `LICENSE.txt` в репозитории/дистрибутиве.

