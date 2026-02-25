import spacy, pickle

import pathlib
PATH = pathlib.Path(__file__).parent.resolve()
import re

ru_nlp = None

try:
    ru_nlp = spacy.load('ru_core_news_md')
except OSError:
    print('Downloading language model for the spaCy POS tagger\n'
        "(don't worry, this will only happen once)")
    from spacy.cli import download
    download('ru_core_news_md')
    ru_nlp = spacy.load('ru_core_news_md')

def load():
    with open(file=f"{PATH}/lemmas.dat", mode='rb') as f:
        lemmas = pickle.loads(f.read())
    with open(file=f"{PATH}/wordforms.dat", mode='rb') as f:
        wordforms = pickle.loads(f.read())
    return lemmas, wordforms

def introduce_special_cases_from_dictionary(dictionary):
    for word in dictionary:
        if (" " in word) or ("-" in word):
            if len(dictionary[word]) == 1:
                ru_nlp.tokenizer.add_special_case(word, [{"ORTH": dictionary[word][0]["accentuated"]}])
                ru_nlp.tokenizer.add_special_case(word.capitalize(), [{"ORTH": dictionary[word][0]["accentuated"].capitalize()}])

def compatible(interpretation, lemma, tag, lemmas):
    if lemma in lemmas:
        pos_exists = False
        possible_poses = lemmas[lemma]["pos"]
        for i in range(len(possible_poses)):
            if possible_poses[i] in tag:
                pos_exists = True
                break
        if not (pos_exists):
            return False

    if interpretation == "canonical":
        return True
    if "plural" in interpretation and not ("Number=Plur" in tag):
        return False
    if "singular" in interpretation and not ("Number=Sing" in tag):
        return False
    if not ("nominative" in interpretation) and ("Case=Nom" in tag):
        return False
    if not ("genitive" in interpretation) and ("Case=Gen" in tag):
        return False
    if not ("dative" in interpretation) and ("Case=Dat" in tag):
        return False
    if not ("accusative" in interpretation) and ("Case=Acc" in tag):
        adj = False
        if "ADJ" in tag and "Animacy=Inan" in tag:
            adj = True
        if not adj:
            return False
    if not ("instrumental" in interpretation) and ("Case=Ins" in tag):
        return False
    if not ("prepositional" in interpretation) and not ("locative" in interpretation) and ("Case=Loc" in tag):
        return False
    if (("present" in interpretation) or ("future" in interpretation)) and ("Tense=Past" in tag):
        return False
    if (("past" in interpretation) or ("future" in interpretation)) and ("Tense=Pres" in tag):
        return False
    if (("past" in interpretation) or ("present" in interpretation)) and ("Tense=Fut" in tag):
        return False

    return True

# Гласные для проверки односложности
RUSSIAN_VOWELS = "аеёиоуыэюя"

def add_stress_single_vowel(word: str) -> str:
    """Если в слове ровно одна гласная, ставит знак ударения ` перед ней."""
    if not word:
        return word
    positions = [i for i, c in enumerate(word) if c.lower() in RUSSIAN_VOWELS]
    if len(positions) != 1:
        return word
    i = positions[0]
    return word[:i] + "`" + word[i:]

# а́е́и́о́у́ы́э́ю́я́
accented_vowels_map = {
    "а": "`а",
    "е": "`е",
    "и": "`и",
    "о": "`о",
    "у": "`у",
    "ы": "`ы",
    "э": "`э",
    "ю": "`ю",
    "я": "`я",
}
def accented_vowel_map_function(m):
    char = m.group(1)
    if char.lower() in accented_vowels_map:
        s = accented_vowels_map[char.lower()]
        if char.isupper():
            s = s[0] + s[1].upper()
        return s
    else:
        return char

def derive_single_accentuation(interpretations):
    if len(interpretations) == 0:
        return None
    res = interpretations[0]["accentuated"]
    
    for i in range(1, len(interpretations)):
        if interpretations[i]["accentuated"] != res:
            return None
    # поменять лагающий символ ударения на `
    res = re.sub(r"([а-яА-ЯёЁ])([^а-яА-ЯёЁ!?/s+.;:-])", accented_vowel_map_function, res)
    if "ё" in res or "Ё" in res:
        res = re.sub(r"([ёЁ])", "`" + r'\1', res)
        return res
    match = re.match("[бвгджзклмнпрстфхцчшщ]*[аеёиоуыэюя][бвгджзклмнпрстфхцчшщь]*", res)
    if match and match.regs[0][0] == match.pos and match.regs[0][1] == match.endpos:
        res = re.sub(r"([бвгджзклмнпрстфхцчшщ]*)([аеёиоуыэюя][бвгджзклмнпрстфхцчшщь]*)", r'\1' + "`" + r'\2', res)
    # Если после всех преобразований ударения нет, а гласная одна — проставляем автоматически
    if "`" not in res:
        res = add_stress_single_vowel(res)
    return res

def accentuate_word(word, lemmas):
    if ("tag" in word) and ("PROPN" in word["tag"]):
        return add_stress_single_vowel(word["token"])

    if word["is_punctuation"] or (not "interpretations" in word):
        return add_stress_single_vowel(word["token"])
    else:
        res = derive_single_accentuation(word["interpretations"])
        if not (res is None):
            return res
        else:
            compatible_interpretations = []
            for i in range(len(word["interpretations"])):
                if compatible(word["interpretations"][i]["form"], word["interpretations"][i]["lemma"], word["tag"], lemmas):
                    compatible_interpretations.append(word["interpretations"][i])
            res = derive_single_accentuation(compatible_interpretations)

            if not (res is None):
                return res
            else:
                new_compatible_interpretations = []
                for i in range(len(compatible_interpretations)):
                    if compatible_interpretations[i]["lemma"] == word["lemma"]:
                        new_compatible_interpretations.append(compatible_interpretations[i])
                res = derive_single_accentuation(new_compatible_interpretations)
                if not (res is None):
                    return res
                else:
                    return add_stress_single_vowel(word["token"])

def tokenize(text, wordforms):
    res = []
    doc = ru_nlp(text)
    for token in doc:
        if token.pos_ != 'PUNCT':
            word = {"token": token.text, "tag": token.tag_}
            if word["token"] in wordforms:
                word["interpretations"] = wordforms[word["token"]]
            if word["token"].lower() in wordforms:
                word["interpretations"] = wordforms[word["token"].lower()]
            word["lemma"] = token.lemma_
            word["is_punctuation"] = False
            word["uppercase"] = word["token"].upper() == word["token"]
            word["starts_with_a_capital_letter"] = word["token"][0].upper() == word["token"][0]
        else:
            word = {"token": token.text, "is_punctuation": True}
        word["whitespace"] = token.whitespace_
        res.append(word)
    return res

def process(text, wordforms, lemmas):
    res = ""
    words = tokenize(text, wordforms)
    for i in range(len(words)):
        accentuated = accentuate_word(words[i], lemmas)
        if "starts_with_a_capital_letter" in words[i] and words[i]["starts_with_a_capital_letter"]:
            accentuated = accentuated.capitalize()
        if "uppercase" in words[i] and words[i]["uppercase"]:
            accentuated = accentuated.upper()
        res += accentuated
        res += words[i]["whitespace"]
    return res

def preprocess_text(text):
    # оставляет только русский текст, одиночные пробелы и переносы строк
    result = re.sub(r"[^а-яА-ЯёЁ\s\n]|\t", "", text)
    result = re.sub(r" +", " ", result)
    result = re.sub(r"\n+", "\n", result)
    return result

def accentuate(text, text_is_preprocessed=False):
    if not text_is_preprocessed:
        text = preprocess_text(text)
    lemmas, wordforms = load()
    # introduce_special_cases_from_dictionary(wordforms)
    res = process(text, wordforms, lemmas)
    return res
