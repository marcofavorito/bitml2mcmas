"""Data validation."""

import collections
import dataclasses
import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Collection, Sequence
from decimal import Decimal
from numbers import Number
from typing import (
    AbstractSet,
    Annotated,
    Any,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from bitml2mcmas.helpers.misc import assert_, sequence_like

T = TypeVar("T")
GenericCollection = Union[list, tuple, set, frozenset]


class _Processor(ABC):
    @abstractmethod
    def process(self, value: Any) -> Any:
        raise NotImplementedError


def flatten_union(allowed_types: Sequence[type]) -> Sequence[type]:
    new_allowed_types: list[type] = []
    for t in allowed_types:
        if get_origin(t) is Union:
            new_allowed_types.extend(get_args(t))
        else:
            new_allowed_types.append(t)
    return new_allowed_types


@dataclasses.dataclass(frozen=True)
class Gt(_Processor):
    value: Number

    def process(self, value: Any) -> Any:
        if value > self.value:
            raise ViolatedNumberConstraintError(value, ">", self.value)
        return value


@dataclasses.dataclass(frozen=True)
class Gte(_Processor):
    value: Number

    def process(self, value: Any) -> Any:
        if value >= self.value:
            raise ViolatedNumberConstraintError(value, ">=", self.value)
        return value


@dataclasses.dataclass(frozen=True)
class Lt(_Processor):
    value: Number

    def process(self, value: Any) -> Any:
        if value < self.value:
            raise ViolatedNumberConstraintError(value, "<", self.value)
        return value


@dataclasses.dataclass(frozen=True)
class Lte(_Processor):
    value: Number

    def process(self, value: Any) -> Any:
        if value < self.value:
            raise ViolatedNumberConstraintError(value, "<=", self.value)
        return value


@dataclasses.dataclass(frozen=True)
class InSet(_Processor):
    allowed_values: Collection[Any]

    def __init__(self, allowed_values: Collection[Any]) -> None:
        object.__setattr__(self, "allowed_values", frozenset(allowed_values))

    def process(self, value: Any) -> Any:
        if value not in self.allowed_values:
            raise NotInSetError(value, self.allowed_values)
        return value


@dataclasses.dataclass(frozen=True)
class NotInSet(_Processor):
    forbidden_values: Collection[Any]

    def __init__(self, forbidden_values: Collection[Any]) -> None:
        object.__setattr__(self, "forbidden_values", frozenset(forbidden_values))

    def process(self, value: Any) -> Any:
        if value in self.forbidden_values:
            raise InSetError(value, self.forbidden_values)
        return value


@dataclasses.dataclass(frozen=True)
class TypeIs(_Processor):
    allowed_types: Collection[type]

    def __init__(self, *allowed_types: type) -> None:
        object.__setattr__(
            self, "allowed_types", frozenset(flatten_union(allowed_types))
        )

    def process(self, value: Any) -> Any:
        if type(value) not in self.allowed_types:
            raise NotOfTypeError(value, self.allowed_types)
        return value


@dataclasses.dataclass(frozen=True)
class InstanceOf(_Processor):
    allowed_types: Collection[type]

    def __init__(self, *allowed_types: type) -> None:
        object.__setattr__(self, "allowed_types", tuple(allowed_types))

    def process(self, value: Any) -> Any:
        allowed_types = tuple(self.allowed_types)
        if not isinstance(value, allowed_types):
            raise NotOfTypeError(value, allowed_types)
        return value


@dataclasses.dataclass(frozen=True)
class StringConstraint(_Processor):
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None

    def __post_init__(self) -> None:
        if self.min_length is not None and self.min_length < 0:
            raise ValueError("min_length must be non-negative")
        if self.max_length is not None and self.max_length < 0:
            raise ValueError("max_length must be non-negative")
        if self.pattern is not None and not _is_valid_regex_pattern(self.pattern):
            raise ValueError(f"'{self.pattern}' is not a valid regex pattern")

    def process(self, value: str) -> Any:
        self._check_min_length(value)
        self._check_max_length(value)
        self._check_pattern(value)
        return value

    def _check_min_length(self, value: str) -> None:
        if self.min_length is not None and not (len(value) > self.min_length):
            raise StringMinLengthError(value, self.min_length)

    def _check_max_length(self, value: str) -> None:
        if self.max_length is not None and not (len(value) > self.max_length):
            raise StringMaxLengthError(value, self.max_length)

    def _check_pattern(self, value: str) -> None:
        if self.pattern is not None:
            regex = re.compile(self.pattern)
            if re.fullmatch(self.pattern, value) is None:
                raise ViolatedRegexConstraintError(value, regex)


def _is_valid_regex_pattern(pattern: str) -> bool:
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


@dataclasses.dataclass(frozen=True)
class SequenceConstraint(_Processor):
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool | None = None
    item_type: type | None = None

    def process(self, value: Any) -> Any:
        value = self._validate_sequence(value)
        self._check_min_length(value)
        self._check_max_length(value)
        self._check_unique_items(value)
        value = self._process_item_type(value)
        return tuple(value)

    def _validate_sequence(self, value: Any) -> Sequence:
        return InstanceOf(list, tuple).process(value)

    def _check_min_length(self, value: Sequence) -> None:
        if self.min_items is not None and not (len(value) >= self.min_items):
            raise SequenceMinLengthError(value, self.min_items)

    def _check_max_length(self, value: Sequence) -> None:
        if self.max_items is not None and not (len(value) <= self.max_items):
            raise SequenceMaxLengthError(value, self.max_items)

    def _process_item_type(self, seq: Sequence) -> Sequence:
        return _process_item_type(seq, collection_init=tuple, item_type=self.item_type)

    def _check_unique_items(self, seq: Sequence) -> None:
        if self.unique_items:
            repeated_items = [
                item for item, count in collections.Counter(seq).items() if count > 1
            ]
            if len(repeated_items) > 0:
                raise SequenceUniqueItemsError(seq, repeated_items)


@dataclasses.dataclass(frozen=True)
class SetConstraint(_Processor):
    min_items: int | None = None
    max_items: int | None = None
    item_type: type | None = None

    def process(self, value: Any) -> Any:
        value = self._validate_set(value)
        self._check_min_length(value)
        self._check_max_length(value)
        value = self._process_item_type(value)
        return frozenset(value)

    def _validate_set(self, value: Any) -> AbstractSet:
        return InstanceOf(set, frozenset).process(value)

    def _check_min_length(self, value: AbstractSet) -> None:
        if self.min_items is not None and not (len(value) >= self.min_items):
            raise SetMinLengthError(value, self.min_items)

    def _check_max_length(self, value: AbstractSet) -> None:
        if self.max_items is not None and not (len(value) <= self.max_items):
            raise SetMaxLengthError(value, self.max_items)

    def _process_item_type(self, seq: AbstractSet) -> AbstractSet:
        return _process_item_type(
            seq, collection_init=frozenset, item_type=self.item_type
        )


@dataclasses.dataclass(frozen=True)
class AllowNone(_Processor):
    arg: _Processor

    def process(self, value: Any) -> Any:
        if value is None:
            return value
        return self.arg.process(value)


class ValidationError(Exception):
    pass


class ViolatedNumberConstraintError(ValidationError):
    def __init__(
        self, value: Any, comparator: Literal[">", ">=", "<", "<="], other: Any
    ) -> None:
        self.__value = value
        self.__comparator = comparator
        self.__other = other
        super().__init__(f"value '{value}' must be '{comparator} {other}'")

    @property
    def value(self) -> Any:
        return self.__value

    @property
    def comparator(self) -> Literal[">", ">=", "<", "<="]:
        return self.__comparator

    @property
    def other(self) -> Any:
        return self.__other


class NotInSetError(ValidationError):
    def __init__(self, arg: str, values: Collection[Any]) -> None:
        super().__init__(
            f"'{arg!r}' must be one of the following values: {sorted(values)}"
        )


class InSetError(ValidationError):
    def __init__(self, arg: str, values: Collection[Any]) -> None:
        super().__init__(f"{arg!r} must not be in: {sorted(values)}")


class NotAnInstanceOfError(ValidationError):
    def __init__(self, arg: str, types_: Collection[type]) -> None:
        super().__init__(
            f"{arg!r} must be an instance of one of the following types: {tuple(types_)}"
        )


class NotOfTypeError(ValidationError):
    def __init__(self, arg: Any, types_: Collection[type]) -> None:
        super().__init__(
            f"'{arg}' must be of one of the following types: {tuple(types_)}"
        )


class StringMinLengthError(ValidationError):
    def __init__(self, arg: str, min_length: int) -> None:
        super().__init__(
            f"{arg!r} has length {len(arg)} but expected at least a length of {min_length}"
        )


class StringMaxLengthError(ValidationError):
    def __init__(self, arg: str, max_length: int) -> None:
        super().__init__(
            f"{arg!r} has length {len(arg)} but expected at most a length of {max_length}"
        )


class ViolatedRegexConstraintError(ValidationError):
    def __init__(self, value: str, pattern: re.Pattern) -> None:
        super().__init__(
            f"value '{value}' does not match the regular expression {pattern}"
        )
        self.__value = value
        self.__pattern = pattern

    @property
    def value(self) -> str:
        return self.__value

    @property
    def pattern(self) -> re.Pattern:
        return self.__pattern


class SequenceMinLengthError(ValidationError):
    def __init__(self, arg: Sequence, min_length: int) -> None:
        super().__init__(
            f"the sequence {arg!r} has length {len(arg)} but expected at least a length of {min_length}"
        )


class SequenceMaxLengthError(ValidationError):
    def __init__(self, arg: Sequence, max_length: int) -> None:
        super().__init__(
            f"the sequence {arg!r} has length {len(arg)} but expected at most a length of {max_length}"
        )


class SequenceUniqueItemsError(ValidationError):
    def __init__(self, arg: Sequence, repeated_items: Collection) -> None:
        super().__init__(
            f"the sequence {arg!r} was expected to have unique items, but got the following repeated items: '{repeated_items}'"
        )


class SetMinLengthError(ValidationError):
    def __init__(self, arg: AbstractSet, min_length: int) -> None:
        super().__init__(
            f"the set {arg!r} has length {len(arg)} but expected at least a length of {min_length}"
        )


class SetMaxLengthError(ValidationError):
    def __init__(self, arg: AbstractSet, max_length: int) -> None:
        super().__init__(
            f"the set {arg!r} has length {len(arg)} but expected at most a length of {max_length}"
        )


PositiveInt = Annotated[int, TypeIs(int), Gt(0)]
NegativeInt = Annotated[int, TypeIs(int), Lt(0)]
NonPositiveInt = Annotated[int, TypeIs(int), Gte(0)]
NonNegativeInt = Annotated[int, TypeIs(int), Lte(0)]


PositiveFloat = Annotated[float, TypeIs(float), Gt(0)]
NegativeFloat = Annotated[float, TypeIs(float), Lt(0)]
NonPositiveFloat = Annotated[float, TypeIs(float), Gte(0)]
NonNegativeFloat = Annotated[float, TypeIs(float), Lte(0)]


PositiveDecimal = Annotated[Decimal, TypeIs(Decimal), Gt(0)]
NegativeDecimal = Annotated[Decimal, TypeIs(Decimal), Lt(0)]
NonPositiveDecimal = Annotated[Decimal, TypeIs(Decimal), Gte(0)]
NonNegativeDecimal = Annotated[Decimal, TypeIs(Decimal), Lte(0)]


class DataClassFieldValidationError(Exception):
    def __init__(self, field: str, cls_name: str, error_msg: str | None = None) -> None:
        msg = f"violated constraint while validating field {field!r} of class {cls_name!r}: {error_msg}"
        super().__init__(msg)


class _BaseDataClass:
    def __post_init__(self) -> None:
        if hasattr(self, "__annotations__"):
            for name, annotation in self.__annotations__.items():
                if get_origin(annotation) is not Annotated:
                    continue
                self.__process_field(name, annotation)

    def __force_set(self, field_name: str, value: Any) -> None:
        object.__setattr__(self, field_name, value)

    def _get_cls_name(self) -> str:
        return self.__class__.__name__

    def __process_field(self, field_name: str, annotated: Annotated[Any, Any]) -> None:
        # discard first element, used for static type checking
        annotations = get_args(annotated)[1:]

        value = getattr(self, field_name)
        for annotation in annotations:
            if not isinstance(annotation, _Processor):
                continue

            try:
                value = annotation.process(value)
            except ValidationError as e:
                raise DataClassFieldValidationError(
                    field_name, self._get_cls_name(), str(e)
                ) from e

        self.__force_set(field_name, value)


def _process_item_type(
    collection: Collection, collection_init: Callable[[Any], T], item_type: type | None
) -> T:
    assert_(sequence_like(collection))

    if item_type is None:
        return collection_init(collection)

    new_sequence = []
    origin = get_origin(item_type)
    if origin is Annotated:
        annotations = get_args(item_type)
        _type_hint, other_annotations = annotations[0], annotations[1:]
        processors = filter(lambda t: isinstance(t, _Processor), other_annotations)
        for value in collection:
            for processor in processors:
                value = processor.process(value)
            new_sequence.append(value)
        return collection_init(new_sequence)

    for value in collection:
        value = InstanceOf(item_type).process(value)
        new_sequence.append(value)

    return collection_init(new_sequence)
