import re
from typing import Match

# Direct import to avoid relative import issue
from ruphonetic.accentuation import stress

def apply_jotation(s: str) -> str:
    # Базовая карта звуков для йотированных гласных
    # (используется для обеих позиций: и для йотации, и для смягчения)
    vowel_map = {
        'е': 'э', 'ё': 'о', 'ю': 'у', 'я': 'а'
    }

    # 1. Йотирование (два звука: [й] + гласный)
    # Условия: начало строки, после гласных или после Ъ/Ь
    def jot_replacer(match):
        prefix = match.group(1) or ""  # Символ перед буквой
        accent = match.group(2)         # Маркер ` (если есть)
        char = match.group(3)           # Сама буква е/ё/ю/я
        
        sound = vowel_map[char]
        # Если был знак ударения `, ставим его ПОСЛЕ 'й'
        if accent == "`":
            return f"{prefix}й'{accent}{sound}"
        return f"{prefix}й'{sound}"

    # Регулярное выражение с Lookbehind для определения позиции йотирования
    pattern_jot = r"(^|(?<=[аеёиоуыэюяъ'\s]))(`?)([еёюя])"
    s = re.sub(pattern_jot, jot_replacer, s)

    # 2. Смягчение (один звук после согласных)
    # Если буква не йотировалась выше, значит она стоит после согласного.
    def soft_replacer(match):
        accent = match.group(1) or ""
        char = match.group(2)
        # В транскрипции смягчение ' ставится после согласного, 
        # а ударение ` — над/после гласного.
        return f"'{accent}{vowel_map[char]}"

    # Ищем оставшиеся е, ё, ю, я
    s = re.sub(r"(`?)([еёюя])", soft_replacer, s)

    return s

def deafen_and_sharpen(s: str) -> str:
    """
    Оглушение и озвончение согласных по правилам русского языка.
    """
    deafening_map: dict[str, str] = {"г": "к", "д": "т", "б": "п", "з": "с", "ж": "ш", "в": "ф"}
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

    # Озвончение после "в" и "с" перед звонкими/глухими
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
    Замена окончаний -ого на -ава/-ово, -его на -ива в соответствии с фонетикой
    """
    s = re.sub(r"([^`])его\b", r"\1ива", s)
    s = re.sub(r"([^`])ого\b", r"\1ава", s)
    s = re.sub(r"`ого\b", r"`ова", s)
    return s

def word_ending(s: str) -> str:
    """Замена окончаний ться/тся и ого/его последовательно"""
    return ego(tsya(s))

def vowel_reduction(s: str) -> str:
    """
    Редукция безударных гласных. 
    'я' редуцируется в 'и' только если она без ударения 
    и находится в середине слова (не в начале и не в конце).
    """
    # 1. Редукция "о" (о → а)
    s = re.sub(r"(?<!`)о(?!`)", "а", s)
    
    # 2. Редукция "е" (е → и)
    s = re.sub(r"(?<![ь`])е(?!`)(?=[\w])", "и", s)
    # (?=\w)   -- проверка, что справа есть буква (не конец слова)
    
    # 3. Редукция "я" (я → и)
    # (?<=\w)  -- проверка, что слева есть буква (не начало слова)
    # (?<!`)   -- проверка, что нет ударения перед буквой
    # (?=\w)   -- проверка, что справа есть буква (не конец слова)
    s = re.sub(r"(?<=\w)(?<!`)я(?=[\w])", "и", s)
    
    return s

def handle_sch_combinations(s: str) -> str:
    """
    Заменяет сочетания 'сч' на звук 'щ' в соответствии с правилами русского языка.
    Примеры: 'счастье' → 'щастье', 'считать' → 'щитать'
    """
    # Заменяем "сч" на "щ" в любой позиции
    s = re.sub(r"сч", r"щ'", s)

    # Убираем возможное двойное смягчение, если оно возникло
    s = re.sub(r"щ'", r"щ", s)
    
    return s

def transcribe(s: str, simplify: bool = False, verbose: bool = False) -> str:
    """
    Главная функция транскрибирования.
    Включает акцентуацию, замену оканчаний, мягкость, оглушение, йотирование и упрощение.
    """

    s = accentuate(s) # Расставляем ударения
    if verbose:
        print("accentuate:\n", s, "\n")

    
    s = word_ending(s) # Замена окончаний
    if verbose:
        print("word_ending:\n", s, "\n")

    s = vowel_reduction(s) # Редукция безударных гласных
    if verbose:
        print("vowel_reduction:\n", s, "\n")

    s = soften(s) # Смягчение согласных
    if verbose:
        print("soften:\n", s, "\n")

    s = apply_jotation(s) # Замена йотированных гласных
    if verbose:
        print("jot:\n", s, "\n")

    s = handle_sch_combinations(s)
    if verbose:
        print("sch: \n", s, "\n")

    s = deafen_and_sharpen(s) # Оглушение и озвончение согласных
    if verbose:
        print("deafen&sharpen:\n", s, "\n")

    s = remove_hard_sign(s) # Удаление твердого знака
    if verbose:
        print("hard sign:\n", s, "\n")

    if simplify:
        s = simplify_transcription(s) # Упрощение транскрипции
        if verbose:
            print("simplify:\n", s, "\n")

    # Убираем начальные и лишние пробелы
    s = re.sub("^ ", "", s)
    s = re.sub("\n ", "\n", s)
    s = re.sub(r"[^\S\r\n]+", " ", s)
    return s

