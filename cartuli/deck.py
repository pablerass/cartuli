"""Deck module."""
from copy import deepcopy
from pathlib import Path

from .card import Card, CardImage
from .measure import Size


class Deck:
    # TUNE: Use dataclasses
    def __init__(self, cards: list[Card] = None, /, name: str = '',
                 back: Path | str | CardImage = None, size: Size = None):
        if isinstance(back, Path) or isinstance(back, str):
            if size is None:
                raise ValueError("card size must be specified when not using a CardImage as back")
            back = CardImage(back, size)
        elif isinstance(back, CardImage):
            if size is None:
                size = back.size
            elif size != back.size:
                raise ValueError("back image is not of the same size as the card")
        self.__back = back
        self.__size = size

        self.__cards = []
        if cards is not None:
            self.add_cards(cards)

        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def size(self) -> Size:
        return self.__size

    @property
    def cards(self) -> list[Card]:
        return tuple(self.__cards)

    @property
    def back(self) -> CardImage:
        return self.__back

    def __add_card(self, card: Card, index: int = None):
        if self.__size is None:
            self.__size = card.size

        if card.size != self.size:
            raise ValueError(f"Card size {card.size} distinct from deck {self.size} card size")
        if self.back is not None and card.back is not None and self.back != card.back:
            raise ValueError("Card back image is different from the deck one")

        if self.back is not None:
            try:
                card.back = self.back
            except AttributeError:
                raise ValueError("Card back image can not be set to deck one")

        if index is None:
            self.__cards.append(card)
        else:
            self.__cards.insert(card)

    @property
    def two_sided(self) -> bool:
        if not self.__cards:
            raise AttributeError("Deck is empty, is not yet one sided or two sided ")
        return self.__cards[0].two_sided

    def __len__(self):
        return len(self.__cards)

    def add_cards(self, cards: Card | list[Card], index: int = None):
        if isinstance(cards, Card):
            self.__add_card(cards, index)
        else:
            if index is None:
                for card in cards:
                    self.__add_card(card)
            else:
                for n, card in enumerate(cards):
                    self.__add_card(card, index + n)
