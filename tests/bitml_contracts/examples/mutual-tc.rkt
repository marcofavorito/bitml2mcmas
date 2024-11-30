#lang bitml

(participant "A" "0a")
(participant "B" "0b")

(contract
  (pre
    (deposit "A" 1 "txA@0")
    (deposit "B" 1 "txB@0")
    (secret "A" a1 "0001a")
    (secret "B" b1 "0001b")
  )
  (choice
    (reveal (a1) (choice
      (reveal (b1) (split
        (1 -> (withdraw "A"))
        (1 -> (withdraw "B"))
      ))
      (after 2 (withdraw "A"))
    ))
    (after 1 (withdraw "B"))
  )
)
