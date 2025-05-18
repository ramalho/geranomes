#!/usr/bin/env python3
import pickle
import random
import sys

from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path

MarkovModel = Mapping[str, list[str]]
Starters = list[str]

MODEL_PATH = Path('markov-model.pickle')
SAMPLE_PATH = Path('amostras')
NAMES_SAMPLE = SAMPLE_PATH / 'nomes-reais.txt'
ACCENTED_SAMPLE = SAMPLE_PATH / 'nomes-acentuados.tsv'
PREPOSITIONS = 'da das de di do dos du del von van'
PREPOSITIONS += ' ' + PREPOSITIONS.title()
PREFIXES = set(PREPOSITIONS.split())
BATCH_SIZE = 10000


class MarkovNameMaker:
    def __init__(self, names: Iterable[str], order: int = 6):
        self.order = order
        self.end_char = ''
        if MODEL_PATH.exists():
            with open(MODEL_PATH, 'rb') as f:
                self.model, self.starters = pickle.load(f)
        else:
            sys.stderr.write(f'Indexing {order}-grams {MODEL_PATH}...\n')
            self.model, self.starters = self._build_model(names)
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump((self.model, self.starters), f)

    def _build_model(self, names: Iterable[str]) -> tuple[MarkovModel, Starters]:
        model: MarkovModel = defaultdict(list)
        starters: Starters = []

        for name in names:
            if self.end_char == '':
                self.end_char = name[-1]
            else:
                if self.end_char != name[-1]:
                    print('All names must have the same last character. Ex: \\n')
                    sys.exit(1)
            starters.append(name[: self.order])
            for i in range(len(name) - self.order):
                key = name[i : i + self.order]
                next_char = name[i + self.order]
                model[key].append(next_char)
        return model, starters

    def plausible_name(self, name: str) -> bool:
        parts = name.split()
        return len(parts) >= 3 and parts[-1] not in PREFIXES and len(parts[-1]) > 1

    def make_name(self) -> str:
        name = ''
        while len(name.split()) < 3:  # restart if short name generated
            name = random.choice(self.starters)
            while True:
                key = name[-self.order :]
                if key not in self.model:
                    break
                next_char = random.choice(self.model[key])

                ok_to_end = self.plausible_name(name)
                if ok_to_end and next_char == ' ' and random.randrange(3) < 2:
                    break
                elif next_char == self.end_char:
                    if ok_to_end:
                        break
                    else:
                        next_char = ' '
                name += next_char
        return name.strip()


type AccentProbabilities = dict[str, tuple[float, str]]


def load_accented_names() -> AccentProbabilities:
    accent_prob: AccentProbabilities = {}
    with open(ACCENTED_SAMPLE, encoding='utf8') as fp:
        for line in fp:
            prob_str, name, name_ac = line.strip().split()
            prob = float(prob_str)
            accent_prob[name] = prob, name_ac
    return accent_prob


def add_accents(name:str, accent_prob: AccentProbabilities) -> str:
    parts = name.split()
    changed = False
    for i, part in enumerate(parts):
        if part in accent_prob:
            prob, name_ac = accent_prob[part]
            if prob > random.random():
                parts[i] = name_ac
                changed = True
    if changed:
        return ' '.join(parts)
    else:
        return name


def make_names(sample_file_path, quantity, ascii_only, order=6):
    with open(sample_file_path) as sample:
        maker = MarkovNameMaker(sample, order)
    writing_to_file = not sys.stdout.isatty()
    accented_names = None if ascii_only else load_accented_names()

    for i in range(quantity):
        name = maker.make_name()
        if accented_names:
            name = add_accents(name, accented_names)
        print(name)
        if writing_to_file and i % BATCH_SIZE == 0:
            sys.stderr.write(f'\r{i:_} names generated')
            sys.stderr.flush()
    if writing_to_file:
        sys.stderr.write(f'\r{" "*80}\r')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <how_many_names>')
        sys.exit(1)
    if '-a' in sys.argv:
        ascii_only = True
        del sys.argv[sys.argv.index('-a')]
    else:
        ascii_only = False
    quantity = int(sys.argv[1])
    make_names(NAMES_SAMPLE, quantity, ascii_only)
