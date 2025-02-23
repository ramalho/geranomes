#!/usr/bin/env python3
import pickle
import random
import sys

from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path

MarkovModel = Mapping[str, list[str]]
Starters = list[str]

MODEL_PATH = Path("markov-model.pickle")
CONJUNCOES = "da das de di do dos du del von van"
CONJUNCOES += " " + CONJUNCOES.title()
CONJUNCOES = set(CONJUNCOES.split())


class MarkovNameMaker:
    def __init__(self, names: Iterable[str], order: int = 6):
        self.order = order
        self.end_char = ""
        if MODEL_PATH.exists():
            with open(MODEL_PATH, "rb") as f:
                self.model, self.starters = pickle.load(f)
        else:
            sys.stderr.write(f"Building model {MODEL_PATH}...\n")
            self.model, self.starters = self._build_model(names)
            with open(MODEL_PATH, "wb") as f:
                pickle.dump((self.model, self.starters), f)

    def _build_model(self, names: Iterable[str]) -> tuple[MarkovModel, Starters]:
        model: MarkovModel = defaultdict(list)
        starters: Starters = []

        for name in names:
            if self.end_char == "":
                self.end_char = name[-1]
            else:
                if self.end_char != name[-1]:
                    print("All names must have the same last character. Ex: \\n")
                    sys.exit(1)
            starters.append(name[: self.order])
            for i in range(len(name) - self.order):
                key = name[i : i + self.order]
                next_char = name[i + self.order]
                model[key].append(next_char)
        return model, starters

    def make_name(self) -> str:
        name = ""
        while len(name.split()) < 3: # restart if short name generated
            name = random.choice(self.starters)
            while True:
                key = name[-self.order :]
                if key not in self.model:
                    break
                next_char = random.choice(self.model[key])
                parts = name.split()
                if next_char == self.end_char:
                    if (len(parts) >= 4
                        and parts[-1] not in CONJUNCOES
                        and len(parts[-1]) > 1
                    ):
                        break
                    else:
                        next_char = " "
                elif (
                    next_char == " "
                    and parts[-1] not in CONJUNCOES
                    and len(parts[-1]) > 1
                    and len(parts) >= 4
                ):
                    break
                name += next_char
        return name.strip()


def make_names(names_file_path, quantity, order):
    with open(names_file_path) as f:
        names = f.readlines()
    maker = MarkovNameMaker(names, order)
    for _ in range(quantity):
        print(maker.make_name())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <how_many_names>")
        sys.exit(1)
    quantity = int(sys.argv[1])
    make_names("amostras/nomes.txt", quantity, 6)
