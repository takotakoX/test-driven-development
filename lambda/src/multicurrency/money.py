from __future__ import annotations
import abc
import dataclasses


class Expression(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def times(self, multiplier: int):
        raise NotImplementedError()

    @abc.abstractmethod
    def plus(self, addend: Expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def reduce(self, bank: Bank, to_currency: str):
        raise NotImplementedError()


@dataclasses.dataclass
class Sum(Expression):
    augend: Expression
    addend: Expression

    def times(self, multiplier: int):
        return Sum(self.augend.times(multiplier), self.addend.times(multiplier))

    def plus(self, addend: Expression):
        return Sum(self, addend)

    def reduce(self, bank: Bank, to_currency: str):
        amount = self.augend.reduce(bank, to_currency)._amount + self.addend.reduce(bank, to_currency)._amount
        return Money(amount, to_currency)


@dataclasses.dataclass
class Money(Expression):
    _amount: int
    _currency: str

    @staticmethod
    def dollar(amount: int) -> Money:
        return Money(amount, "USD")

    @staticmethod
    def franc(amount: int) -> Money:
        return Money(amount, "CHF")

    def __eq__(self, __o: object) -> bool:
        if isinstance((money := __o), Money):
            return self._amount == money._amount and self._currency == money._currency
        else:
            return False

    def times(self, multiplier: int) -> Expression:
        return Money(self._amount * multiplier, self._currency)

    def plus(self, addend: Expression) -> Expression:
        return Sum(self, addend)

    def reduce(self, bank: Bank, to_currency: str):
        rate = bank.rate(self._currency, to_currency)
        return Money(self._amount / rate, to_currency)

    def currency(self) -> str:
        return self._currency


@dataclasses.dataclass
class Pair:
    __from_currency: str
    __to_currency: str

    def __eq__(self, __o: object) -> bool:
        if isinstance((pair := __o), Pair):
            return self.__dict__ == pair.__dict__
        else:
            return False

    def __hash__(self) -> int:
        return 0


@dataclasses.dataclass
class Bank:
    __rates: dict = dataclasses.field(default_factory=dict)

    def reduce(self, source: Expression, to_currency: str):
        return source.reduce(self, to_currency)

    def add_rate(self, from_currency: str, to_currency: str, rate: int):
        self.__rates[Pair(from_currency, to_currency)] = rate

    def rate(self, from_currency: str, to_currency: str):
        if from_currency == to_currency:
            return 1
        return self.__rates[Pair(from_currency, to_currency)]
