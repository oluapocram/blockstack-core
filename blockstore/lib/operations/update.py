from pybitcoin import embed_data_in_blockchain, BlockchainInfoClient, hex_hash160
from utilitybelt import is_hex
from binascii import hexlify, unhexlify

from ..b40 import b40_to_hex, bin_to_b40
from ..config import *
from ..scripts import blockstore_script_to_hex, add_magic_bytes
from ..hashing import hash256_trunc128

def build(name, consensus_hash, data=None, testset=False):
    """
    Takes in the name to update the data for and the data update itself.
    Name must include the namespace ID, but not the scheme.
    
    Record format:
    
    0     2  3                                   19                      39
    |-----|--|-----------------------------------|-----------------------|
    magic op  hash128(name.ns_id,consensus hash) hash160(data)
    """
    
    if name.startswith(NAME_SCHEME):
       raise Exception("Invalid name %s: must not start with %s" % (name, NAME_SCHEME))
    
    hex_name = hash256_trunc128( name + consensus_hash )
    data_hash = hex_hash160( data )
    
    readable_script = 'NAME_UPDATE %s %s' % (hex_name, data_hash)
    hex_script = blockstore_script_to_hex(readable_script)
    packaged_script = add_magic_bytes(hex_script, testset=testset)

    return packaged_script


def broadcast(name, data, consensus_hash, private_key, blockchain_client=BlockchainInfoClient(), testset=False):
    """
    Write a name update into the blockchain.
    """
    nulldata = build(name, consensus_hash, data=data, testset=testset)
    response = embed_data_in_blockchain(nulldata, private_key, blockchain_client, format='hex')
    response.update({'data': nulldata})
    return response


def parse(bin_payload, block_number):
    """
    Parse a payload to get back the name and update hash.
    NOTE: bin_payload excludes the leading three bytes.
    """
    name_hash_bin = bin_payload[:LENGTHS['name_hash']]
    update_hash_bin = bin_payload[LENGTHS['name_hash']:]
    
    name_hash = hexlify( name_hash_bin )
    update_hash = hexlify( update_hash_bin )
    
    return {
        'opcode': 'NAME_UPDATE',
        'name_hash': name_hash,
        'update_hash': update_hash
    }
