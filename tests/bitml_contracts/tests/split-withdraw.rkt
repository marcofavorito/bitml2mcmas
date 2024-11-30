#lang bitml

(participant "A" "0")
(participant "B" "1")

(contract
  (pre
    (deposit "A" 1 "txA@0")
    (deposit "B" 1 "txB@0")
  )
  (split
    (1 -> (withdraw "A"))
    (1 -> (withdraw "B"))
  )
)
