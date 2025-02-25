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
PREPOSITIONS = 'da das de di do dos du del von van'
PREPOSITIONS += ' ' + PREPOSITIONS.title()
PREFIXES = set(PREPOSITIONS.split())


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
        return len(parts) >= 4 and parts[-1] not in PREFIXES and len(parts[-1]) > 1

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
                if next_char == ' ' and ok_to_end:
                    break
                elif next_char == self.end_char:
                    if ok_to_end:
                        break
                    else:
                        next_char = ' '
                name += next_char
        return name.strip()


def make_names(sample_file_path, quantity, order):
    with open(sample_file_path) as sample:
        maker = MarkovNameMaker(sample, order)
    writing_to_file = not sys.stdout.isatty()
    for i in range(quantity):
        print(maker.make_name())
        if writing_to_file and i % 1000 == 0:
            sys.stderr.write(f'\r{i:_} names generated')
            sys.stderr.flush()
    if not sys.stdout.isatty():
        sys.stderr.write('\r{" "*80}\r')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <how_many_names>')
        sys.exit(1)
    quantity = int(sys.argv[1])
    make_names('amostras/nomes.txt', quantity, 6)
