#lang bitml

(participant "A" "00a")
(participant "B" "00b")
(participant "G" "00c")


(contract
  (pre
    (deposit "A" 9 "txA@0")
    (vol-deposit "B" txb1 10 "txB@0")
    (deposit "G" 10 "txG@0"))
  (split
    (9  -> (withdraw "B"))
    (10 -> (choice
      (after 1
        (put (txb1)
          (split
            (10 -> (withdraw "A"))
            (10 -> (withdraw "G"))
          )
        )
      )
      (after 2 (withdraw "A"))
    ))
  )
)
