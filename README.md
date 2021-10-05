# LeaveALegacy
https://github.com/danieljperry/LeaveALegacy/

**Video tutorials now available!**

https://www.youtube.com/playlist?list=PL3k_XsjZ_oMytBzyWX1G51lGgCEOLbVRi


LeaveALegacy (and the resultant Legacy Coin) is a first pass at using Chialisp to answer the question "What happens to our crypto when we die?"

*** This project comes with a giant caveat: There is no trustworthy oracle (yet) for determining death. Instead, I'll substitute a simple timelock feature for this example. Therefore, I don’t expect this project to have any real-world commercial value. ***


Sections:

I.   Assumptions

II.  Basic Example

III. More Complex Example

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

1. While Alice is alive, only she can spend the coin. When she does spend it, she can allocate funds however she deems fit, eg she can send half to her wallet and half to a friend. If anyone other than Alice attempts to spend the coin while Alice is still alive, they will encounter an ASSERT_SECONDS_RELATIVE_FAILED error.

2. After Alice dies (simulated by N seconds having elapsed since the coin’s creation), anyone may spend the coin.

Here's a visual example of what this coin will look like:

![alt text](https://github.com/danieljperry/LeaveALegacy/blob/main/img/01_outer.jpg?raw=true)

------------------------------------------
**III. More Complex Example**

Legacy Coins can support inner coins of any type, including other Legacy Coins. This makes possible a wide variety of functionality.

For example, let’s say Alice wants to bequeath her money to Bob upon her death. If Bob also dies before the money has been spent, she wants the money to go to a charity. But she doesn’t trust everyone at the charity, so she gives a password to a few of its employees, which can be used to unlock the coin. Here are the rules she can set up:

– Before Alice’s death, only Alice can spend the coin.

– After Alice’s death and before Bob’s death, Bob (or anyone holding Alice’s private key) can spend the coin.

– After Alice and Bob’s deaths, anyone with the password can spend the coin. A few members of the charity have access to the password.

(This example is a bit contrived, but the coin itself is quite versatile in its possibilities. It could go many levels deep, or it could automatically allocate funds to multiple recipients. It could even have a “failsafe” feature to unlock the money if it hasn't been spent after, say, 100 years.)

One advantage of this coin is that as soon as it is created, Alice can provide its ID, along with the correct puzzle and solution to unlock it, to both Bob and the employees of the charity. They can all see the coin on the blockchain and verify that it has not been spent. Even though they possess the solution, they cannot spend it until Alice and/or Bob has died. This could potentially eliminate the need for complicated wills and/or expensive lawyers to determine inheritance.*

	* I have no idea how inheritance law actually works.

And here's a visual representation of this coin:

![alt text](https://github.com/danieljperry/LeaveALegacy/blob/main/img/03_password.jpg?raw=true)

------------------------------------------
**IV. Command Line Instructions**

Here’s how to create a Legacy Coin using the more complex scenario laid out above:

1. Compile the clsp code for both the Legacy Coin and a password-protected coin:

		cdv clsp build ./leavealegacy/legacy.clsp
		cdv clsp build ./leavealegacy/passwordprotect.clsp

2. Start by building the innermost puzzle, which in this case is the password-protected puzzle. I’ll call it [PasswordPuzzle].

	a. Choose a password and get its hash. Sha256 is built into chialisp, so this is easy to do from the command line. If we want the password to be _hello_, we can run this command:
	
			run '(sha256 hello)'
			
	The resulting hash is 0x2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
		
	b. Curry the hash into [PasswordPuzzle], and use the treehash flag:
	
			cdv clsp curry ./leavealegacy/passwordprotect.clsp.hex -a 0x2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824 --treehash
			
	The result using the ‘hello’ hash is 0933224426cc47801ecfc4d1914c22ea5116c38eefef9989396e85af75b1259f
		
	Save this hash as it will be needed in the next puzzle.
	
		* Caution: Passwords aren't particularily secure on public blockchains, so don't try this for real unless you know what you are doing. For more info, see https://chialisp.com/docs/security/#password-locked-coin-security

3. Now build the inner legacy puzzle, which I’ll call [BobPuzzle]. This puzzle uses [PasswordPuzzle] as its inner puzzle. Curry in 3 values:

	a. Bob’s public key.

	b. The amount of time before Bob’s simulated death, in seconds.
	
	c. The inner puzzle hash, obtained in step 2 above.
	
	Also, use the --treehash flag to obtain a hash:

		cdv clsp curry ./leavealegacy/legacy.clsp.hex -a BobPubKey -a 7200 -a 0x0933224426cc47801ecfc4d1914c22ea5116c38eefef9989396e85af75b1259f --treehash

	NOTE: You have to prepend all command line arguments that should be interpreted as bytes with ‘0x’.

	The result of this command using the above parameters is:
	dd9e391596a5fd732897d32d189db7768ef05a332e325eec1a0a0f4205aed845

	This gives us the treehash of [BobPuzzle] with [PasswordPuzzle] as its inner puzzle.

4. Build the outer legacy puzzle, which I’ll call [AlicePuzzle]. This puzzle uses [BobPuzzle] as its inner puzzle. Curry in 3 values:
	
	a. Alice’s public key.
	
	b. The amount of time before Alice’s simulated death, in seconds.
	
	c. The inner puzzle hash, obtained in step 3 above.
	
	Also, use the --treehash flag to obtain a hash:

		cdv clsp curry ./leavealegacy/legacy.clsp.hex -a AlicePubKey -a 3600 -a 0xdd9e391596a5fd732897d32d189db7768ef05a332e325eec1a0a0f4205aed845 --treehash

	This gives the treehash of [AlicePuzzle]. Using the above values gives us: 50981592c840f68d27821a2dc75cc8b268da992753f00ab155798f94d7252acf

5. Obtain the wallet address for the treehash. If running on testnet, use the txch prefix:

		cdv encode [treehash] --prefix txch

6. Send a coin of any value to the wallet address. Presumably this will be sent from Alice’s wallet, but technically it could come from anywhere.

After confirmation on the blockchain, the coin is now set up. Using the values from this example, only Alice can spend the coin for the first hour. During the second hour (after Alice’s simulated death and before Bob’s), only Alice and Bob can spend the coin. After two hours anyone with the password can spend it.

------------------------------------------
**V. How To Spend**

The solution to [AlicePuzzle] requires three things:
	
1. The inner puzzle.
	
2. The inner solution.
	
3. The public key of whoever is attempting to spend the coin.

- If the curryed OWNER_PUBKEY matches the passed-in public key, an aggregated signature with a matching private key is also required. Otherwise, no aggregated signature is immediately required, but one might be required in an inner puzzle.

The requirements for the inner puzzle and inner solution are dependent on who is attempting to spend the coin. For example:

– Alice is allowed to use any values. Presumably she’ll create one or more conditions to spend the coins. This is similar to the delegated spend in Chia’s standard transaction construction.
	
– Everyone else must enter exactly the inner puzzle that was used to generate the treehash for [BobPuzzle] above. They then execute [BobPuzzle] and the process repeats. See below for some examples.

------------------------------------------
**VI. Example Puzzle And Solutions**

Here is the puzzle generated from the above example, which will go on the blockchain:

	'(a (q 2 (q 2 (i (= 5 -65) (q 4 (c 4 (c -65 (c (a 14 (c 2 (c 47 ()))) ()))) (a 47 95)) (q 4 (c 10 (c 11 ())) (a (i 23 (q 2 (i (= 23 (a 14 (c 2 (c 47 ())))) (q 2 47 95) (q 8 (q . "Inner puzzle does not match inner puzzle hash."))) 1) (q 2 47 95)) 1))) 1) (c (q 50 80 2 (i (l 5) (q 11 (q . 2) (a 14 (c 2 (c 9 ()))) (a 14 (c 2 (c 13 ())))) (q 11 (q . 1) 5)) 1) 1)) (c (q . "AlicePubKey") (c (q . 3600) (c (q . 0xdd9e391596a5fd732897d32d189db7768ef05a332e325eec1a0a0f4205aed845) 1))))'

And now for some solutions. Let’s say the coin is worth 1000 mojos and Alice wants to send half to herself and half to her car dealer. She could use this solution:

	'( (q . ((51 0xa11ce 500) (51 0xfadedcab 500))) () AlicePubKey)'
	
Here is the command to do this (brun '[puzzle]' '[solution]'):

	brun '(a (q 2 (q 2 (i (= 5 -65) (q 4 (c 4 (c -65 (c (a 14 (c 2 (c 47 ()))) ()))) (a 47 95)) (q 4 (c 10 (c 11 ())) (a (i 23 (q 2 (i (= 23 (a 14 (c 2 (c 47 ())))) (q 2 47 95) (q 8 (q . "Inner puzzle does not match inner puzzle hash."))) 1) (q 2 47 95)) 1))) 1) (c (q 50 80 2 (i (l 5) (q 11 (q . 2) (a 14 (c 2 (c 9 ()))) (a 14 (c 2 (c 13 ())))) (q 11 (q . 1) 5)) 1) 1)) (c (q . "AlicePubKey") (c (q . 3600) (c (q . 0xdd9e391596a5fd732897d32d189db7768ef05a332e325eec1a0a0f4205aed845) 1))))' '( (q . ((51 0xa11ce 500) (51 0xfadedcab 500))) () AlicePubKey)'

Which would result in the following conditions:

_((50 "AlicePubKey" 0xc6293dd476f247a55ed0b58eba456ee8b8f17fb3948306f8bdf0b30e4d681725) (51 0x0a11ce 500) (51 0xfadedcab 500))_

If Bob (or anyone else) attempts the same solution, he’ll receive an error for not supplying the correct inner puzzle:

'( (q . ((51 0xa11ce 500) (51 0xfadedcab 500))) () BobPubKey)'
FAIL: clvm raise ("Inner puzzle does not match inner puzzle hash.")

Even if he supplies the inner puzzle (which he should have in his possession), he’ll be stopped by the timelock as long as Alice is still Alive:

	'( [BobPuzzle] ((q . ((51 b0b 500) (51 fadedcab 500))) () BobPubKey) BobPubKey)'

((80 3600) (50 "BobPubKey" 0x81c0451c54b5b8a9de0752a601a05f4a59f75d7eedd305350e014c167b69508f) (51 "b0b" 500) (51 "fadedcab" 500))

If someone from the charity has the correct password and wishes to spend the coin, they must supply both inner puzzles:

	'( [BobPuzzle] ([CharityPuzzle] (hello CharityPubKey 0xdeadbeef 1000) CharityPubKey) CharityPubKey)'

((80 3600) (80 7200) (50 "CharityPubKey" 0x43138432a85321ce4eb110af0ec388a4fabc1deb8e82242430579bd3e41abda2) (51 0xdeadbeef 1000) (60 1000))

With each inner Legacy Puzzle, we add on a new condition:

- 80 – Ensure that at least a certain number of seconds have elapsed since the coin’s creation, simulating the owner’s untimely death. If this condition is not met, the spend fails with ASSERT_SECONDS_RELATIVE_FAILED.

If the "owner" of that puzzle attempts to spend it, another condition is also added:

- 50 – Sign the transaction with the private key that matches the public key given in the solution.

Most users will also want to add their own conditions, such as:

- 51 – create a new coin
	
- 60 – create an announcement for the coin spend

If Alice or Bob attempt to spend the coin without an aggregated signature, the spend will fail with BAD_AGGREGATE_SIGNATURE. This protects against malicious users attempting to spend the coin to themselves by impersonating its rightful owner.

If anyone else attempts to spend the coin, they'll reach the innermost puzzle, which in this example also requires an aggregated signature. However, this won't necessarily be the case. But even in case an aggregated signature is not required, those attempting to spend the coin will still be blocked by the timelock.

------------------------------------------
**VII. Potential Future Improvements**

– A web or command line interface for creating and spending the coin.
	
– Include a testing framework.
	
– Multisig capabilities, for example Bob and Brian (Alice’s two children) must both sign off before the coin can be spent.
