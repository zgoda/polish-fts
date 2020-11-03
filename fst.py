"""Polish stemmer using Finite State Transducers

Original code: https://github.com/eugeniashurko/polish-stem
License: ???
"""

from csv import reader
from itertools import repeat


def train_file_handler(filename):
    train = []
    target = []
    with open(filename, encoding='iso-8859-2', newline='') as csvfile:
        for row in reader(csvfile):
            train.append(row[0])
            target.append(row[1])
    return (train, target)


def test_file_handler(filename):
    with open(filename, encoding='iso-8859-2', newline='') as csvfile:
        return [r[0] for r in reader(csvfile)]


def output_file_handler(out):
    out_file = input("Enter the file path for classified Test Data -> ")
    with open(out_file, 'w') as f:
        f.write('\n'.join(out))


def preproc(words_list, sub):
    for i in range(len(words_list)):
        for let, numb in sub.items():
            words_list[i] = words_list[i].replace(let, str(numb))
    v = {
        'ia': '`a',
        'ie': '`e',
        'i\u0119': '`\u0119',
        'io': '`o',
        'i\u0105': '`\u0105',
        'iu': '`u',
        'i\u00f3': '`\u00f3'
    }
    for i in range(len(words_list)):
        for soft, code in v.items():
            words_list[i] = words_list[i].replace(soft, code)
    return words_list


def back_preproc(words_list, sub):
    for i in range(len(words_list)):
        words_list[i] = words_list[i].replace('`', 'i')
        sub = {v: k for k, v in sub.items()}
    for i in range(len(words_list)):
        for let, numb in sub.items():
            words_list[i] = words_list[i].replace(str(let), numb)
    return words_list


def rplc(word, index, symb):
    p1 = word[0:index] + symb
    p2 = word[index + 1:len(word)]
    word = p1 + p2
    return word


def part_suffix(word, suffix):
    s_len = len(suffix)
    w_len = len(word)
    if word[(w_len - s_len):w_len] == suffix:
        word = word[0:(w_len - s_len)] + '^' + suffix
    return word


def one_sylab(word):
    vowels = ['a', '\u0105', 'e', '\u0119', 'i', 'o', '\u00f3', 'u', 'y']
    vow = 0
    for i in range(len(word)):
        if word[i] in vowels:
            vow += 1
    return vow == 1


def remove_suffix(word):
    vowels = ['a', '\u0105', 'e', '\u0119', 'i', 'o', '\u00f3', 'u', 'y']
    if word.find('^') > -1:
        if (word[word.find('^') + 1] == 'i'):
            if word[word.find('^') - 1] in vowels and one_sylab(word[0:word.find('^')]):
                word = word[0:word.find('^')] + 'j' + word[word.find('^'):len(word)]
        word = word[0: word.find('^')]
    return word


def apply_alternation(word, alt):
    target = alt
    caret_p = word.find('^')
    if caret_p > -1:
        a = word[0:caret_p - len(alt)] + target + word[caret_p:len(word)]
    else:
        a = word[0:len(word) - len(target)] + target
    word = a
    return word


def has_suffix(word, suffix):
    res = -1
    caret_p = word.find('^')
    if caret_p > 0:
        start = caret_p + 1
        s = word[start:len(word)]
        if s == suffix and start + len(s) == len(word):
            res = start
    return res


def no_suffix(word):
    if word.find('^') > 0:
        return False
    return True


class Stemmer:

    def __init__(self):
        self.reg_end = []
        self.sub = {
            'ch': 1,
            'cz': 2,
            'dz': 3,
            'd\u017a': 4,
            'd\u017c': 5,
            'rz': 6,
            'sz': 7,
        }
        self.alternation = {}
        self.morph_changes = {}

    def _suffix_recognition(self, train, target):
        train = preproc(train, self.sub)
        target = preproc(target, self.sub)
        ends = []
        for i in range(len(train)):
            dif = len(train[i]) - len(target[i])
            if dif > 0:
                if target[i][len(target[i]) - 1] == train[i][len(target[i]) - 1]:
                    ends.append(train[i][len(target[i]):len(train[i])])
        ends = set(ends)
        ends = list(ends)
        ends = sorted(ends, key=len, reverse=True)
        self.reg_end = ends

    def _statistics(self, train):
        count = list(repeat(0, len(self.reg_end)))
        self.stat = dict(zip(self.reg_end, count))
        for t in train:
            for e in self.reg_end:
                if has_suffix(t, e) > -1:
                    self.stat[e] += 1
        for k in self.stat.keys():
            self.stat[k] = float(self.stat[k]) / float(len(train))
        # h = sorted(self.stat, key=lambda x: self.stat[x], reverse=True)

    def _exact_rules(self, train, target):
        alternation = {}
        morph_changes = {}
        for j in range(len(self.reg_end)):
            e = self.reg_end[j]
            ast = []
            a = {}
            for i in range(len(train)):
                s_index = has_suffix(train[i], e)
                si_1 = s_index - 1
                si_2 = s_index - 2
                si_3 = s_index - 3
                if s_index > 0:
                    if si_2 < len(target[i]):
                        if (
                            train[i][si_2].islower()
                            and target[i][si_2].islower()
                            or train[i][si_2].isdigit()
                        ):
                            if train[i][si_2] != target[i][si_2]:
                                if train[i][si_3] != target[i][si_3]:
                                    a.update({
                                        train[i][si_3:si_1]: target[i][si_3:si_1]
                                    })
                                    ast.append((
                                        train[i][si_3:si_1], target[i][si_3:si_1]
                                    ))
                                else:
                                    a.update({train[i][si_2]: target[i][si_2]})
                                    ast.append((train[i][si_2], target[i][si_2]))
                            elif (train[i][si_3] != target[i][si_3]):
                                a.update({
                                    train[i][si_3:si_1]: target[i][si_3:si_1]
                                })
                                ast.append((
                                    train[i][si_3:si_1], target[i][si_3:si_1]
                                ))
                else:
                    if len(train[i]) == len(target[i]):
                        len_t = len(train[i])
                        if train[i][len_t - 2] != target[i][len_t - 2]:
                            morph_changes.update({
                                train[i][len_t - 2]: target[i][len_t - 2]
                            })
            alt = set(ast)
            alt = list(alt)
            count = list(repeat(0, len(alt)))
            for k in range(len(alt)):
                for i in range(len(ast)):
                    if alt[k] == ast[i]:
                        count[k] += 1
            delete = []
            for k in range(len(alt) - 1):
                for u in range(1, len(alt), 1):
                    if k != u:
                        if (alt[k][0] == alt[u][0]):
                            if count[k] > count[u]:
                                delete.append(u)
                            else:
                                delete.append(k)
            delete = set(delete)
            delete = list(delete)
            for k in range(len(delete) - 1, -1, -1):
                del alt[delete[k]]
            alternation.update({e: dict(alt)})
        self.morph_changes = morph_changes
        self.alternation = alternation
        return alternation

    def _train_stemmer(self, train, target):
        tr = list(train)
        ta = list(target)
        self._suffix_recognition(tr, ta)
        intermidiate = self._suffix_part(tr)
        self._statistics(intermidiate)
        self._exact_rules(intermidiate, ta)

    def _suffix_remove(self, test):
        for i in range(len(test)):
            test[i] = remove_suffix(test[i])
        return test

    def _suffix_part(self, test):
        for i in range(len(test)):
            c_suffix = []
            for suffix in self.reg_end:
                if len(suffix) != 0:
                    if test[i][len(test[i]) - 1] == suffix[len(suffix) - 1]:
                        c_suffix.append(suffix)
            rplcd = False
            for s in c_suffix:
                temp = test[i]
                test[i] = part_suffix(test[i], s)
                if temp != test[i]:
                    rplcd = True
                if rplcd is True:
                    break
        return test

    def _apply_rules(self, test):
        endings = self.reg_end
        for i in range(len(test)):
            if not no_suffix(test[i]):
                for e in endings:
                    s_index = has_suffix(test[i], e)
                    si_1 = s_index - 1
                    si_2 = s_index - 2
                    si_3 = s_index - 3
                    if (s_index > 0):
                        if test[i][si_3:si_1] in self.alternation[e]:
                            test[i] = apply_alternation(
                                test[i], self.alternation[e][test[i][si_3:si_1]]
                            )
                        elif test[i][si_2:si_1] in self.alternation[e]:
                            test[i] = apply_alternation(
                                test[i], self.alternation[e][test[i][si_2:si_1]]
                            )
            else:
                if test[i][len(test[i]) - 2] == 'e':
                    if test[i][len(test[i]) - 3] == '`':
                        test[i] = rplc(test[i], len(test[i]) - 3, '')
                        test[i] = rplc(test[i], len(test[i]) - 2, '')
                    else:
                        test[i] = rplc(test[i], len(test[i]) - 2, '')
                elif test[i][len(test[i]) - 2] in self.morph_changes:
                    test[i] = rplc(
                        test[i],
                        len(test[i]) - 2,
                        self.morph_changes[test[i][len(test[i]) - 2]]
                    )
        return test

    def _exact_stem(self, test):
        test = preproc(test, self.sub)
        intermidiate = self._suffix_part(test)
        intermidiate = self._apply_rules(intermidiate)
        stem = self._suffix_remove(intermidiate)
        stem = back_preproc(stem, self.sub)
        return stem


def main():
    train, target = train_file_handler()
    stemmer = Stemmer()
    stemmer._train_stemmer(train, target)

    print("Stemmer application on test data...")
    test_data = test_file_handler()

    out = stemmer._exact_stem(test_data)

    output_file_handler(out)


if __name__ == "__main__":
    main()
