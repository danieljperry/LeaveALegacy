# LeaveALegacy
https://github.com/danieljperry/LeaveALegacy/


LeaveALegacy (and the resultant Legacy Coin) is a first pass at using Chialisp to answer the question "What happens to our crypto when we die?"

*** This project comes with a giant caveat: There is no trustworthy oracle (yet) for determining death. Instead, I'll substitute a simple timelock feature for this example. Therefore, I don’t expect this project to have any real-world commercial value. ***


Sections:

I.   Assumptions
II.  Basic Explanation
III. More Complex Explanation
IV.  Command Line Instructions
V.   How To Spend
VI.  Example Puzzle And Solutions
VII. Potential Future Improvements


I. Assumptions

This guide assumes the reader is familiar with the Chia blockchain and the Chialisp language. It also assumes the reader has already set up a development environment with chia-dev-tools. For more info on these prerequisites, visit:

https://www.chia.net/
https://chialisp.com/


II. Basic Explanation

Let's say Alice wants to bequeath her money to Bob upon her death. Using LeaveALegacy, she sets up a Legacy Coin on the Chia blockchain. She has permission to spend the coin whenever she wants. Everyone else (including Bob) will encounter an ASSERT_SECONDS_RELATIVE_FAILED error if they attempt to spend the coin while Alice is still alive.

After Alice dies (simulated by N seconds having elapsed since the coin’s creation), Bob is free to spend the coin. Everyone else will still encounter the ASSERT_SECONDS_RELATIVE_FAILED error.

After Bob dies, the coin becomes spendable by anyone.


III. More Complex Explanation

Legacy Coins can be embedded inside other Legacy Coins, forming increasingly complex scenarios. For example:

– Before Alice’s death, only Alice can spend the coin.
– After Alice’s death and before Bob’s death, Bob (or anyone holding Alice’s private key) can spend the coin.
– After Alice and Bob’s deaths, a specific Charity (or anyone holding Alice’s or Bob’s private key) can spend the coin.
– After 100 years if the coin still hasn’t been spent, it becomes available for anyone to spend.

One advantage of this coin is that as soon as it is created, Alice can provide its wallet address to Bob and the Charity. They can both see the coin on the blockchain and verify that it has not been spent, but they themselves cannot spend it yet. This could potentially eliminate the need for complicated wills and/or expensive lawyers to determine inheritance.*

* I have no idea how inheritance law actually works.


IV. Command Line Instructions

Here’s how to create a Legacy Coin using the more complex scenario laid out above:

1. Compile the clsp code:

	cdv clsp build ./leavealegacy/legacy.clsp

2. Curry in 4 values to obtain the puzzle for the Charity (the innermost puzzle), which I’ll call <CharityPuzzle>:
	a. The Charity’s public key
	b. The Legacy Coin’s value, in mojos
	c. The amount of time the Charity has to spend the coin before it becomes available to everyone (eg 100 years, in seconds)
	d. An empty puzzle, indicating that this is the innermost puzzle

	cdv clsp curry ./leavealegacy/legacy.clsp.hex -a CharityPubKey -a 1000 -a 3155760000 -a '()'

3. Once again curry in 4 values to obtain Bob’s puzzle, which I’ll call <BobPuzzle>:
	a. Bob’s public key.
	b. The Legacy Coin’s value, in mojos
	c. The amount of time before Bob’s simulated death, in seconds
	d. The result of the previous curry command, ie <CharityPuzzle>

cdv clsp curry ./leavealegacy/legacy.clsp.hex -a BobPubKey -a 1000 -a 7200 -a '<CharityPuzzle>'

4. Once again curry in 4 values to obtain Alice’s puzzle, which I’ll call <AlicePuzzle>:
	a. Alice’s public key.
	b. The Legacy Coin’s value, in mojos
	c. The amount of time before Alice’s simulated death, in seconds
	d. The result of the previous curry command, ie <BobPuzzle>

cdv clsp curry ./leavealegacy/legacy.clsp.hex -a AlicePubKey -a 1000 -a 3600 -a '<BobPuzzle>'

5. Calculate the treehash for <AlicePuzzle>. Run the same curry command from step 4, passing in --treehash as a final argument:

cdv clsp curry ./leavealegacy/legacy.clsp.hex -a AlicePubKey -a 1000 -a 3600 -a '<BobPuzzle>' --treehash

6. Obtain the wallet address for the treehash. If running on testnet, use the txch prefix:

cdv encode <treehash> --prefix txch

7. Send a coin (in this example 1000 mojos) to the wallet address. Presumably this will be sent from Alice’s wallet, but technically it could come from anywhere.


After confirmation on the blockchain, the coin is now set up. Using the values from this example, only Alice can spend the coin for the first hour. During the second hour (after Alice’s simulated death and before Bob’s), only Alice and Bob can spend the coin. After two hours and before 100 years (after both Alice and Bob’s simulated deaths), only Alice, Bob, and the Charity can spend the coin. After 100 years, anyone can spend it.


V. How To Spend

The solution to the puzzle requires three things:
1. A message to be included with the aggregated signature. Can be anything.
2. The public key of whoever is attempting to spend the coin.
3. A puzzlehash where the coin will be sent when it is spent.

For example, this could be Alice’s solution:
'(alice_message AlicePubKey 0xa11ce)'

– An aggregated signature with a private key that corresponds to the spender’s public key is also required.


VI. Example Puzzle And Solutions

Here is the puzzle generated from the above example:

'(a (q 2 (q 2 (i (= 5 -65) (q 4 (c 8 (c -65 (c (sha256 95) ()))) (c (c 10 (c 383 (c 11 ()))) (c (c 14 (c 11 ())) ()))) (q 4 (c 12 (c 23 ())) (a (i 47 (q 2 47 (c 95 (c -65 (c 383 ())))) (q 4 (c 8 (c -65 (c (sha256 95) ()))) (c (c 10 (c 383 (c 11 ()))) (c (c 14 (c 11 ())) ())))) 1))) 1) (c (q (50 . 80) 51 . 60) 1)) (c (q . "AlicePubKey") (c (q . 1000) (c (q . 3600) (c (q 2 (q 2 (q 2 (i (= 5 -65) (q 4 (c 8 (c -65 (c (sha256 95) ()))) (c (c 10 (c 383 (c 11 ()))) (c (c 14 (c 11 ())) ()))) (q 4 (c 12 (c 23 ())) (a (i 47 (q 2 47 (c 95 (c -65 (c 383 ())))) (q 4 (c 8 (c -65 (c (sha256 95) ()))) (c (c 10 (c 383 (c 11 ()))) (c (c 14 (c 11 ())) ())))) 1))) 1) (c (q (50 . 80) 51 . 60) 1)) (c (q . "BobPubKey") (c (q . 1000) (c (q . 7200) (c (q 2 (q 2 (q 2 (i (= 5 -65) (q 4 (c 8 (c -65 (c (sha256 95) ()))) (c (c 10 (c 383 (c 11 ()))) (c (c 14 (c 11 ())) ()))) (q 4 (c 12 (c 23 ())) (a (i 47 (q 2 47 (c 95 (c -65 (c 383 ())))) (q 4 (c 8 (c -65 (c (sha256 95) ()))) (c (c 10 (c 383 (c 11 ()))) (c (c 14 (c 11 ())) ())))) 1))) 1) (c (q (50 . 80) 51 . 60) 1)) (c (q . "CharityPubKey") (c (q . 1000) (c (q . 0x00bc191380) (c (q) 1))))) 1))))) 1)))))'

And here are example solutions for Alice, Bob, Charity, and Delinquent (an arbitrary user):

A. '("Alice Message" AlicePubKey AliceWallet)'
B. '("Bob Message" BobPubKey BobWallet)'
C. '("Charity Message" CharityPubKey CharityWallet)'
D. '("Delinquent Message" DelinquentPubKey DelinquentWallet)'

To test the puzzle, use brun:

brun '<puzzle>' '<solution>'

The conditions that result from the above solutions are as follows:
A. ((50 "AlicePubKey" 0x6616ef45b21eadf75075cc98d224d1aba165072dc1773be6e205b80390a5b330) (51 "AliceWallet" 1000) (60 1000))

B. ((80 3600) (50 "BobPubKey" 0x9c6ef28a7efd918c83d3ca615b3fc4fcdaecaa5ef6b132aec8c08e433a518752) (51 "BobWallet" 1000) (60 1000))

C. ((80 3600) (80 7200) (50 "CharityPubKey" 0x10989e80281bf15d78b5ae1dcb6f917c7de2bb50598f85ba9d416b982cbbda6e) (51 "CharityWallet" 1000) (60 1000))

D. ((80 3600) (80 7200) (80 0x00bc191380) (50 "DelinquentPubKey" 0x4cac8979e0b7944313cb016153d6c91e108e88ecec4d2f52f07b54886fe1e059) (51 "DelinquentWallet" 1000) (60 1000))

If Alice attempts to spend the coin, the blockchain will evaluate the following conditions:

- 50 – sign the transaction using AlicePubKey and "Alice Message"
- 51 – create a new coin worth 1000 mojos in AliceWallet
- 60 – create an announcement for the coin spend

If Bob attempts to spend the coin, the above 3 conditions are also used (substituting Bob for Alice), along with an additional condition to be evaluated before anything else:

– 80 – Ensure that at least 3600 seconds have elapsed since the coin’s creation, simulating Alice’s untimely death. If this condition is not met, the spend fails with ASSERT_SECONDS_RELATIVE_FAILED.

If Charity or Delinquent attempt to spend the coin, additional timelocks are applied accordingly.

If anyone (even Alice) attempts to spend the coin without an aggregated signature, the spend will fail with BAD_AGGREGATE_SIGNATURE.


VII. Potential Future Improvements

– A web or command line interface for creating and spending the coin.
– Include some example spendbundles.
– Include a testing framework.
– The ability to include inner puzzles, for example to add a password lock (or any other functionality).
– Multisig capabilities, for example Bob and Brian (Alice’s two children) must both sign off before the coin can be spent.
– An online tutorial explaining in-depth how to set this up.
