import re
from typing import Match, Callable

from .accentuation import stress

# Словарь замен для йотированных гласных
jot_dict: dict[str, str] = {
    "ё": "й'о", "`ё": "`о",
    "е": "й'э", "`е": "`э",
    "я": "й'а", "`я": "й'`а",
    "ю": "й'у", "`ю": "`у",
    "'ё": "'й'о", "'`ё": "'`о",
    "'е": "'й'э", "'`е": "'`э",
    "'я": "'й'а", "'`я": "'й'`а",
    "'ю": "'й'у", "'`ю": "'`у",
}

def jot_function_1(m: Match) -> str:
    """Функция замены для йотированных гласных после гласной, мягкого или твердого знака"""
    return jot_dict[m.group(1)]

def jot_function_2(m: Match) -> str:
    """Дополнительная функция замены для других случаев (зарезервировано)"""
    return jot_dict[m.group(2)]

def jot(s: str) -> str:
    """
    Замена йотированных гласных в нужной позиции.
    Например: 'е', 'ё', 'ю', 'я' – после гласных или знаков.
    """
    # После гласной буквы
    s = re.sub(r"[аяиыуюеёо]([еёюя])", jot_function_1, s)
    # После мягкого или твердого знака
    s = re.sub(r"('[еёюя])|ъ([еёюя])", jot_function_1, s)
    return s

def deafen_and_sharpen(s: str) -> str:
    """
    Оглушение и озвончение согласных по правилам русского языка.
    """
    sharpening_map: dict[str, str] = {"к": "г", "т": "д", "п": "б", "с": "з", "ш": "ж", "ф": "в"}
    deafening_map: dict[str, str] = {"г": "к", "д": "т", "б": "п", "з": "с", "ж": "ш", "в": "ф"}
    sharp_sounds: str = "бгвдзжмнл"
    deaf_sounds: str = "пкфтсшщхцч"

    # Заменяем специфические сочетания
    s = re.sub("гк", "хк", s)

    # Оглушение в середине слова перед глухим согласным
    for k in "бгвдзж":
        s = re.sub(k + rf"([{deaf_sounds}])", deafening_map[k] + r'\1', s)

    # Оглушение в конце слова и текста
    for sharp_sound in deafening_map:
        s = re.sub(rf"([а-я]+){sharp_sound}([^а-яё`'])", r'\1' + deafening_map[sharp_sound] + r'\2', s)
        s = re.sub(rf"{sharp_sound}$", deafening_map[sharp_sound], s)

    # Ожзвончение после "в" и "с" перед звонкими/глухими
    s = re.sub(rf"в ([{deaf_sounds}])", "ф " + r'\1', s)
    s = re.sub(r"с ([бгдзжмнл])", "з " + r'\1', s)

    return s

def soften_vowels(s: str) -> str:
    """
    Смягчение согласных перед некоторыми гласными (я, ё, ю, е, и, ь)
    """
    always_softening_vowels: str = "яёюеиь"
    vowels_map: dict[str, str] = {
        "я": "'а", "`я": "'`а",
        "ё": "'о", "`ё": "'`о",
        "ю": "'у", "`ю": "'`у",
        "е": "'э", "`е": "'`э",
        "и": "'и", "`и": "'`и",
        "ь": "'"
    }

    def soften_function(m: Match) -> str:
        # Берём согласный + замену по словарю (гласная с мягкостью)
        item = vowels_map[m.group(1)]
        return m.group()[0] + item

    not_always_hard_consonants: str = "бвгдзклмнпрстфхчщ"

    for consonant in not_always_hard_consonants:
        s = re.sub(consonant + r"(`*[" + always_softening_vowels + r'])', soften_function, s)
    return s

def soften_consonants(s: str) -> str:
    """
    Дополнительное смягчение некоторых согласных в определённых сочетаниях.
    """
    # Смягчение "н" перед "ч" и "щ"
    s = re.sub(rf"н([чщ])", "н'" + r"\1", s)
    # Смягчение твердых согласных перед мягкими согласными
    s = re.sub(rf"([дтзсн])(д'|т'|з'|с'|н')", r"\1'" + r"\2", s)

    always_soft_consonants: str = "чщ"
    for consonant in always_soft_consonants:
        s = re.sub(rf"{consonant}([^'])", consonant + "'" + r'\1', s)
    return s

def soften(s: str) -> str:
    """
    Комплексное смягчение букв и сочетаний
    """
    s = soften_vowels(s)
    s = soften_consonants(s)
    return s

def accentuate(s: str) -> str:
    """
    Добавляет ударения с помощью модуля stress.
    """
    s = stress.accentuate(s).lower()
    # Можно добавить правило для автоматического замещения 'о' без ударения, если нужно
    return s

def remove_hard_sign(s: str) -> str:
    """
    Удаляет твёрдый знак из транскрипции
    """
    return re.sub("ъ", "", s)

def simplify_transcription(s: str) -> str:
    """
    Оставляет только набор допустимых фонем и их символику в упрощённом виде
    """
    result = re.findall(r"`[аеёиоуыэюя]|[бвгджзклмнпрстфхцчшщ' \n]", s)
    s = "".join(result)
    s = re.sub("`", "", s)
    s = re.sub("(')+", "'", s)
    return s

def tsya(s: str) -> str:
    """
    Замена тся/ться на 'ца' в соответствии с произношением
    """
    result = re.sub(r"ться|тся", "ца", s)
    return result

def ego(s: str) -> str:
    """
    Замена окончаний -ого, -его на -ава, -ива в соответствии с фонетикой
    """
    s = re.sub(r"([^`])его\b", r"\1ива", s)
    s = re.sub(r"([^`])ого\b", r"\1ава", s)
    return s

def transcribe(s: str, simplify: bool = False, verbose: bool = False) -> str:
    """
    Главная функция транскрибирования.
    Включает акцентуацию, замену оканчаний, мягкость, оглушение, йотирование и упрощение.
    """

    s = accentuate(s)
    if verbose:
        print("accentuate:\n", s, "\n")

    s = tsya(s)
    if verbose:
        print("tsya:\n", s, "\n")

    s = ego(s)
    if verbose:
        print("ego:\n", s, "\n")

    s = soften(s)
    if verbose:
        print("soften:\n", s, "\n")

    s = jot(s)
    if verbose:
        print("jot:\n", s, "\n")

    s = deafen_and_sharpen(s)
    if verbose:
        print("deafen&sharpen:\n", s, "\n")

    s = remove_hard_sign(s)
    if verbose:
        print("hard sign:\n", s, "\n")

    if simplify:
        s = simplify_transcription(s)
        if verbose:
            print("simplify:\n", s, "\n")

    # Убираем начальные и лишние пробелы
    s = re.sub("^ ", "", s)
    s = re.sub("\n ", "\n", s)
    s = re.sub(r"[^\S\r\n]+", " ", s)
    return s

if __name__ == '__main__':
    # Пример работы транскриптора с простым текстом
    s = (
        "У лукоморья дуб зелёный;\n"
        "Златая цепь на дубе том:\n"
        "И днём и ночью кот учёный\n"
        "Всё ходит по цепи кругом"
    )
    print(transcribe(s, True))