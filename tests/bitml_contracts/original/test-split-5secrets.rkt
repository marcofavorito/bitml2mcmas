#lang bitml

(participant "A" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1")
(participant "B" "034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809")

(contract
  (pre
    (deposit "A" 5 "txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35@1")
    (secret "A" a1 "aaa1")
    (secret "A" a2 "aaa2")
    (secret "A" a3 "aaa3")
    (secret "A" a5 "aaa5")
  )
  (split
    (1 -> (revealif (a1) (pred (= a1 1)) (withdraw "A")))
    (4 -> (revealif (a5) (pred (= a5 5)) (withdraw "A")))
  )
)
