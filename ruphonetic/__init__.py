import re
import json
import math
from pathlib import Path
from ruphonetic import utils
from collections import Counter
from typing import Dict, Any
from ruphonetic.transcriptor import transcribe as _transcribe

def transcribe(text: str, simplify: bool = False, verbose: bool = False) -> str:
    """
    Транскрибирует текст по русским правилам фонетики.
    :param text: исходный текст
    :param simplify: применять ли упрощённые правила
    :return: транскрибированный текст
    """
    if len(text) > 1000000:
        print("WARNING! text is too long. Transcribing only first 1000000 symbols")
        text = text[:1000000]
    return _transcribe(text, simplify=simplify, verbose=verbose)

def sound_spectre(
    text: str, 
    input_is_transcribed: bool = False, 
    show_plot: bool = False, 
    show_pie_plot: bool = False, 
    show_bar_plot: bool = False
) -> Dict[str, float]:
    """
    Возвращает частотный спектр звуков (фонем) в тексте.
    По умолчанию, применяется русская фонетика.
    """
    if not input_is_transcribed:
        text = transcribe(text, simplify=True)
    # Регулярка: любая русская буква в нижнем регистре, возможно с мягкостью (апостроф)
    sounds = re.findall(r"[а-я]'?", text)
    total = len(sounds)
    if not total:
        return {}  # Пустой ввод — пустой результат
    result = {sound: count / total for sound, count in Counter(sounds).items()}
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True)) # сортировка по значению (ascending)
    utils.show_plots(result, show_plot, show_pie_plot, show_bar_plot)

    return result

def sound_spectre_grouped(
    text: str, 
    input_is_transcribed: bool = False, 
    show_plot: bool = False, 
    show_pie_plot: bool = False, 
    show_bar_plot: bool = False
) -> Dict[str, float]:
    """
    Группировка по типам фонем (свистящие, шипящие, твёрдые, мягкие).
    Версия 2026: учтена классификация Ц и всегда мягких/твёрдых звуков.
    """
    if not input_is_transcribed:
        # Предполагаем, что ваша функция transcribe возвращает символы с апострофом ' 
        # для мягких звуков (например, л', ч', щ')
        text = transcribe(text, simplify=True)

    # 1. СВИСТЯЩИЕ: з, з', с, с', ц (Ц всегда твёрдый, но свистящий)
    whistling_pat = r"з'?|с'?|ц"
    
    # 2. ШИПЯЩИЕ: ж, ш, щ', ч' (Ж, Ш всегда твёрдые; Щ, Ч всегда мягкие)
    hissing_pat = r"ж|ш|щ'|ч'"

    # 3. ТВЁРДЫЕ:
    # - всегда твёрдые: ж, ш, ц
    # - парные твёрдые: б, в, г, д, з, к, л, м, n, п, р, с, т, ф, х (без следующего ')
    # Используем негативную проверку (?![яёюие']) если работаем с текстом, 
    # но так как у нас ТРАНСКРИПЦИЯ, проверяем только отсутствие апострофа.
    hard_pat = r"[бвгдзклмнпрстфх](?!')|ж|ш|ц"

    # 4. МЯГКИЕ:
    # - всегда мягкие: й', ч', щ' (или й, если он без ')
    # - парные мягкие: любой согласный с апострофом
    soft_pat = r"[бвгдзклмнпрстфх]'|й'?|ч'|щ'"

    # Подсчёт совпадений
    whistling_count = len(re.findall(whistling_pat, text))
    hissing_count = len(re.findall(hissing_pat, text))
    hard_count = len(re.findall(hard_pat, text))
    soft_count = len(re.findall(soft_pat, text))

    # Суммируем для нормализации (пропорции)
    # Важно: один звук может быть и свистящим, и твёрдым (например, Ц). 
    # Это нормально для спектрального анализа.
    total_found = whistling_count + hissing_count + hard_count + soft_count
    
    def safe_div(val: int) -> float:
        return val / total_found if total_found else 0.0

    result = {
        "свистящие": safe_div(whistling_count),
        "шипящие":   safe_div(hissing_count),
        "твердые":   safe_div(hard_count),
        "мягкие":    safe_div(soft_count)
    }

    utils.show_plots(result, show_plot, show_pie_plot, show_bar_plot)
        
    return result


def sound_spectre_grouped_custom(
    text: str,
    input_is_transcribed: bool = False,
    show_plot: bool = False,
    show_pie_plot: bool = False,
    show_bar_plot: bool = False
) -> Dict[str, float]:
    """
    Кастомная группировка фонем — пользователь вводит группы вручную через консоль.
    Правильное применение требует ввода на русском, можно мягкость с апострофом.
    """
    if not input_is_transcribed:
        text = transcribe(text, simplify=True)

    print(text)
    group_num = 1
    groups: Dict[int, Dict[str, Any]] = {}
    entries_sum = 0
    print("Введите группы звуков, разделяя звуки знаком |, без пробелов. Напишите /s если Вы ввели все группы.")

    while True:
        print(f"Группа {group_num}: ")
        user_input = input()
        if "/s" in user_input:
            break
        # Проверка правильности формата: последовательности [а-я]'? разделены |
        if not re.fullmatch(r"([а-я]'?)(\|[а-я]'?)*", user_input):
            print("Неверный ввод")
            continue
        # Проверка дублей
        sounds = user_input.split('|')
        if len(set(sounds)) != len(sounds):
            print("В группах не могут повторяться одни и те же звуки.")
            continue
        # Составляем regexp: подбирает указанную букву с опциональным апострофом
        # Вариант: поочерёдно искать каждую фонему в тексте 
        entries = []
        for s in sounds:
            entries.extend(re.findall(r"{}".format(re.escape(s)), text))
        groups[group_num] = {
            'input': user_input,
            'sounds': sounds,
            'entries': entries
        }
        entries_sum += len(entries)
        group_num += 1

    # Формирование результата с подсчётом нормализованных частот
    result: Dict[str, float] = {}
    for group_num in groups:
        entries_count = len(groups[group_num]['entries'])
        result[groups[group_num]['input']] = entries_count / entries_sum if entries_sum else 0

    utils.show_plots(result, show_plot, show_pie_plot, show_bar_plot)
    return result

def sound_spectre_dynamic_position(
    text: str, 
    word_amount: int, 
    input_is_transcribed: bool = False
) -> Dict[int, Dict[str, Any]]:
    """
    Возвращает спектры звуков по 'скользящему окну' размера word_amount по словам.
    """
    if not input_is_transcribed:
        text = transcribe(text, simplify=True)
    words = text.replace("\n", " ").split(" ")
    if word_amount > len(words):
        raise IndexError("Количество слов в окне превышает общее число слов в тексте")
    result: Dict[int, Dict[str, Any]] = {}

    for i in range(0, len(words) - word_amount + 1):
        substring = " ".join(words[i:i+word_amount])
        substring_spectre = sound_spectre(substring, input_is_transcribed=True)
        result[i] = {
            'substring': substring,
            'result': substring_spectre
        }

    return result

def sound_spectre_dynamic_length(
    text: str, 
    input_is_transcribed: bool = False
) -> Dict[int, Dict[str, Any]]:
    """
    Возвращает спектры звуков по последовательному наращиванию длины по словам.
    """
    if not input_is_transcribed:
        text = transcribe(text, simplify=True)
    words = text.replace("\n", " ").split(" ")
    result: Dict[int, Dict[str, Any]] = {}

    # i = 1 ... len(words)-1 (не включаем всё строку сразу)
    for i in range(1, len(words)):
        substring = " ".join(words[0:i])
        substring_spectre = sound_spectre(substring, input_is_transcribed=True)
        result[i] = {
            'substring': substring,
            'result': substring_spectre
        }

    return result

def identify_author_by_sound_spectre(text: str, grouped: bool = False) -> Dict[str, float]:
    """
    Сравнивает звуковой спектр текста со спектрами известных авторов
    и возвращает словарь с вероятностями соответствия каждому автору.
    
    :param text: исходный текст для анализа
    :return: словарь с ключами - именами авторов, значениями - коэффициентами схожести (float)
    """
    # Генерируем звуковой спектр для входного текста
    if grouped:
        user_spectre = sound_spectre_grouped(text, input_is_transcribed=False)
    else:
        user_spectre = sound_spectre(text, input_is_transcribed=False)
    
    if not user_spectre:
        return {}  # Пустой текст - возвращаем пустой результат
    
    # Находим все файлы sound_spectre.json в директориях авторов
    authors_dir = Path(__file__).parent / "authors"
    author_scores: Dict[str, float] = {}
    
    # Ищем все sound_spectre.json файлы
    if grouped:
        path =  "*/sound_spectres/sound_spectre_grouped.json"
    else:
        path = "*/sound_spectres/sound_spectre.json"
    spectre_files = list(authors_dir.glob(path))
    
    for spectre_file in spectre_files:
        # Извлекаем имя автора из пути
        author_name = spectre_file.parent.parent.name
        
        try:
            # Загружаем спектр автора
            with open(spectre_file, 'r', encoding='utf-8') as f:
                author_spectre = json.load(f)
            
            # Вычисляем косинусное сходство
            similarity = _cosine_similarity(user_spectre, author_spectre)
            author_scores[author_name] = similarity
            
        except (json.JSONDecodeError, IOError) as e:
            # Пропускаем файлы, которые не удалось загрузить
            continue
    sorted_author_scores = dict(sorted(author_scores.items(), key=lambda item: item[1], reverse=True))
    return sorted_author_scores

def _cosine_similarity(spectre1: Dict[str, float], spectre2: Dict[str, float]) -> float:
    """
    Вычисляет косинусное сходство между двумя звуковыми спектрами.
    
    :param spectre1: первый спектр (словарь звук -> частота)
    :param spectre2: второй спектр (словарь звук -> частота)
    :return: коэффициент сходства от 0 до 1
    """
    # Получаем все уникальные звуки из обоих спектров
    all_sounds = set(spectre1.keys()) | set(spectre2.keys())
    
    if not all_sounds:
        return 0.0
    
    # Создаём векторы для всех звуков (отсутствующие звуки = 0)
    vec1 = [spectre1.get(sound, 0.0) for sound in all_sounds]
    vec2 = [spectre2.get(sound, 0.0) for sound in all_sounds]
    
    # Вычисляем скалярное произведение
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Вычисляем нормы векторов
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    # Косинусное сходство
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return similarity
