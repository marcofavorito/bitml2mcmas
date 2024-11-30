#lang bitml

(participant "A" "0a")
(participant "B" "0b")
(participant "M" "0e")

(contract
  (pre
    (deposit "A" 10 "txA@0")
  )
  (choice
    (auth "A" (withdraw "B"))
    (auth "B" (withdraw "A"))
    (auth "A" (split
      (1 -> (withdraw "M"))
      (9 -> (choice
        (auth "M" (withdraw "A"))
        (auth "M" (withdraw "B"))
      ))
    ))
    (auth "B" (split
      (1 -> (withdraw "M"))
      (9 -> (choice
        (auth "M" (withdraw "A"))
        (auth "M" (withdraw "B"))
      ))
    ))
  )
)
