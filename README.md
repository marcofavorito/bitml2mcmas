# BitML2MCMAS

Strategic Reasoning for BitML Smart Contracts using MCMAS.

## Installation

The tool has been tested on Linux (Ubuntu LTS 22.04).

- Make sure Python is installed.

- Download the repository:

```
git clone git@github.com:marcofavorito/bitml2mcmas.git
```

- Install the package:

```
cd bitml2mcmas
pip install .
```

- To process the ISPL file, you need the MCMAS tool, which you can download from the official website: [https://sail.doc.ic.ac.uk/software/mcmas/](https://sail.doc.ic.ac.uk/software/mcmas/).

- To run tests with `pytest`, add the `mcmas` binary in `tests/bin`.

- We use [`poetry`](https://python-poetry.org/) to handle the development dependencies. To install them, do `poetry install`, and then `poetry shell`. 

## Quickstart

- Define the BitML contract in the BitML syntax (see the [original BitML project](https://bitml-lang.github.io/)):

```python
bitml_timed_commitment = """
#lang bitml

(participant "A" "0a")
(participant "B" "0b")

(contract
  (pre
    (deposit "A" 1 "txA@0")
    (secret "A" a1 "0001a")
  )
  (choice
    (reveal (a1) (withdraw "A"))
    (after 1 (withdraw "B"))
  )
)

"""
```

- Parse the BitML contract:

```python
from bitml2mcmas.bitml.parser.parser import BitMLParser

parser = BitMLParser()
contract = parser(bitml_timed_commitment)
```

- Compile in an ISPL file. You may specify (1) evaluation rules, that define the alphabet over which formulae are defined,
and (2) the ATL formulas to specify:

```python
from pathlib import Path
from bitml2mcmas.compiler.core import Compiler
from bitml2mcmas.mcmas.ast import EvaluationRule
from bitml2mcmas.mcmas.boolcond import EqualTo, EnvironmentIdAtom, IntAtom
from bitml2mcmas.mcmas.formula import AtomicFormula, DiamondEventuallyFormula
from bitml2mcmas.mcmas.to_string import interpreted_system_to_string

formulae = [DiamondEventuallyFormula("Agent_A", AtomicFormula("A_gets_1"))]
evaluation_rules = [
    EvaluationRule("A_gets_1",
                   EqualTo(EnvironmentIdAtom("part_A_total_deposits"),
                           IntAtom(1)))
]
compiler = Compiler(
    contract, formulae, evaluation_rules=evaluation_rules
)
interpreted_system = compiler.compile()
interpreted_system_str = interpreted_system_to_string(interpreted_system)
Path("output.ispl").write_text(interpreted_system_str)
```

- Use the `mcmas` tool to process the `output.ispl` file.  

```
mcmas -atlk 1 output.ispl
```


## Docs

To build the docs: `mkdocs build`

To view documentation in a browser: `mkdocs serve`
and then go to [http://localhost:8000](http://localhost:8000)
