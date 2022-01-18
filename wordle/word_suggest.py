import json
from typing import List, Set, Optional
import string


YES_INPUTS = ["y", "yes", "true", "1"]
GAME_TURNS = 6
WORD_LENGTH = 5


with open("words.json", "r") as f:
    DICTIONARY = json.load(f)


def ordinal(pos: int) -> str:
    pos_str = str(pos)
    if pos_str.endswith("1") and not pos_str.endswith("11"):
        return f"{pos_str}st"
    if pos_str.endswith("2") and not pos_str.endswith("12"):
        return f"{pos_str}nd"
    if pos_str.endswith("3") and not pos_str.endswith("13"):
        return f"{pos_str}rd"
    return f"{pos_str}th"


class LetterState:
    def __init__(
        self,
        letter: str,
        presence: Optional[bool] = None,
        known_locations: Set[int] = None,
        known_misses: Set[int] = None
    ) -> None:
        super().__init__()
        self.letter = letter
        self.presence = presence
        self.known_locations = known_locations or set()
        self.known_misses = known_misses or set()

    def known_location_state(self, pos: int) -> bool:
        return pos in self.known_locations or pos in self.known_misses

    def matches_word(self, word: str) -> bool:
        # Presence check
        if self.presence is not None and (self.letter in word) != self.presence:
            return False
        # Location checks
        if not all(word[loc] == self.letter for loc in self.known_locations):
            return False
        if any(word[loc] == self.letter for loc in self.known_misses):
            return False
        return True

    def add_known_location(self, pos: int) -> None:
        self.known_locations.add(pos)

    def add_known_miss(self, pos: int) -> None:
        self.known_misses.add(pos)


class WordleState:
    def __init__(self) -> None:
        self.state = {
            letter: LetterState(letter)
            for letter in string.ascii_lowercase
        }

    def set_presence(self, letter: str, presence: bool) -> None:
        self.state[letter].presence = presence

    def add_known_miss(self, letter: str, not_pos: int) -> None:
        self.state[letter].add_known_miss(not_pos)

    def add_known_location(self, letter: str, pos: int) -> None:
        self.state[letter].add_known_location(pos)

    def build_state(self) -> None:
        next_word = input("What word have you entered? ")
        for pos, letter in enumerate(next_word):
            # Ask about presence
            if self.state[letter].presence is None:
                matched = input(f"Did the {ordinal(pos+1)} letter, \"{letter}\" match at all? [Y/N] ")
                self.set_presence(letter, matched.lower() in YES_INPUTS)
            # Ask about location
            if self.state[letter].presence is True and not self.state[letter].known_location_state(pos):
                correct_loc = input(f"Was the {ordinal(pos+1)} letter, \"{letter}\" in the right location? [Y/N] ")
                if correct_loc.lower() in YES_INPUTS:
                    self.add_known_location(letter, pos)
                else:
                    self.add_known_miss(letter, pos)
        return

    def remaining_words(self) -> List[str]:
        matching = []
        for word in DICTIONARY:
            if all(letter_state.matches_word(word) for letter_state in self.state.values()):
                matching.append(word)
        return matching

    def word_would_leave(self, word: str, other_words: List[str]) -> int:
        remaining = other_words[:]
        for pos, letter in enumerate(word):
            if self.state[letter].presence is True:
                if pos in self.state[letter].known_locations:
                    continue
                remaining = [w for w in remaining if w[pos] != letter]
            else:
                remaining = [w for w in remaining if letter not in w]
        return len(remaining)

    def suggest_matching(self, count: int = -1) -> None:
        all_matching = self.remaining_words()
        print(f"There are {len(all_matching)} matching words")
        print(f"Matching words: ")
        match_counts = {
            word: self.word_would_leave(word, all_matching)
            for word in all_matching
        }
        for match, count in sorted(match_counts.items(), key=lambda pair: pair[1])[:count]:
            print(f"{match}: Could rule out {len(all_matching) - count}")

    def game_won(self) -> bool:
        return sum(
            len(letter_state.known_locations)
            for letter_state in self.state.values()
        ) == WORD_LENGTH

    def winning_word(self) -> Optional[str]:
        word_letters: List[Optional[str]] = [None] * WORD_LENGTH
        for letter_state in self.state.values():
            for loc in letter_state.known_locations:
                word_letters[loc] = letter_state.letter
        if None in word_letters:
            return None
        return "".join(word_letters)


def play():
    state = WordleState()
    print("For your first word, may I suggest:")
    state.suggest_matching(10)
    turn = 1
    while not state.game_won() and turn < GAME_TURNS:
        state.build_state()
        state.suggest_matching()
        turn += 1
    if state.game_won():
        print("You won, congrats")
        print(f"The word was: {state.winning_word()}")
    else:
        print("You lost.")
        remaining_words = state.remaining_words()
        if len(remaining_words) > 1:
            print(f"There were {len(remaining_words)} remaining words")
        elif len(remaining_words) == 1:
            print(f"There was one word left: {remaining_words[0]}")
        else:
            print("I cannot find a valid solution")


if __name__ == "__main__":
    play()
