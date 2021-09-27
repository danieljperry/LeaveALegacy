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

------------------------------------------
**I. Assumptions**

This guide assumes the reader is familiar with the Chia blockchain and the Chialisp language. It also assumes the reader has already set up a development environment with chia-dev-tools. For more info on these prerequisites, visit:

https://www.chia.net/

https://chialisp.com/

------------------------------------------
**II. Basic Example**

In the simplest case, let's say Alice doesn’t have any heirs and she wants to give her money away on a first-come, first-served basis. She creates a Legacy Coin on the Chia blockchain with the following rules:

1. While Alice is alive, only she can spend the coin. When she does spend it, she can allocate funds however she seems fit, eg she can send half to her wallet and half to a friend. If anyone other than Alice attempts to spend the coin while Alice is still alive, they will encounter an ASSERT_SECONDS_RELATIVE_FAILED error.

2. After Alice dies (simulated by N seconds having elapsed since the coin’s creation), Anyone may spend the coin.

------------------------------------------
**III. More Complex Example**

Legacy Coins can support inner coins of any type, including other legacy coins. This makes a wide variety of functionality possible. For example, let’s say Alice wants to bequeath her money to Bob upon her death. If Bob also dies before the money has been spent, she wants the money to go to a charity. But she doesn’t trust everyone at the charity, so she gives a password to a few of its employees, which can be used to unlock the coin. Here are the rules she can set up:

– Before Alice’s death, only Alice can spend the coin. She can spend it in any way she sees fit, including divvying it up to multiple people.

– After Alice’s death and before Bob’s death, Bob (or anyone holding Alice’s private key) can spend the coin.

– After Alice and Bob’s deaths, anyone with the password can spend the coin. A few members of the charity have access to the password.

(This example is a bit contrived, but the coin itself is quite versatile in its possibilities. It could go many levels deep, or it could automatically allocate funds to multiple recipients, or it could even have a “failsafe” feature to release the money to whoever attempts to spend it first after, say, 100 years.)

One advantage of this coin is that as soon as it is created, Alice can provide its ID, along with the correct puzzle and solution to unlock it, to both Bob and the employees of the Charity. They can all see the coin on the blockchain and verify that it has not been spent, but they themselves cannot spend it yet. This could potentially eliminate the need for complicated wills and/or expensive lawyers to determine inheritance.*

	* I have no idea how inheritance law actually works.

------------------------------------------
**IV. Command Line Instructions**

Here’s how to create a Legacy Coin using the more complex scenario laid out above:

1. Compile the clsp code for both the Legacy Coin and a password-protected coin:

	_cdv clsp build ./leavealegacy/legacy.clsp_
	_cdv clsp build ./leavealegacy/passwordprotect.clsp_

2. The first puzzle we need to build is the password-protected puzzle, which is the innermost puzzle. I’ll call it [PasswordPuzzle].
	a. Choose a password and get its hash. Sha256 is built into chialisp, so this is easy to do from the command line. If we want the password to be _hello_, we can run this command:
		_run '(sha256 hello)'_
		The resulting hash is 0x2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
	b. Curry the hash into [PasswordPuzzle], and use the treehash flag:
		_cdv clsp curry ./leavealegacy/passwordprotect.clsp.hex -a 0x2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824 –treehash_
		The result using the ‘hello’ hash is 0933224426cc47801ecfc4d1914c22ea5116c38eefef9989396e85af75b1259f
		Save this hash as it will be needed in the next puzzle.

3. Now build the inner legacy puzzle, which I’ll call [BobPuzzle]. This puzzle uses [PasswordPuzzle] as its inner puzzle. Do this by currying in 3 values, and using the --treehash flag to obtain a hash:
	a. Bob’s public key.

	b. The amount of time before Bob’s simulated death, in seconds
	
	c. The inner puzzle hash, obtained in step 2 above.

	_cdv clsp curry ./leavealegacy/legacy.clsp.hex -a BobPubKey -a 7200 -a 0x0933224426cc47801ecfc4d1914c22ea5116c38eefef9989396e85af75b1259f --treehash_

NOTE: You have to prepend all command line arguments that should be interpreted as bytes with ‘0x’.

The result of this command using the above parameters is:
9c6e047a0771accebb46d5448d172b4e9f77f805f3b33d7fff5db4208c46286a

This gives us the treehash of [BobPuzzle] with [PasswordPuzzle] as the inner puzzle.

4. Build the outer legacy puzzle, which I’ll call [AlicePuzzle]. This puzzle uses [BobPuzzle] as its inner puzzle. Do this by currying in 3 values, and using the --treehash flag to obtain a hash:
	
	a. Alice’s public key.
	
	b. The amount of time before Alice’s simulated death, in seconds
	
	c. The inner puzzle hash, obtained in step 3 above.

	_cdv clsp curry ./leavealegacy/legacy.clsp.hex -a AlicePubKey -a 3600 -a 0x9c6e047a0771accebb46d5448d172b4e9f77f805f3b33d7fff5db4208c46286a --treehash_

This gives the treehash of [AlicePuzzle]. Using the above values gives us:
cd1a9493211f66da3afda7c1a313877d14c29655d9713d96c872e396f82fc4d9

6. Obtain the wallet address for the treehash. If running on testnet, use the txch prefix:

	_cdv encode [treehash] --prefix txch_

7. Send a coin of any value to the wallet address. Presumably this will be sent from Alice’s wallet, but technically it could come from anywhere.


After confirmation on the blockchain, the coin is now set up. Using the values from this example, only Alice can spend the coin for the first hour. During the second hour (after Alice’s simulated death and before Bob’s), only Alice and Bob can spend the coin. After two hours anyone with the password can spend it.

------------------------------------------
**V. How To Spend**

The solution to [AlicePuzzle] requires three things:
	
1. The inner puzzle.
	
2. The inner solution.
	
3. The public key of whoever is attempting to spend the coin.

– An aggregated signature with a private key that corresponds to the spender’s public key is also required.

The requirements for the inner puzzle and inner solution are dependent on who is attempting to spend the coin. For example:
	– Alice is allowed to use any values. Presumably she’ll create one or more conditions to spend the coins. This is similar to the delegated spend in Chia’s standard transaction construction.
	– Everyone else must enter exactly the inner puzzle that was used to generate the treehash for [BobPuzzle] above. They then execute [BobPuzzle] and the process repeats. See below for some examples.

------------------------------------------
**VI. Example Puzzle And Solutions**

Here is the puzzle generated from the above example, which will go on the blockchain:

'(a (q 2 (q 2 (i (= 5 -65) (q 4 (c 4 (c -65 (c (a 14 (c 2 (c 47 ()))) ()))) (a 47 95)) (q 4 (c 10 (c 11 ())) (a (i (= 23 ()) (q 4 (c 4 (c -65 (c (a 14 (c 2 (c 47 ()))) ()))) (a 47 95)) (q 2 (i (= 23 (a 14 (c 2 (c 47 ())))) (q 4 (c 4 (c -65 (c (a 14 (c 2 (c 47 ()))) ()))) (a 47 95)) (q 8 (q . "Inner puzzle does not match inner puzzle hash."))) 1)) 1))) 1) (c (q 50 80 2 (i (l 5) (q 11 (q . 2) (a 14 (c 2 (c 9 ()))) (a 14 (c 2 (c 13 ())))) (q 11 (q . 1) 5)) 1) 1)) (c (q . "AlicePubKey") (c (q . 3600) (c (q . 0x9c6e047a0771accebb46d5448d172b4e9f77f805f3b33d7fff5db4208c46286a) 1))))'

And now for some solutions. Let’s say the coin is worth 1000 mojos and Alice wants to send half to herself and half to her car dealer. She could use this solution:

_'( (q . ((51 0xa11ce 500) (51 0xfadedcab 500))) () AlicePubKey)'_

Which would result in the following conditions:

_((50 "AlicePubKey" 0xc6293dd476f247a55ed0b58eba456ee8b8f17fb3948306f8bdf0b30e4d681725) (51 0x0a11ce 500) (51 0xfadedcab 500))_

If Bob (or anyone else) attempts the same solution, he’ll receive an error for not supplying the correct inner puzzle:

'( (q . ((51 0xa11ce 500) (51 0xfadedcab 500))) () BobPubKey)'
FAIL: clvm raise ("Inner puzzle does not match inner puzzle hash.")

Even if he supplies the inner puzzle (which he should have in his possession), he’ll be stopped by the timelock as long as Alice is still Alive:

'_[BobPuzzle]_ ((q . ((51 0b0b 500) (51 0xfadedcab 500))) () BobPubKey) BobPubKey)'

((80 3600) (50 "BobPubKey" 0x9c6e047a0771accebb46d5448d172b4e9f77f805f3b33d7fff5db4208c46286a) (50 "BobPubKey" 0x1b60245290c5cc917b2efa6294565146c4caf7d4f2b37352c142faa2f0f762bd) (51 "0b0b" 500) (51 0xfadedcab 500))

If someone from the Charity has the correct password and wishes to spend the coin, they must supply both inner puzzles:

'_[BobPuzzle]_ (_[CharityPuzzle]_ (hello CharityPubKey 0xdeadbeef 1000) CharityPubKey) CharityPubKey)'

((80 3600) (50 "CharityPubKey" 0x9c6e047a0771accebb46d5448d172b4e9f77f805f3b33d7fff5db4208c46286a) (80 7200) (50 "CharityPubKey" 0x0933224426cc47801ecfc4d1914c22ea5116c38eefef9989396e85af75b1259f) (50 "CharityPubKey" 0x43138432a85321ce4eb110af0ec388a4fabc1deb8e82242430579bd3e41abda2) (51 0xdeadbeef 1000) (60 1000))

With each inner puzzle, we add on at least two new conditions:

- 50 – Sign the transaction with the private key that matches the public key given in the solution.

– 80 – Ensure that at least a certain number of seconds have elapsed since the coin’s creation, simulating owner’s untimely death. If this condition is not met, the spend fails with ASSERT_SECONDS_RELATIVE_FAILED.

Most users will also want to add their own conditions, such as:

- 51 – create a new coin
	
- 60 – create an announcement for the coin spend

If anyone (even Alice) attempts to spend the coin without an aggregated signature, the spend will fail with BAD_AGGREGATE_SIGNATURE.

------------------------------------------
**VII. Potential Future Improvements**

– A web or command line interface for creating and spending the coin.
	
– Include some example spendbundles.
	
– Include a testing framework.
	
– Multisig capabilities, for example Bob and Brian (Alice’s two children) must both sign off before the coin can be spent.
	
– An online tutorial explaining in-depth how to set this up.
