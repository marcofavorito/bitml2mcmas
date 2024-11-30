#lang bitml

(participant "A" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1")
(participant "B" "034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809")
(participant "B1" "034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809")

(contract
  (pre
    (deposit "A" 1 "txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35@1")
    (secret "A" a "aaa")
  )
  (choice
    (revealif (a) (pred (not (< a 5))) (choice
      (revealif (a) (pred (not (< a 10))) (auth "B" (withdraw "A")))
      (revealif (a) (pred (< a 7)) (auth "B1" (withdraw "A")))
    ))
    (revealif (a) (pred (< a 4)) (choice
      (revealif (a) (pred (< a 7)) (withdraw "A"))
      (revealif (a) (pred (!= a 5)) (withdraw "A"))
    ))
  )
)
