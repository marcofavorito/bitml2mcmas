#lang bitml

(participant "A" "0")
(participant "B" "1")

(contract
  (pre
    (deposit "A" 1 "txA@0")
    (deposit "B" 1 "txB@0")
    (vol-deposit "A" txa1 1 "txA@1")
    (vol-deposit "B" txb1 1 "txB@1")
  )
  (put (txa1 txb1) (withdraw "A"))
)