# This library handles all communication with the blockchain, using our dogecoin_OP_RETURN package
#
# Copyright (C) 2017 Ingo R. Keck for Kubrik Engineering / Open Knowledge Ireland
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import libnacl.public
import libnacl.utils
import op_return_dogecoin
import unittest
import json
import time, os
import copy
import datetime, binascii

# load dogecoin config
try:
    with open("dogecoinconf.json", "r") as dogc:
        doge = json.load(dogc)
except FileNotFoundError:
    print("Please provide a dogecoinconf.json file with port, user, password and doge-address " +
          "of a local dogecoind for rpc calls. \n An example file will be generated now.")
    if not os.path.exists("dogecoinconf.json"):
        with open("dogecoinconf.json", "w") as dogc:
            doge = {'port': 8484, 'user': 'username', 'password': '1234', 'address': 'DHf1S...'}
            json.dump(doge, dogc)
op_return_dogecoin.OP_RETURN_DOGECOIN_PORT = doge['port']
op_return_dogecoin.OP_RETURN_DOGECOIN_USER = doge['user']
op_return_dogecoin.OP_RETURN_DOGECOIN_PASSWORD = doge['password']
op_return_dogecoin.OP_RETURN_DOGECOIN_ADDRESS = doge['address']


def load_key_file():
    key_obj = libnacl.utils.load_key('keyfile.json')
    # privkey = key_obj.sk
    # pubkey = key_obj.pk
    return key_obj


def generate_key_file():
    """
    Generate new keys and save them locally. backs up old file
    :return: status from saving keys
    """
    mykey = create_keys()
    if os.path.exists('keyfile.json'):
        os.rename('keyfile.json', time.strftime('%Y_%m_%d_%H_%M_%S_', )+'keyfile.json')
    r = mykey.save('keyfile.json')
    return r

def create_keys():
    """
    Create public private key pair
    :return: created key
    """
    allkeys = libnacl.public.SecretKey()
    #privkey = allkeys.sk
    #pubkey = allkeys.pk
    return allkeys

def encrypt(privkey, pubkey, message):
    """
    Encrypt a message to the pubkey, using the privkey for authentication
    :param privkey:
    :param pubkey:
    :param message: message as bytes
    :return: encrypted message
    """
    cryptbox = libnacl.public.Box(sk=privkey, pk=pubkey)
    encrypted = cryptbox.encrypt(message)
    return encrypted

def decrypt(privkey, pubkey, message):
    cryptbox = libnacl.public.Box(sk=privkey, pk=pubkey)
    plaintext = cryptbox.decrypt(message)
    return plaintext

def save_on_dogecoin(message, privkey=None, pubkey=None, dogeaddress=op_return_dogecoin.OP_RETURN_DOGECOIN_ADDRESS):
    # encrypt message
    # split up in xxbytes parts
    if not privkey:
        # first get keys
        key_obj = load_key_file()
        privkey = key_obj.sk
        pubkey = key_obj.pk
    messagelength = op_return_dogecoin.OP_RETURN_MAX_BYTES - 10
    if not isinstance(message, bytes):
        if isinstance(message, str):
            message = message.encode('latin1')
        else:
            raise TypeError
    if len(message) > (messagelength*10):
        print("Message should be smaller than %d bytes" %(messagelength*10))
        raise MemoryError
    encrypted = encrypt(privkey=privkey, pubkey=pubkey, message=message).decode('latin1')

    # KUxxxyz: KU Kubrik, xxx: random identifier, y message index, z max index
    xxx = os.urandom(4).decode('latin1')
    max_index = int(len(encrypted)/messagelength)-1 #0 is first
    if len(encrypted)%messagelength > 0:
        max_index += 1
    if len(encrypted) > messagelength:
        enclist = []
        for _ in range(int(len(encrypted)/messagelength)):
            pos = '%d%d:'%(_,max_index)
            enclist.append('KU'+xxx+str(pos)+encrypted[_*messagelength:(_+1)*messagelength])
        if len(encrypted)%messagelength > 0:
            _ += 1
            pos = '%d%d:' % (_,max_index)
            enclist.append('KU'+xxx+str(pos)+encrypted[_ * messagelength:])
    else:
        enclist = [encrypted]
    # create dogecoin transactions
    # put it on dogecoin
    txlist = []
    for m in enclist:
        print('sent Message:')
        print(m)
        newtx = op_return_dogecoin.OP_RETURN_send(send_address=dogeaddress, send_amount=1, metadata=m, testnet=False)
        if isinstance(newtx, dict):
            if 'error' in newtx:
                if newtx['error']:
                    print(newtx['error'])
                    raise ValueError
        txlist.append(newtx)
    return txlist

def retrieve_from_dogecoin(dogeaddress, startnumber=0, startdate=None, stopdate=None, key_object=None, VERBOSE=False):
    """
    Searches the blockchain for op_return transactions, decrypts them and
    returns them as tuple (message, timestamp)
    :param dogeaddress: Dogecoin address to watch
    :param startnumber: Start with that message number
    :param startdate: Start looking for transactions at that date
    :param stopdate: Stop looking for transactions at that date
    :param VERBOSE: if True print out what you are doing
    :return: list of decrypted messages for the dogeaddress
    """
    if VERBOSE:
        print("Dogecoin address: %s, loading keys..." % dogeaddress)
    # first get keys
    if not key_object:
        key_object = load_key_file()
    # retrieve transactions
    if VERBOSE:
        print("get all transactions starting with %d" %startnumber)
    all_tx = get_transactions_dogecoin(dogeaddress, startnumber=startnumber)
    # extract op_return for transactions with the same times
    messages = dict()
    for tx in all_tx:
        if VERBOSE:
            print("looking at transaction %s " % tx['txid'])
        if startdate:
            if tx['time'] < startdate:
                continue
        if stopdate:
            if tx['time'] > stopdate:
                continue
        if VERBOSE:
            print("Get message from transaction %s " % tx['txid'])
        message = op_return_dogecoin.OP_RETURN_get(tx['txid'], testnet=False)
        if not message:
            continue
        # sort for time, then for reference
        # get actual time with datetime.datetime.fromtimestamp(tx['time'] or tx['blocktime'] )
        # sort for xxx reference
        # KUxxxyz:data KU Kubrik, xxx: random identifier, y message index, z max index
        # convert to latin1
        try:
            message['op_return']=message['op_return'].decode('latin1')
        except:
            # probably not one of ours
            continue
        if not message['op_return'][8]==':':
            # not one of ours
            continue
        #print('got message: ')
        #print(message['op_return'])
        xxx = message['op_return'][2:6]
        txtime = round(tx['time']/1800) # put all messages within 1800sec together
        if txtime in messages:
            if xxx in messages[txtime]:
                messages[txtime][xxx].append((message['op_return'], tx['time']))
            else:
                messages[txtime][xxx] = [(message['op_return'],tx['time'])]
        else:
            messages[txtime] = dict()
            messages[txtime][xxx]=[(message['op_return'],tx['time'])]
    # combine them
    # we can get attacked with additional messages. We need to test them to find the right ones
    decrypted_msg = list()
    for txtime in messages:
        # all messages in one time frame
        for xxx in messages[txtime]:
            # all messages with same xxx code
            #possible_msg = list()
            allmsg = dict()
            alltimes = dict()
            for mesgtx in messages[txtime][xxx]:
                msg = mesgtx[0]
                # we can have multiple lengths
                # KUxxxyz: KU Kubrik, xxx: random identifier, y message index, z max index
                try:
                    if msg[7] in allmsg:
                        if int(msg[6]) in allmsg[msg[7]]:
                            allmsg[msg[7]][int(msg[6])].append(msg[9:])
                        else:
                            allmsg[msg[7]][int(msg[6])] = [msg[9:]]
                    else:
                        allmsg[msg[7]] = dict()
                        allmsg[msg[7]][int(msg[6])] = [msg[9:]]
                        alltimes[msg[7]] = mesgtx[1]  # we take the first time as reference
                except:
                    continue
            # now get all permutations for a given length
            possible_msg = list()
            for l in allmsg:
                newmsg = list()
                newtime = alltimes[l]
                for p in range(len(allmsg[l])):
                    # make a copy of the tree so far for later
                    newtree_orig = list(newmsg)
                    try:
                        for idx, m in enumerate(allmsg[l][p]):
                            newtree = list(newtree_orig)
                            if idx > 0:
                                #print(l, p, m)
                                if len(newtree) == 0:
                                    newtree.append(m)
                                else:
                                    for i in range(len(newtree)):
                                        newtree[i] += m
                                # add new tree
                                for n in newtree:
                                    newmsg.append(n)
                            else:
                                if len(newmsg) == 0:
                                    newmsg.append(m)
                                else:
                                    for i in range(len(newmsg)):
                                        newmsg[i] += m
                                        #print(l, p, m)
                    except:
                        # fail silently for messages that do not have all positions
                        pass
                for m in newmsg:
                    possible_msg.append((m, newtime))
            # decrypt all
            for message in possible_msg:
                try:
                    msg = decrypt(message=message[0].encode('latin1'), privkey=key_object.sk, pubkey=key_object.pk)
                    # add valid ones to decrypted_msg
                    decrypted_msg.append((msg, message[1]))
                except:
                    # we ignore bad messages
                    pass
            # print(possible_msg)
    # return them
    return decrypted_msg

def add_watchadress_dogecoin(dogeaddress):
    """
    Adds an address as address to watch to dogecoin
    :param dogeaddress: address that should be added
    :return: True if all went well
    """
    # first test if address is watched
    addressgroups = op_return_dogecoin.OP_RETURN_dogecoin_cmd('listaddressgroupings', False)
    createaddress = True
    for ag in addressgroups:
        for ad in ag:
            if ad[0] == dogeaddress:
                createaddress = False
                break
    if createaddress:
        # add address as watchonly in wallet
        try:
            result = op_return_dogecoin.OP_RETURN_dogecoin_cmd('importaddress', False, dogeaddress, 'reprowatch')
        except BaseException:
            print("could not add address %s as watch-only" % dogeaddress)
            return False
    return True

def get_transactions_dogecoin(dogeaddress, startnumber=0, maxnumber=None):
    """
    Get list of transactions for a given dogecoin address
    :param dogeaddress: Dogecoin Address
    :param startnumber: Start with that transaction number
    :param maxnumber: only retrieve that amount of transactions
    :return: list of transaction IDs
    """
    # we need to do that with an address that is watched, so make sure it is in the wallet
    add_watchadress_dogecoin(dogeaddress)
    # now, get all the transactions
    txlist = list()
    tx_no = 50
    tx_start = startnumber
    txid_list=list()
    while True:
        result = op_return_dogecoin.OP_RETURN_dogecoin_cmd('listtransactions', False, "*", tx_no, tx_start, True)
        #result = op_return_dogecoin.OP_RETURN_dogecoin_cmd('listtransactions', False)
        if not result:
            break
        for tx in result:
            if 'address' in tx:
                #print(tx['address'])
                #print(tx)
                if tx['address'] == dogeaddress:
                    if tx['txid'] not in txid_list:
                        #print(datetime.datetime.fromtimestamp(tx['time']))
                        txlist.append(copy.deepcopy(tx))
                        txid_list.append(tx['txid'])
        tx_start += tx_no
        if maxnumber:
            if tx_start - startnumber > maxnumber:
                break
    return txlist

def get_tx(txid):
    """
    Retrieve the transaction txid from the blockchain. Will fail if it is not for a watched address.
    :param txid: transaction id
    :return: decomposed transaction
    """
    # test if txid is valid
    test = op_return_dogecoin.OP_RETURN_hex_to_bin(txid) # returns None if failes
    if test:
        transaction = op_return_dogecoin.OP_RETURN_get_mempool_txn(txid, testnet=False)
    else:
        transaction = None
    return transaction

# tests
class TestCrypto(unittest.TestCase):

    def test_createkeys(self):
        """
        Test if we can create keys
        :return:
        """
        a = create_keys()
        privk = a.sk
        pubk = a.pk
        self.assertEqual(len(privk), 32)
        self.assertEqual(len(pubk), 32)

    def test_endecrypt(self):
        """
        Test if we can corretly encrypt messages
        :return:
        """
        keys1 = create_keys()
        keys2 = create_keys()
        message = "Hola".encode('latin1')
        encrypted = encrypt(keys1.sk, keys2.pk, message)
        decrypted = decrypt(keys2.sk, keys1.pk, encrypted)
        self.assertEqual(message,decrypted)

# try to load key file
try:
    keys = load_key_file()
except FileNotFoundError:
    print("local key file not found. We will create a new one.")
    if not os.path.exists('keyfile.json'):
        generate_key_file()

if __name__ == '__main__':
    # we can do a full test that actually costs coins, or a reduced test that only reads
    # messages from the chain
    a = input('Do Dogecoin test? "full" will cost coins for a message! [y,n, f=full]')
    ad = op_return_dogecoin.OP_RETURN_DOGECOIN_ADDRESS
    if a == 'f':
        if ad:
            add_watchadress_dogecoin(ad)
            message = 10*"test"+ datetime.datetime.now().isoformat()
            kk = load_key_file()
            privk = kk.sk
            pubk = kk.pk
            txlist =save_on_dogecoin(message, privk, pubk, dogeaddress=ad)
            print(txlist)
            # give it 10 s to settle
            time.sleep(10)
            # retrieve it again
    if (a=='f') | (a == 'y'):
        if ad:
            add_watchadress_dogecoin(ad)
            message = 20 * "test"
            kk = load_key_file()
            privk = kk.sk
            pubk = kk.pk
            messages = retrieve_from_dogecoin(dogeaddress=ad)
            print (messages)
