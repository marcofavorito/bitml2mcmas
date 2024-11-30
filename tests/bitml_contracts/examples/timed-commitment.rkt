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
