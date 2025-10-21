import re
from . import utils
from collections import Counter
from typing import Dict, Any

def _get_transcriptor():
    # Ленивая загрузка транскриптора для избежания циклических импортов
    from . import transcriptor
    return transcriptor

def transcribe(text: str, simplify: bool = False) -> str:
    """
    Транскрибирует текст по русским правилам фонетики.
    :param text: исходный текст
    :param simplify: применять ли упрощённые правила
    :return: транскрибированный текст
    """
    transcriptor = _get_transcriptor()
    return transcriptor.transcribe(text, simplify=simplify)

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
    """
    if not input_is_transcribed:
        text = transcribe(text, simplify=True)

    # Группы определены по фонетическим признакам:
    whistling_pat = r"з'?|с'?"                 # свистящие: з, з', с, с'
    hissing_pat   = r"ж|ш|щ'|ч"                # шипящие: ж, ш, щ', ч
    # твёрдые и мягкие определяются наличием мягкого/твердого знака после согласной
    hard_pat      = r"ц|ш|ж|н(?!')|б(?!')|в(?!')|г(?!')|д(?!')|з(?!')|к(?!')|л(?!')|м(?!')|п(?!')|р(?!')|с(?!')|т(?!')|ф(?!')|х(?!')"
    soft_pat      = r"й|ч|щ'|б'|в'|г'|д'|з'|к'|л'|м'|н'|п'|р'|с'|т'|ф'|х'"

    # Подсчёт:
    whistling_count = len(re.findall(whistling_pat, text))
    hissing_count = len(re.findall(hissing_pat, text))
    hard_count = len(re.findall(hard_pat, text))
    soft_count = len(re.findall(soft_pat, text))

    sum_count = whistling_count + hissing_count + hard_count + soft_count
    # Возможен случай, когда сумма нулевая (вернуть нули)
    def safe_div(val: int) -> float:
        return val / sum_count if sum_count else 0.0

    result = {
        "свистящие": safe_div(whistling_count),
        "шипящие":  safe_div(hissing_count),
        "твердые":  safe_div(hard_count),
        "мягкие":   safe_div(soft_count)
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
