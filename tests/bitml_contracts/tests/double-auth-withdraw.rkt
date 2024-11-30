#lang bitml

(participant "A" "0")
(participant "B" "1")

(contract
  (pre
    (deposit "A" 1 "txA@0")
    (deposit "B" 1 "txB@0")
  )
  (auth "A" (auth "B" (withdraw "B")))
)
