#!/usr/bin/env python3
import pickle
import random
import sys

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path

MarkovModel = Mapping[str, list[str]]
Starters = list[str]
PartCounts = Mapping[int, int]  # number of names by number of words

MODEL_PREFIX = 'model-order'
SAMPLE_PATH = Path('amostras')
NAMES_SAMPLE = SAMPLE_PATH / 'nomes-reais.txt'
ACCENTED_SAMPLE = SAMPLE_PATH / 'nomes-acentuados.tsv'
PREPOSITIONS = 'da das de di do dos du del von van'
PREPOSITIONS += ' ' + PREPOSITIONS.title()
PREFIXES = set(PREPOSITIONS.split())
BATCH_SIZE = 10000
MIN_PARTS = 2  # minimum number of words in a name


def model_path_for(order: int) -> Path:
    return Path(f'{MODEL_PREFIX}-{order}.pickle')


class MarkovNameMaker:
    def __init__(self, names: Iterable[str], order: int = 6):
        self.order = order
        self.end_char = '\n'
        model_path = model_path_for(order)
        if model_path.exists():
            with open(model_path, 'rb') as f:
                self.model, self.starters, part_counts = pickle.load(f)
        else:
            sys.stderr.write(f'Indexing {order}-grams to {model_path}...\n')
            self.model, self.starters, part_counts = self._build_model(names)
            with open(model_path, 'wb') as f:
                pickle.dump((self.model, self.starters, part_counts), f)
        self.part_sizes = [n for n in part_counts if n >= MIN_PARTS]
        self.part_weights = [part_counts[n] for n in self.part_sizes]

    def _build_model(self, names: Iterable[str]) -> tuple[MarkovModel, Starters, PartCounts]:
        model: MarkovModel = defaultdict(list)
        starters: Starters = []
        part_counts: Counter[int] = Counter()

        for name in names:
            if name[-1] != self.end_char:
                print(f'All names must end with {self.end_char!r}')
                sys.exit(1)
            starters.append(name[: self.order])
            part_counts[len(name.split())] += 1
            for i in range(len(name) - self.order):
                key = name[i : i + self.order]
                next_char = name[i + self.order]
                model[key].append(next_char)
        return model, starters, part_counts

    def target_parts(self) -> int:
        """Draw a number of words with the frequencies found in the sample"""
        return random.choices(self.part_sizes, self.part_weights)[0]

    def plausible_name(self, name: str, min_parts: int) -> bool:
        parts = name.split()
        return len(parts) >= min_parts and parts[-1] not in PREFIXES and len(parts[-1]) > 1

    def make_name(self) -> str:
        name = ''
        while len(name.split()) < MIN_PARTS:  # restart if short name generated
            target = self.target_parts()
            name = random.choice(self.starters)
            while True:
                key = name[-self.order :]
                if key not in self.model:
                    break
                next_char = random.choice(self.model[key])

                ok_to_end = self.plausible_name(name, target)
                if ok_to_end and next_char in (' ', self.end_char):
                    break
                elif next_char == self.end_char:
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
