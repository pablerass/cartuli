"""Deck module."""
from pathlib import Path

from .card import Card, CardImage
from .measure import Size


class Deck:
    # TUNE: Use dataclasses
    def __init__(self, cards: list[Card] = None, /, name: str = '',
                 default_back: Path | str | CardImage = None, size: Size = None):
        if isinstance(default_back, Path) or isinstance(default_back, str):
            if size is None:
                raise ValueError("card size must be specified when not using a CardImage as default back")
            default_back = CardImage(default_back, size)
        elif isinstance(default_back, CardImage):
            if size is None:
                size = default_back.size
            elif size != default_back.size:
                raise ValueError("default back image is not of the same size as the deck")
        self.__default_back = default_back
        self.__size = size

        self.__cards = []
        if cards is not None:
            self.add(cards)

        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def size(self) -> Size:
        if self.__size is None:
            # TUNE: Find better error test
            raise AttributeError('size is not yet set')
        return self.__size

    @property
    def cards(self) -> list[Card]:
        return tuple(self.__cards)

    @property
    def default_back(self) -> CardImage:
        return self.__default_back

    @property
    def two_sided(self) -> bool:
        if not self.__cards:
            raise AttributeError("Deck is empty, is not yet one sided or two sided ")
        return self.__cards[0].two_sided

    def __len__(self):
        return len(self.__cards)

    def __add_card(self, card: Card, index: int = None):
        if self.__size is None:
            self.__size = card.size

        if card.size != self.size:
            raise ValueError(f"Card size {card.size} distinct from deck {self.size} card size")

        if self.default_back is not None:
            try:
                card.back = self.default_back
            except AttributeError:
                # Back image is already set
                pass

        if index is None:
            self.__cards.append(card)
        else:
            self.__cards.insert(card)

    def add(self, cards: Card | list[Card], index: int = None):
        if isinstance(cards, Card):
            self.__add_card(cards, index)
        else:
            if index is None:
                for card in cards:
                    self.__add_card(card)
            else:
                for n, card in enumerate(cards):
                    self.__add_card(card, index + n)
