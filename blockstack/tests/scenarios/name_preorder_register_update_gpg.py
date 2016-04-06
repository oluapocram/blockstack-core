#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Blockstack
    ~~~~~
    copyright: (c) 2014-2015 by Halfmoon Labs, Inc.
    copyright: (c) 2016 by Blockstack.org

    This file is part of Blockstack

    Blockstack is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Blockstack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Blockstack. If not, see <http://www.gnu.org/licenses/>.
""" 

import testlib
import pybitcoin
import urllib2
import json
import blockstack_client
from blockstack_client import storage, user, client
import blockstack_profiles
import blockstack_gpg
import time
import os

wallets = [
    testlib.Wallet( "5JesPiN68qt44Hc2nT8qmyZ1JDwHebfoh9KQ52Lazb1m1LaKNj9", 100000000000 ),
    testlib.Wallet( "5KHqsiU9qa77frZb6hQy9ocV7Sus9RWJcQGYYBJJBb2Efj1o77e", 100000000000 ),
    testlib.Wallet( "5Kg5kJbQHvk1B64rJniEmgbD83FpZpbw2RjdAZEzTefs9ihN3Bz", 100000000000 ),
    testlib.Wallet( "5JuVsoS9NauksSkqEjbUZxWwgGDQbMwPsEfoRBSpLpgDX1RtLX7", 100000000000 ),
    testlib.Wallet( "5KEpiSRr1BrT8vRD7LKGCEmudokTh1iMHbiThMQpLdwBwhDJB1T", 100000000000 ),
    testlib.Wallet( "5K5hDuynZ6EQrZ4efrchCwy6DLhdsEzuJtTDAf3hqdsCKbxfoeD", 100000000000 ),
    testlib.Wallet( "5J39aXEeHh9LwfQ4Gy5Vieo7sbqiUMBXkPH7SaMHixJhSSBpAqz", 100000000000 ),
    testlib.Wallet( "5K9LmMQskQ9jP1p7dyieLDAeB6vsAj4GK8dmGNJAXS1qHDqnWhP", 100000000000 ),
    testlib.Wallet( "5KcNen67ERBuvz2f649t9F2o1ddTjC5pVUEqcMtbxNgHqgxG2gZ", 100000000000 )
]

consensus = "17ac43c1d8549c3181b200f1bf97eb7d"
wallet_keys = None
wallet_keys_2 = None
error = False

key_names = {
    'foo.test': [], # to be filled in 
    'bar.test': []  # to be filled in 
}

def scenario( wallets, **kw ):

    global wallet_keys, wallet_keys_2, key_names, error


    testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_ready( "test", wallets[1].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_name_preorder( "foo.test", wallets[2].privkey, wallets[3].addr )
    testlib.blockstack_name_preorder( "bar.test", wallets[5].privkey, wallets[6].addr )
    testlib.next_block( **kw )
    
    testlib.blockstack_name_register( "foo.test", wallets[2].privkey, wallets[3].addr )
    testlib.blockstack_name_register( "bar.test", wallets[5].privkey, wallets[6].addr )
    testlib.next_block( **kw )

    test_proxy = testlib.TestAPIProxy()
    client.set_default_proxy( test_proxy )
    wallet_keys = client.make_wallet_keys( owner_privkey=wallets[3].privkey, data_privkey=wallets[4].privkey )
    wallet_keys_2 = client.make_wallet_keys( owner_privkey=wallets[6].privkey, data_privkey=wallets[7].privkey )

    # migrate profiles 
    res = blockstack_client.migrate_profile( "foo.test", proxy=test_proxy, wallet_keys=wallet_keys )
    if 'error' in res:
        res['test'] = 'Failed to initialize foo.test profile'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return 

    res = blockstack_client.migrate_profile( "bar.test", proxy=test_proxy, wallet_keys=wallet_keys_2 )
    if 'error' in res:
        res['test'] = 'Failed to initialize bar.test profile'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return

    testlib.next_block( **kw )

    # add account keys 
    res = blockstack_gpg.gpg_profile_create_key( "foo.test", "foo.test's account key", immutable=False,
                                                proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw),
                                                gpghome=testlib.gpg_key_dir(**kw), use_key_server=False )

    if 'error' in res:
        res['test'] = 'Failed to create foo.test account key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return 

    else:
        key_names['foo.test'].append( res )

    res = blockstack_gpg.gpg_profile_create_key( "bar.test", "bar.test's account key", immutable=False,
                                                proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw),
                                                gpghome=testlib.gpg_key_dir(**kw), use_key_server=False )

    if 'error' in res:
        res['test'] = 'Failed to create bar.test account key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return 

    else:
        key_names['bar.test'].append( res )

    testlib.next_block( **kw )

    # add immutable app keys 
    res = blockstack_gpg.gpg_app_create_key( "foo.test", "secure messaging", "foo.test's immutable secmsg key", immutable=True,
                                              proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw) )

    if 'error' in res:
        res['test'] = 'Failed to create foo.test immutable app key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return 
    else:
        key_names['foo.test'].append( res )

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_app_create_key( "bar.test", "secure messaging", "bar.test's immutable secmsg key", immutable=True,
                                                proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw) )

    if 'error' in res:
        res['test'] = 'Failed to create bar.test immutable app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return
    else:
        key_names['bar.test'].append( res )

    testlib.next_block( **kw )

    # add mutable app keys 
    res = blockstack_gpg.gpg_app_create_key( "foo.test", "less-secure messaging", "foo.test's mutable secmsg key",
                                                proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw) )

    if 'error' in res:
        res['test'] = 'Failed to create foo.test mutable app key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return
    else:
        key_names['foo.test'].append( res )

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_app_create_key( "bar.test", "less-secure messaging", "bar.test's mutable secmsg key",
                                                proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw) )

    if 'error' in res:
        res['test'] = 'Failed to create bar.test mutable app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return
    else:
        key_names['bar.test'].append( res )

    testlib.next_block( **kw )

    # add profile keys that we'll delete
    res = blockstack_gpg.gpg_profile_create_key( "foo.test", "foo.test's deleted account key", immutable=True,
                                                proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw),
                                                gpghome=testlib.gpg_key_dir(**kw), use_key_server=False)

    foo_profile_delete_key_id = None
    if 'error' in res:
        res['test'] = 'Failed to create deletable foo.test account key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return
    else:
        key_names['foo.test'].append( res )
        foo_profile_delete_key_id = res['key_id']

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_profile_create_key( "bar.test", "bar.test's deleted account key", immutable=True,
                                                proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw),
                                                gpghome=testlib.gpg_key_dir(**kw), use_key_server=False)

    bar_profile_delete_key_id = None
    if 'error' in res:
        res['test'] = 'Failed to create deletable bar.test account key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return
    else:
        key_names['bar.test'].append( res )
        bar_profile_delete_key_id = res['key_id']

    testlib.next_block( **kw )

    # add immutable app keys, which we can delete
    res = blockstack_gpg.gpg_app_create_key( "foo.test", "immutable delete", "foo.test's deleted immutable secmsg key", immutable=True,
                                                proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw) )

    foo_immutable_delete_key_id = None
    if 'error' in res:
        res['test'] = 'Failed to create deletable foo.test immutable app key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return
    else:
        key_names['foo.test'].append( res )
        foo_immutable_delete_key_id = res['key_id']

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_app_create_key( "bar.test", "immutable delete", "bar.test's deleted immutable secmsg key", immutable=True,
                                                proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw) )
    
    bar_immutable_delete_key_id = None
    if 'error' in res:
        res['test'] = 'Failed to create deletable bar.test immutable app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return
    else:
        key_names['bar.test'].append( res )
        bar_immutable_delete_key_id = res['key_id']

    testlib.next_block( **kw )

    # add mutable app keys which we can delete
    res = blockstack_gpg.gpg_app_create_key( "foo.test", "mutable delete", "foo.test's deleted mutable secmsg key",
                                                proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw) )

    foo_mutable_delete_key_id = None
    if 'error' in res:
        res['test'] = 'Failed to create deletable mutable foo.test app key'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return
    else:
        key_names['foo.test'].append( res )
        foo_mutable_delete_key_id = res['key_id']

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_app_create_key( "bar.test", "mutable delete", "bar.test's deleted mutable secmsg key",
                                                proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw) )

    bar_mutable_delete_key_id = None
    if 'error' in res:
        res['test'] = 'Failed to create deletable mutable bar.test app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return
    else:
        key_names['bar.test'].append( res )
        bar_mutable_delete_key_id = res['key_id']

    testlib.next_block( **kw )

    # delete profile keys
    res = blockstack_gpg.gpg_profile_delete_key( "foo.test", foo_profile_delete_key_id, proxy=test_proxy, wallet_keys=wallet_keys )
    if 'error' in res:
        res['test'] = 'Failed to create deletable account foo.test profile key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_profile_delete_key( "bar.test", bar_profile_delete_key_id, proxy=test_proxy, wallet_keys=wallet_keys_2 )
    if 'error' in res:
        res['test'] = 'Failed to create deletable account bar.test profile key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return 

    # delete immutable app keys 
    res = blockstack_gpg.gpg_app_delete_key( "foo.test", "immutable delete", "foo.test's deleted immutable secmsg key", 
                                            immutable=True, proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw))

    if 'error' in res:
        res['test'] = 'Failed to create deletable foo.test immutable app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return 

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_app_delete_key( "bar.test", "immutable delete", "bar.test's deleted immutable secmsg key",
                                            immutable=True, proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw))

    if 'error' in res:
        res['test'] = 'Failed to create deletable bar.test immutable app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True
        return 

    testlib.next_block( **kw )

    # delete mutable app keys
    res = blockstack_gpg.gpg_app_delete_key( "foo.test", "mutable delete", "foo.test's deleted mutable secmsg key",
                                            proxy=test_proxy, wallet_keys=wallet_keys, config_dir=testlib.get_working_dir(**kw))

    if 'error' in res:
        res['test'] = 'Failed to create deletable foo.test mutable app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True 
        return 

    testlib.next_block( **kw )
    res = blockstack_gpg.gpg_app_delete_key( "bar.test", "mutable delete", "bar.test's deleted mutable secmsg key",
                                            proxy=test_proxy, wallet_keys=wallet_keys_2, config_dir=testlib.get_working_dir(**kw))

    if 'error' in res:
        res['test'] = 'Failed to create deletable bar.test mutable app key'
        print json.dumps(res, indent=4, sort_keys=True )
        error = True 
        return 

    testlib.next_block( **kw )


def check( state_engine ):

    global wallet_keys, wallet_keys_2, key_names, error

    if error:
        print "Key operation failed."
        return False

    # not revealed, but ready 
    ns = state_engine.get_namespace_reveal( "test" )
    if ns is not None:
        print "namespace not ready"
        return False 

    ns = state_engine.get_namespace( "test" )
    if ns is None:
        print "no namespace"
        return False 

    if ns['namespace_id'] != 'test':
        print "wrong namespace"
        return False 

    # not preordered
    names = ['foo.test', 'bar.test']
    wallet_keys_list = [wallet_keys, wallet_keys_2]

    for i in xrange(0, len(names)):
        name = names[i]
        wallet_payer = 3 * (i+1) - 1
        wallet_owner = 3 * (i+1)
        wallet_data_pubkey = 3 * (i+1) + 1
        wallet_keys = wallet_keys_list[i]
        key_res = key_names[name]

        preorder = state_engine.get_name_preorder( name, pybitcoin.make_pay_to_address_script(wallets[wallet_payer].addr), wallets[wallet_owner].addr )
        if preorder is not None:
            print "still have preorder"
            return False
    
        # registered 
        name_rec = state_engine.get_name( name )
        if name_rec is None:
            print "name does not exist"
            return False 

        # owned 
        if name_rec['address'] != wallets[wallet_owner].addr or name_rec['sender'] != pybitcoin.make_pay_to_address_script(wallets[wallet_owner].addr):
            print "name has wrong owner"
            return False 

        # account listing exists, and other keys are deleted
        account_key_listing = blockstack_gpg.gpg_list_profile_keys( name )
        secure_app_listing = blockstack_gpg.gpg_list_app_keys( name, "secure messaging" )
        less_secure_app_listing = blockstack_gpg.gpg_list_app_keys( name, "less-secure messaging" )

        if 'error' in account_key_listing:
            print json.dumps(account_key_listing)
            return False 

        if len(account_key_listing) != 1:
            print "Invalid account keys:\n%s" % json.dumps(account_key_listing)
            return False 

        key_id, key_url = account_key_listing[0]['identifier'], account_key_listing[0]['contentUrl']
        if key_url != key_res[0]['key_url']:
            print "Key ID mismatch (account): %s != %s\nFull listing:\n%s\n\nKeys we generated:\n%s\n" % \
                    (key_url, key_res[0]['key_url'], account_key_listing[0], json.dumps(key_res, indent=4, sort_keys=True))
            return False 

        # immutable listings exist, and other keys are deleted
        if 'error' in secure_app_listing:
            print json.dumps(secure_app_listing)
            return False 

        if len(secure_app_listing) != 1:
            print "Invalid immutable keys:\n%s" % json.dumps(secure_app_listing)
            return False 

        key_id, key_url = secure_app_listing[0]['identifier'], secure_app_listing[0]['contentUrl']
        if key_url != key_res[1]['key_url']:
            print "Key ID mismatch (immutable app): %s != %s\nFull listing:\n%s\n\nKeys we generated:\n%s\n" % \
                    (key_url, key_res[1]['key_url'], secure_app_listing[0], json.dumps(key_res, indent=4, sort_keys=True))
            return False 

        # mutable listings exist, and other keys are deleted
        if 'error' in less_secure_app_listing:
            print json.dumps(less_secure_app_listing)
            return False 

        if len(less_secure_app_listing) != 1:
            print "Invalid mutable keys (mutable app):\n%s" % json.dumps(less_secure_app_listing)
            return False 

        key_id, key_url = less_secure_app_listing[0]['identifier'], less_secure_app_listing[0]['contentUrl']
        if key_url != key_res[2]['key_url']:
            print "Key ID mismatch: %s != %s\nFull listing:\n%s\n\nKeys we generated:\n%s\n" % \
                    (key_url, key_res[2]['key_url'], less_secure_app_listing[0], json.dumps(key_res, indent=4, sort_keys=True))
            return False


    return True