from utilitybelt import dev_urandom_entropy, is_hex
from binascii import hexlify, unhexlify
from pybitcoin.hash import hex_hash160, bin_hash160, bin_sha256, bin_double_sha256, hex_to_bin_reversed, bin_to_hex_reversed

from .b40 import b40_to_bin
from .config import LENGTHS


def hash_name(name, script_pubkey):
   """
   Generate the hash over a name and hex-string script pubkey.
   """
   bin_name = b40_to_bin(name)
   name_and_pubkey = bin_name + unhexlify(script_pubkey)
   return hex_hash160(name_and_pubkey)


def hash256_trunc128( data ):
   """
   Hash a string of data by taking its 256-bit sha256 and truncating it to 128 bits.
   """
   return hexlify( bin_sha256( data )[0:16] )
   