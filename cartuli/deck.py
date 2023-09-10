"""Deck module."""
from pathlib import Path
from typing import Iterable

from .card import Card, CardImage
from .measure import Size


class Deck:
    # TUNE: Use dataclasses
    def __init__(self, cards: Card | Iterable[Card] = None, /, name: str = '',
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

        self.__name = name

        self.__cards = []
        if cards is not None:
            self.add(cards)

    def __update_card_image_names(self, name: str):
        if not name:
            return
        for num, card in enumerate(self.cards):
            if not card.name:
                card.name = f'{name}_{num}'

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        if not name or name is None:
            return
        if self.__name:
            raise AttributeError("can't set attribute 'name' if already set")
        self.__update_card_image_names(name)
        self.__name = name

    @property
    def size(self) -> Size:
        if self.__size is None:
            raise AttributeError('size is not yet available as no card has been added')
        return self.__size

    @property
    def cards(self) -> list[Card]:
        return tuple(self.__cards)

    @property
    def default_back(self) -> CardImage:
        return self.__default_back

    @property
    def two_sided(self) -> bool:
        """Return if deck cards have two sides."""
        if not self.__cards:
            raise AttributeError("Deck is empty, is not yet one sided or two sided ")
        return self.__cards[0].two_sided

    def __add_card(self, card: Card):
        # TODO: Name cards if they are not already named
        if self.__size is None:
            self.__size = card.size

        if card.size != self.size:
            raise ValueError(f"Card size {card.size} distinct from deck {self.size} card size")

        if self.default_back is not None:
            if not card.back:
                card.back = self.default_back

        if self.__name and not card.name:
            card.name = f'{self.name}_{len(self)+1}'

        self.__cards.append(card)

    def add(self, cards: Card | Iterable[Card]):
        if isinstance(cards, Card):
            cards = [cards]
        for card in cards:
            self.__add_card(card)

    def __len__(self):
        return len(self.__cards)

    def __str__(self):
        if self.name:
            return self.name
        return super().__str__()
