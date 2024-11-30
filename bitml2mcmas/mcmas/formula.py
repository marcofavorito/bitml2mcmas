"""Classes for representing specification formulas."""

import dataclasses
from abc import ABC
from typing import Annotated, Union, cast

from bitml2mcmas.helpers.validation import InstanceOf, _BaseDataClass
from bitml2mcmas.mcmas.custom_types import McmasId


class _BaseFormula(ABC):

    def __invert__(self: "FormulaType"):
        return NotFormula(self)

    def __and__(self, other: "FormulaType"):
        return AndFormula(cast(FormulaType, self), other)

    def __or__(self, other: "FormulaType"):
        return OrFormula(cast(FormulaType, self), other)



class _BaseAtomicFormula(_BaseFormula):
    pass


@dataclasses.dataclass(frozen=True)
class AtomicFormula(_BaseAtomicFormula, _BaseDataClass):
    id: McmasId


@dataclasses.dataclass(frozen=True)
class GreenStatesAtomicFormula(_BaseAtomicFormula, _BaseDataClass):
    id: McmasId


@dataclasses.dataclass(frozen=True)
class RedStatesAtomicFormula(_BaseAtomicFormula, _BaseDataClass):
    id: McmasId


@dataclasses.dataclass(frozen=True)
class EnvGreenStatesAtomicFormula(_BaseAtomicFormula, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class EnvRedStatesAtomicFormula(_BaseAtomicFormula, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class _BaseDiamondFormula(_BaseFormula, _BaseDataClass):
    group_id: McmasId
    arg: Annotated["FormulaType", InstanceOf(_BaseFormula)]


@dataclasses.dataclass(frozen=True)
class DiamondNextFormula(_BaseDiamondFormula):
    pass


@dataclasses.dataclass(frozen=True)
class DiamondEventuallyFormula(_BaseDiamondFormula):
    pass


@dataclasses.dataclass(frozen=True)
class DiamondAlwaysFormula(_BaseDiamondFormula):
    pass


@dataclasses.dataclass(frozen=True)
class DiamondUntilFormula(_BaseFormula):
    group_id: McmasId
    left: Annotated["FormulaType", InstanceOf(_BaseFormula)]
    right: Annotated["FormulaType", InstanceOf(_BaseFormula)]


@dataclasses.dataclass(frozen=True)
class _BaseUnaryFormula(_BaseFormula, _BaseDataClass, ABC):
    arg: Annotated["FormulaType", InstanceOf(_BaseFormula)]


@dataclasses.dataclass(frozen=True)
class _BaseBinaryFormula(_BaseFormula, _BaseDataClass, ABC):
    left: Annotated["FormulaType", InstanceOf(_BaseFormula)]
    right: Annotated["FormulaType", InstanceOf(_BaseFormula)]


@dataclasses.dataclass(frozen=True)
class AGFormula(_BaseUnaryFormula):
    pass


@dataclasses.dataclass(frozen=True)
class EGFormula(_BaseUnaryFormula):
    pass


@dataclasses.dataclass(frozen=True)
class AXFormula(_BaseUnaryFormula):
    pass


@dataclasses.dataclass(frozen=True)
class EXFormula(_BaseUnaryFormula):
    pass


@dataclasses.dataclass(frozen=True)
class AFFormula(_BaseUnaryFormula):
    pass


@dataclasses.dataclass(frozen=True)
class EFFormula(_BaseUnaryFormula):
    pass


@dataclasses.dataclass(frozen=True)
class AUntilFormula(_BaseBinaryFormula, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class EUntilFormula(_BaseBinaryFormula, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class NotFormula(_BaseUnaryFormula, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class AndFormula(_BaseBinaryFormula, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class OrFormula(_BaseBinaryFormula, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class ImpliesFormula(_BaseBinaryFormula, _BaseDataClass):
    pass


FormulaType = Union[
    AGFormula,
    EGFormula,
    AXFormula,
    EXFormula,
    AFFormula,
    EFFormula,
    AUntilFormula,
    EUntilFormula,
    DiamondNextFormula,
    DiamondEventuallyFormula,
    DiamondAlwaysFormula,
    DiamondUntilFormula,
    AtomicFormula,
    GreenStatesAtomicFormula,
    RedStatesAtomicFormula,
    EnvGreenStatesAtomicFormula,
    EnvRedStatesAtomicFormula,
    NotFormula,
    AndFormula,
    OrFormula,
    ImpliesFormula,
]
