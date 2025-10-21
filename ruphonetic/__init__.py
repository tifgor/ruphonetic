import re
from . import transcriptor, utils
from collections import Counter

def transcribe(text, simplify=False):
    return transcriptor.transcribe(text, simplify=simplify)

def sound_spectre(text, input_is_transcribed=False, show_plot=False, show_pie_plot=False, show_bar_plot=False):
    if not input_is_transcribed:
      text = transcribe(text, simplify=True)
    sounds = re.findall(r"[а-я]'*", text)
    result = Counter(sounds)
    for sound in result:
        result[sound] = result[sound] / len(sounds)

    utils.show_plots(result, show_plot, show_pie_plot, show_bar_plot)

    return result

def sound_spectre_grouped(text, input_is_transcribed=False, show_plot=False, show_pie_plot=False, show_bar_plot=False):
    if not input_is_transcribed:
      text = transcribe(text, simplify=True)
    whistling_count = len(re.findall(r"з[^']|з'|с[^']|с'", text))
    hissing_count = len(re.findall(r"ж|ш|щ'|ч", text))
    hard_count = len(re.findall(r"ц|ш|ж|н[^']|б[^']|в[^']|г[^']|д[^']|з[^']|к[^']|л[^']|м[^']|п[^']|р[^']|с[^']|т[^']|ф[^']|х[^']", text))
    soft_count = len(re.findall(r"й|ч|щ'|б'|в'|г'|д'|з'|к'|л'|м'|н'|п'|р'|с'|т'|ф'|х'", text))
    sum_count = whistling_count + hissing_count + hard_count + soft_count

    result = {"свистящие": whistling_count / sum_count, "шипящие": hissing_count / sum_count, "твердые": hard_count / sum_count, "мягкие": soft_count / sum_count}
    utils.show_plots(result, show_plot, show_pie_plot, show_bar_plot)

    return result

def sound_spectre_grouped_custom(text, input_is_transcribed=False, show_plot=False, show_pie_plot=False, show_bar_plot=False):
    if not input_is_transcribed:
      text = transcribe(text, simplify=True)

    print(text)
    input_str = str()
    group_num = 1
    groups = dict()
    entries_sum = 0
    print("Введите группы звуков, разделяя звуки знаком |, без пробелов. Напишите /s если Вы ввели все группы.")
    while(1):
        print(f"Группа {group_num}: ")
        input_str = input()
        if "/s" in input_str:
            break
        if not re.match(r"(([а-я])+(')?)+(\|(([а-я])+(')?)+)*", input_str):
            print("Неверный ввод")
        else:
            groups[group_num] = dict()
            groups[group_num]['input'] = input_str
            groups[group_num]['regexp'] = re.sub(r"(([а-я])+(')?)+", r"\1" + "([^']|$)", input_str)
            sounds = re.findall(r"([а-я])+(')?([а-я])*", input_str)
            if len(set(sounds)) != len(sounds):
                print("В группах не могут повторяться одни и те же звуки.")
                continue
            groups[group_num]['entries'] = re.findall(rf"{groups[group_num]['regexp']}", text)
            entries_sum += len(groups[group_num]['entries'])

            group_num += 1

    result = dict()
    for group_num in groups:
        result[groups[group_num]['input']] = len(groups[group_num]['entries']) / entries_sum if entries_sum else 0

    utils.show_plots(result, show_plot, show_pie_plot, show_bar_plot)
    
    return result

def sound_spectre_dynamic_position(text, word_amount: int, input_is_transcribed=False):
    if not input_is_transcribed:
      text = transcribe(text, simplify=True)
    words = text.replace("\n", " ").split(" ")
    if word_amount > len(words):
        raise IndexError("Word amount can't be greater than number of words in string")
    result = dict()
    i = 0
    while i + word_amount <= len(words):
        step_dict = dict()
        substring = " ".join(words[i:i+word_amount])
        substring_spectre = sound_spectre(substring, input_is_transcribed=True)
        step_dict['substring'] = substring
        step_dict['result'] = substring_spectre
        result[i] = step_dict
        i += 1

    return result

def sound_spectre_dynamic_length(text, input_is_transcribed=False):
    if not input_is_transcribed:
      text = transcribe(text, simplify=True)
    words = text.replace("\n", " ").split(" ")
    result = dict()
    i = 1
    while i < len(words):
        step_dict = dict()
        substring = " ".join(words[0:i])
        substring_spectre = sound_spectre(substring, input_is_transcribed=True)
        step_dict['substring'] = substring
        step_dict['result'] = substring_spectre
        result[i] = step_dict
        i += 1

    return result
