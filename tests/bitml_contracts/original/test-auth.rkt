#lang bitml

(participant "A" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe0")
(participant "A1" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1")
(participant "A2" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe2")
(participant "A3" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe3")
(participant "A4" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe4")
(participant "A5" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe5")
(participant "A6" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe6")
(participant "A7" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe7")
(participant "A8" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe8")
(participant "A9" "0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe9")

(contract
  (pre
    (deposit "A" 1 "txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35@1")
  )
  (auth "A1" (auth "A2" (auth "A3" (auth "A4" (auth "A5" (auth "A6" (auth "A7" (auth "A8" (auth "A9" (withdraw "A"))))))))))
)
