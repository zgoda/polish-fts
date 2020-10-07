"""Implementation of Porter-based stemmer for Polish language.

Original code: https://github.com/Tutanchamon/pl_stemmer
License: MIT
"""

from typing import List


def stem(text: str) -> List[str]:
    stems = []
    for word in text.split():
        word = word.lower()
        stem = word[:]
        stem = remove_nouns(stem)
        stem = remove_diminutive(stem)
        stem = remove_adjective_ends(stem)
        stem = remove_verbs_ends(stem)
        stem = remove_adverbs_ends(stem)
        stem = remove_plural_forms(stem)
        stem = remove_general_ends(stem)
        stems.append(stem)
    return stems


def remove_general_ends(word: str) -> str:
    if len(word) > 4:
        if word[-2:] in {"ia", "ie"}:
            return word[:-2]
        if word[-1:] in {"u", "ą", "i", "a", "ę", "y", "ę", "ł"}:
            return word[:-1]
    return word


def remove_diminutive(word: str) -> str:
    if len(word) > 6:
        if word[-5:] in {"eczek", "iczek", "iszek", "aszek", "uszek"}:
            return word[:-5]
        if word[-4:] in {"enek", "ejek", "erek"}:
            return word[:-2]
    if len(word) > 4:
        if word[-2:] in {"ek", "ak"}:
            return word[:-2]
    return word


def remove_verbs_ends(word: str) -> str:
    if len(word) > 5 and word.endswith("bym"):
        return word[:-3]
    if len(word) > 5 \
            and word.endswith(("esz", "asz", "cie", "eść", "aść", "łem", "amy", "emy")):
        return word[:-3]
    if len(word) > 3 and word[-3:] in {"esz", "asz", "eść", "aść"}:
        return word[:-2]
    if len(word) > 3 and word[-2:] in {"aj"}:
        return word[:-1]
    if len(word) > 3 and word[-2:] in {"eć", "ać", "em", "am", "ał", "ił", "ić", "ąc"}:
        return word[:-2]
    return word


def remove_nouns(word: str) -> str:
    if len(word) > 7 and word[-5:] in {"zacja", "zacją", "zacji"}:
        return word[:-4]
    if len(word) > 6 \
            and word.endswith(
                ("acja", "acji", "acją", "tach", "anie", "enie", "eniu", "aniu")
            ):
        return word[:-4]
    if len(word) > 6 and word.endswith("tyka"):
        return word[:-2]
    if len(word) > 5 and word[-3:] in {"ach", "ami", "nia", "niu", "cia", "ciu"}:
        return word[:-3]
    if len(word) > 5 and word[-3:] in {"cji", "cja", "cją"}:
        return word[:-2]
    if len(word) > 5 and word[-2:] in {"ce", "ta"}:
        return word[:-2]
    return word


def remove_adjective_ends(word: str) -> str:
    if len(word) > 7 \
            and word.startswith("naj") and word.endswith(("sza", "sze", "szy")):
        return word[3:-3]
    if len(word) > 7 and word.startswith("naj") and word.endswith("szych"):
        return word[3:-5]
    if len(word) > 6 and word.endswith(("czny", "czna", "czne")):
        return word[:-4]
    if len(word) > 5 and word[-3:] in {"owy", "owa", "owe", "ych", "ego"}:
        return word[:-3]
    if len(word) > 5 and word[-2:] in {"ej"}:
        return word[:-2]
    return word


def remove_adverbs_ends(word: str) -> str:
    if len(word) > 4 and word[:-3] in {"nie", "wie"}:
        return word[:-2]
    if len(word) > 4 and word.endswith("rze"):
        return word[:-2]
    return word


def remove_plural_forms(word: str) -> str:
    if len(word) > 4 and (word.endswith(u"ów") or word.endswith("om")):
        return word[:-2]
    if len(word) > 4 and word.endswith("ami"):
        return word[:-3]
    return word
