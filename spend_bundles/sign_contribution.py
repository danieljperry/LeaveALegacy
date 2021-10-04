import hashlib
from blspy import PrivateKey, AugSchemeMPL
from chia.util.hash import std_hash
from clvm.casts import int_to_bytes

SK = PrivateKey.from_bytes(bytes.fromhex(""))

DATA_TO_SIGN = bytes.fromhex("")

COIN_ID = bytes.fromhex("")

#ADD_DATA = bytes.fromhex("117816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015af")
ADD_DATA = bytes.fromhex("ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb")

signature = AugSchemeMPL.sign(SK, DATA_TO_SIGN + COIN_ID + ADD_DATA)

print(str(signature))