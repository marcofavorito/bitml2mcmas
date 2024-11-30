#lang bitml

(participant "A" "0")
(participant "B" "1")

(contract
  (pre
    (deposit "A" 1 "txA@0")
    (deposit "B" 1 "txB@0")
    (secret "A" a1 "0001a")
  )
  (reveal (a1) (choice
    (withdraw "A")
    (withdraw "B")
  ))
)
