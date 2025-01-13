#lang bitml

(participant "A" "029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced")
(participant "B" "022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30")

(contract
  (pre
    (deposit "A" 1 "txA@0")
    (deposit "A" 1 "txA1@0")
    (deposit "B" 2 "txB@0")
  )
  (choice
    (auth "B" (withdraw "A"))
    (after 30 (withdraw "B"))
  )
)
