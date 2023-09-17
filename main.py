import hashlib
import hmac
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MRR:
    # Root URI for the api
    root_uri = "https://www.miningrigrentals.com/api/v2"
    
    decode = True
    pretty = False
    print_output = False
    
    def __init__(self, key, secret):
        # Define the api_key and api_secret on construct
        self.key = key
        self.secret = secret
    
    # Raw query function -- includes signing the request
    def query(self, type, endpoint, parms={}):
        rest = ""
        # If there are any url params, remove them for the signature
        if "?" in endpoint:
            arr = endpoint.split("?")
            endpoint = arr[0]
            rest = "?" + arr[1]
        
        # URI is our root_uri + the endpoint
        uri = self.root_uri + endpoint + rest
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.key,
            'x-api-nonce': str(time.time()),
        }
        
        # String to sign is api_key + nonce + endpoint
        sign_string = self.key + headers['x-api-nonce'] + endpoint
        
        # Sign the string using a sha1 hmac
        sign = hmac.new(self.secret.encode(), sign_string.encode(), hashlib.sha1).hexdigest()
        
        headers['x-api-sign'] = sign
        
        # Curl request
        response = requests.request(type, uri, headers=headers, json=parms, verify=False)
        
        if self.pretty:
            if "?" in uri:
                uri += "&pretty"
            else:
                uri += "?pretty"
        
        if self.print_output:
            print(f"{type} {uri} : {response.text}")
        
        return {
            'status': response.status_code,
            'header': response.headers,
            'data': response.text
        }
    
    def parse_return(self, array):
        if array["status"] != 200:
            return array
        else:
            if self.decode:
                return json.loads(array["data"])
            else:
                return array["data"]
    
    # Helper aliases just to make things easier
    def get(self, endpoint, parms={}):
        return self.parse_return(self.query("GET", endpoint, parms))
    
    def post(self, endpoint, parms={}):
        return self.parse_return(self.query("POST", endpoint, parms))
    
    def put(self, endpoint, parms={}):
        return self.parse_return(self.query("PUT", endpoint, parms))
    
    def delete(self, endpoint, parms={}):
        return self.parse_return(self.query("DELETE", endpoint, parms))

key = ""
secret = ""
mrr = MRR(key, secret)
mrr.decode = True
mrr.pretty = True
mrr.print_output = True

# Test connectivity



def main():
    while True:
        
        input('press enter to continue ...')


        print('''
    0 - Information - Test connectivity and return information about you

    1 - Information - Get a list of MRR rig servers. Please note the port and ethereum_port entries are depreciated, port information is dependant on your rig.
        Please see /rig/port for that information.

    2 - Information - Get all algos and statistics for them (suggested price, unit information, current rented hash/etc)

    3 - Information - Get statistics for an algo (suggested price, unit information, current rented hash/etc)

    4 - Information - Get a list of currencies currently used for payments that are installed into our system.
        The currency may be enabled or disabled, disabled means that no function with that currency should work or attempted to be performed.
        Pair with /account/currencies endpoint. Each account has a seperate currency enablement status.
        We may add or disable a currency at any time. txfee is the current fee being charged for withdraw, it *may* change every 15 minutes.

    5 - Account - Retrieve account information

    6 - Account - Retrieve account balances

    7 - Account - Request a payout/withdrawal. This endpoint is disabled until we can find a way to offer this without risk.          

    8 - Account - List/search transaction history. `id`:always, `type`:always, `currency`:always, `amount`:always; and is negative when a deduction, `when`:always as UTC.
        `rental`,`rig`:only when not (`type` = ('Payout' or 'Deposit')).
        `txid`:only when `type` = ('Payout' or 'Deposit').
        `txfee`,`payout_address`:only when `type` = 'Payout'.
        `sent`: only when `sent`='no' and `type` = 'Payout'.
        `status`:always and is 'Cleared' or 'Pending',`pending_seconds`:always and is non 0 when `status` = 'Pending'.
        `info`: only when not (`type` = ('Payout' or 'Deposit')) and there is an extra comment/info for the transaction.

    9 - Account - List all pool profiles, or list by algo

    10 - Account - Create a pool profile

    11 - Account - Get a specific pool profile

    12 - Account - Add or replace a pool to the profile

    13 - Account - Add or replace a pool to a profile

    14 - Account - Delete a specific pool profile

    15 - Account -est a pool to verify connectivity/functionality with MRR. This endpoint is now active.
        Simple or full test; Simple verifies connectivity to the host and port only.
        Full test takes in user, password and the algorithm type which is then used to pick the stratum type to check against the pool.
        extramethod is used to specify an ethhash/ether_stratum protocol version, default is auto detection. 
        Test source can be specified as one of our available rig servers. Test may choose to fall back to simple test if there is a configuration failure. 
        error array is used for internal error, error string in result may contain a description of any problem encountered.
        Output: simple test returns 'source' test server; the 'dest' / destination pool; an 'error' code (usually 'none'); 'connection' is true if we were able to succesfully connect to the pool; 'executiontime' records how long the test took. 
        A test call can take up to 10-20 seconds when all failures are present.Output: full test contains all the same as simple plus; 
        'protocol' the chosen test protocol; if 'sub' is present then the protocol contains a mining subscription - true if sent valid response; 
        'auth' is true if the authorization response was accepted by the pool; if 'red' is present then the protocol may send a 'client.reconnect', if it is true this means the pool is incompatible with MRR; 
        'diffs' is true when pool has set mining difficulty, 'diff' is the difficulty it sent; 'work' is true when the pool has sent a valid work broadcast; 
        'ssl' is true if the pool tested as being ssl/tls compatible and the test used ssl/tls to connect; if 'xnonce' is present and true it means the pool accepts mining.extranonce.
        A valid and complete test in which the pool is compatible with MRR: connection: true, sub: true, auth: true, red: false, diffs: true, diff: >0, work: true. 
        Please do not abuse the test or hammer pools as they may block us and our miners!

    16 - Account - List saved pools

    17 - Account - Get saved pools

    18 - Account - Create a saved pool

    19 - Account - Update saved pools

    20 - Account - Delete saved pools

    21 - Account - Get a list of currencies currently used for payments that are enabled/disabled for your account. 
        If a currency is disabled for your account, you may not have access to some functions or data using that currency. 
        We use this to enable or disable a currency on our platform, we may add or disable a currency at any time.

    22 - Rig - Search for rigs on a specified algo. This is identical to the main rig list pages.

    23 - Rig - List my rigs

    24 - Rig - Get 1 or more rigs by ID

    25 - Rig - Create a rig

    26 - Rig - Update a batch of rigs using a 'rigs' array.

    27 - Rig - Delete 1 or more rigs by ID

    28 - Rig - For Rig Owners: Extend a rental to donate time to the renter -- Assuming an active rental is in progress.
               Extension length must be at least 1 minute (0.0166666666666666 hours).
               Inputs 'hours' and 'minutes' are additive to eachother, for example 0.23343 hours and 2 minutes, are added to the Extension length.
               Must have at least one of the arguments.

    29 - Rig - Batch endpoint - For Rig Owners: Extend a rental using a list of rigs in order to donate time to the renter -- Assuming an active rental is in progress. 
               Extension length must be at least 1 minute (0.0166666666666666 hours). Inputs 'hours' and 'minutes' are additive to eachother, for example 0.23343 hours and 2 minutes, are added to the Extension length.
               Must have at least one of the arguments and are specified individually for each rig.

    30 - Rig - Apply a pool profile to one or more rigs

    31 - Rig - List pools assigned to one or more rigs.

    32 - Rig - Add or replace a pool on one or more rigs

    33 - Rig - Delete a pool on one or more rigs

    34 - Rig - Get a direct port # to use inplace of 3333 when connecting to our servers.

    35 - Rig - Obtain a list of currently active threads for a rig or list of rigs. Note that information output can change depending on level of access, public, renter, or owner. 
               If you are the renter of the rig, access changes to renter and you can see more information than public view for the rig.
               If you are the owner of the rig you can see all the information for your rig.

    36 - Rig - Obtain a rigs graph information. Historical hashrate bars, average, rejected rate, rental periods, offline periods and pool offline periods. 
              "bars","average","rejected" are all strings that contain [] delimited array, consisting of a unix timestamp in miliseconds followed by the numerical hashrate value. 
              "rentals","offline","pooloffline" are comma delimited array, contain unix timestamps in miliseconds for start and end pair of each period seperated by : (colon). 
              For current rigs the lastest timestamp will be the latest minute period processed by our system.

    37 - Rig Groups - Get a list of your rig groups

    38 - Rig Groups - Create a rig group

    39 - Rig Groups - Get a rig group's details

    40 - Rig Groups - Update a rig group

    41 - Rig Groups - Delete a rig group

    42 - Rig Groups - Adds one or more rigs to your rig group. Note, rigs can only be part of one group at a time.

    43 - Rig Groups - Removes one or more rigs from your rig group. Note, rigs can only be part of one group at a time.

    44 - Rental - Lists rentals
                  Note: Average hashrate information is removed over time. Historical rentals may show a "0%"  average hashrate even if they hashed properly.
                  We prune this data to minimize storage space.

    45 - Rental - Get information on rentals by rental ID.

    46 - Rental - Create a new rental

    47 - Rental - Apply a pool profile to one or more rentals

    48 - Rental - List pools assigned to one or more rentals.

    49 - Rental - Add or replace a pool on one or more rentals

    50 - Rental - Delete a pool on one or more rentals

    51 - Rental - Purchase an extension on one more rentals

    52 - Rental - Obtain a rental graph information. Historical hashrate bars, average, rejected rate, rental periods, offline periods and pool offline periods.
                 "bars","average","rejected" are all strings that contain [] delimited array, consisting of a unix timestamp in miliseconds followed by the numerical hashrate value.
                 "offline","pooloffline" are comma delimited array, contain unix timestamps in miliseconds for start and end pair of each period seperated by : (colon).
                 "rentals" is always none. time_start and time_end contain textual display of start and end time of the rental.
                 Please note that for long rentals it can take some time to generate a graph, and even longer if you select more then one of them so please be sparing in the use of this.

    53 - Rental - Obtain 'Activity Log' detail messages on one or more of your rentals.
                  Your view will depend on if you are the renter, or the rig owner.
                  Return data is an array if more then one rental is requested, if single rental then the log is not in an array.

    54 - Rental - Obtain messages on one or more of your rentals.

    55 - Rental - Send a message to one or more of your rentals.

    56 - Pricing - List of marketplace pricing rates.




    ''')
        try:
            command = int(input('Enter number of your command:'))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue


        if command == 0:
            mrr.get("/whoami")

        elif command == 1:
            mrr.get("/info/servers")

        elif command == 2:
            mrr.get("/info/algos")

        elif command == 3:
            algo = input('Enter the name of the algo').upper()
            mrr.get("/info/algos/{algo}".format(algo=algo))

        elif command == 4:
            mrr.get("/info/currencies")

        elif command == 5:
            mrr.get("/account")

        elif command == 6:
            mrr.get("/account/balance")

        # elif command == 7:           
        #     mrr.put("/account/balance")

        elif command == 8:
            start = int(input('Enter Start number (for pagination):'))
            limit = int(input('Enter Limit number (for pagination):'))
            algo = input('Enter the name of the algo(Algo to filter -- see /info/algos)').upper()
            type = input('Type to filter -- one of [credit,payout,referral,deposit,payment,credit/refund,debit/refund,rental fee]')
            rig = int(input('Filter to specific rig.'))
            rental = int(input('Filter to specific rental.'))
            txid = input('Filter to specific txid.')
            time_greater_eq = input('Filter to greater then or equal, as Unix Timestamp integer.')
            time_less_eq = input('Filter to less then or equal, as Unix Timestamp integer.')
            parms = {'start':start,'limit':limit,'algo':algo,'type':type,'rig':rig,'rental':rental,'txid':txid,'time_greater_eq':time_greater_eq,'time_less_eq':time_less_eq}
            mrr.get("/account/transactions",parms=parms)

        elif command == 9:
            algo = input('Enter the name of the algo(Algo to filter -- see /info/algos)').upper()
            parms = {'algo':algo}
            if algo:
                mrr.get("/account/profile", parms=parms)
            mrr.get("/account/profile")

        elif command == 10:
            name = input('Name of the profile')
            algo = input('Enter the name of the algo(Algo to filter -- see /info/algos)').upper()
            parms = {'name': name, 'algo': algo}
            mrr.put("/account/profile", parms=parms)

        elif command == 11:
            Id = input('Enter the profile ID:')
            mrr.get("/account/profile/{Id}".format(Id=Id))

        elif command == 12:
            Id = input('Enter the profile ID:')
            poolId = int(input('Pool ID to add -- see /account/pools'))
            priority = int(input('Enter the priority(0-4)'))
            parms = {'poolid': poolId,'priority': priority}
            mrr.put("/account/profile/{Id}".format(Id=Id),)

        elif command == 13:
            Id = input('Enter the profile ID:')
            poolId = int(input('Pool ID to add -- see /account/pools'))
            priority = int(input('Enter the priority(0-4)'))
            parms = {'poolid': poolId}
            mrr.put("/account/profile/{Id}/{priority}".format(Id=Id, priority=priority),parms=parms)

        elif command == 14:
            Id = input('Enter the profile ID:')
            mrr.delete("/account/profile/{Id}".format(Id=Id))

        elif command == 15:
            method = input('Can be one of simple or full')
            extramethod = input('''Currently intended to use for hashimotos/ubiqhash/etchash algo type name / ether_stratum protocol.
                                 default is esm0(auto detect); can be [esm0,esm1,esm2,esm3].''')
            Type = input('''The algorithm type name, such as scrypt,sha256,hashimotos,x11. See /info/algos.
                          This determnes the protocol used in the test. Required when using 'full' test method.''')
            host = input('Url or host address of the pool. Can include port.')
            port = int(input('Port to connect to the pool host, required if no port is set in the host parameter.'))
            user = input('User to attempt to authenticate with the pool. Required when using full test method.')
            Pass = input('Password sent with authentication to the pool. Required when using full test method.')
            source = input('''Source MRR server to test from, one of 
                           [us-central01,us-east01,us-west01,us-nw01,us-south01,ca-tor01,ap-01,au-01,eu-uk01,eu-01,
                           eu-ru01,eu-ru02,eu-de01,eu-de02,jp-01,sa-br01,us-tx01,hk-01,ru-kra01,in-01]''')
            parms = {'method':method,'extramethod':extramethod,'type':Type,'host':host,'port':port,'user':user,'pass':Pass,'source':source}
            mrr.put("/account/pool/test", parms=parms)

        elif command == 16:
            mrr.get("/account/pool")

        elif command == 17:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/account/pool/{ids}".format(ids=ids))

        elif command == 18:
            type = input('Pool algo, eg: sha256, scrypt, x11, etc')
            name = input('Name to identify the pool with')
            host = input('Pool host, the part after stratum+tcp://')
            port = int(input('Pool port, the part after the : in most pool host strings'))
            user = input('Your workername')
            Pass = input('Worker Password')
            note = input('Additional notes to help identify the pool for you')
            parms = {'type': type,'name':name,'host':host,'port':port,'user':user,'pass':Pass,'note':note}
            mrr.put("/account/pool",parms=parms)

        elif command == 19:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            name = input('Name to identify the pool with')
            host = input('Pool host, the part after stratum+tcp://')
            port = int(input('Pool port, the part after the : in most pool host strings'))
            user = input('Your workername')
            Pass = input('Worker Password')
            note = input('Additional notes to help identify the pool for you')
            parms = {'name':name,'host':host,'port':port,'user':user,'pass':Pass,'note':note}
            mrr.put("/account/pool/{ids}".format(ids=ids),parms=parms)

        elif command == 20:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.delete("/account/pool/{ids}".format(ids=ids))

        elif command == 21:
            mrr.get("/account/currencies")

        elif command == 22:
            type = input('Pool algo, eg: sha256, scrypt, x11, etc')
            parms = {'type': type}
            mrr.get("/rig")

        elif command == 23:
            type = input('Pool algo, eg: sha256, scrypt, x11, etc')
            parms = {'type': type,'hashrate':True}
            mrr.get("/rig/mine")

        elif command == 24:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rig/{ids}".format(ids=ids))

        elif command == 25:
            name = input("Name of rig:")
            server = input('Server name -- see /info/servers:')
            parms = {'name':name, 'server':server} 
            mrr.put("/rig",parms=parms)

        elif command == 26:
            id = input("Rig ID:")
            parms = {'id':id}
            mrr.post("/rig/batch",parms=parms)

        elif command == 27:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.delete("/rig/{ids}".format(ids=ids))

        elif command == 28:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.put("/rig/{ids}}/extend".format(ids=ids))

        elif command == 29:
            id = int(input('Enter the Rig ID:'))
            hours = float(input('Enter the Hours to extend by'))
            minutes = float(input('Enter the Minutes to extend by'))
            parms = {'id': id, 'hours': hours, 'minutes': minutes}
            mrr.post("/rig/batch/extend")

        elif command == 30:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            profile = int(input('enter a profile ID to apply -- see /account/profile:'))
            parms = {'profile': profile}
            mrr.put("/rig/{ids}/profile".format(ids=ids),parms=parms)

        elif command == 31:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rig/{ids}/pool".format(ids=ids))

        elif command == 32:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            host = input('Pool host, the part after stratum+tcp://')
            port = int(input('Pool port, the part after the : in most pool host strings'))
            user = input('Your workername')
            Pass = input('Worker Password')
            parms = {'host': host, 'port': port, 'user': user, 'pass': Pass}
            mrr.put("/rig/{ids}/pool".format(ids=ids))

        elif command == 33:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            priority = int(input('Enter the priority(0-4)'))
            parms = {'priority': priority}
            mrr.delete("/rig/{ids}/pool".format(ids = ids))

        elif command == 34:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rig/{ids}/port".format(ids=ids))

        elif command == 35:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rig/{ids}/threads".format(ids=ids))

        elif command == 36:
            ids = input('Enter an ID or IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rig/{ids}}/graph".format(ids=ids))

        elif command == 37:
            mrr.get("/riggroup")

        elif command == 38:
            name = input('Enter A name to represent your rig group:')
            parms = {'name': name}
            mrr.put("/riggroup", parms=parms)

        elif command == 39:
            id = input('Enter A Rig Group ID:')
            mrr.get("/riggroup/{id}".format(id=id))

        elif command == 40:
            id = input('Enter A Rig Group ID:')
            name = input('Enter A name to represent your rig group:')
            enabled = int(input('''1 is enabled, 0 is disabled.
                                 Disabling a rig group will prevent the rental triggers that disable other rigs in the group.'''))
            rental_limit = int(input('The number of active rentals allowed on a group before disabling the other rigs in the group (Typically this will always be 1)'))
            parms = {'name':name, 'enabled':enabled, 'rental_limit':rental_limit}
            mrr.put("/riggroup/{id}".format(id=id),parms=parms)

        elif command == 41:
            id = input('Enter A Rig Group ID:')
            mrr.delete("/riggroup/{id}".format(id=id))

        elif command == 42:
            id = input('Enter A Rig Group ID:')
            rigIds = input('Enter an  rig ID or rig IDs in this format -> ID1;ID2;ID3 ...')
            mrr.post("/riggroup/{id}/add/{rigids}".format(id=id,rigIds=rigIds))

        elif command == 43:
            id = input('Enter A Rig Group ID:')
            rigIds = input('Enter an  rig ID or rig IDs in this format -> ID1;ID2;ID3 ...')
            mrr.post("/riggroup/{id}/remove/{rigids}".format(id=id,rigIds=rigIds))

        elif command == 44:
            type = input('Enter the type. Type is one of [owner,renter] -- owner means rentals on your rigs, renter means rentals you purchased')
            algo = input('Enter the algorithm, Filter by algo, see /info/algos')
            history = bool(input('Enter true/false. true = Show completed rentals, false = Active rentals'))
            rig = int(input('Enter the rig ID, to Show rentals related to a specific rig ID'))
            start = int(input('Enter Start number (for pagination):'))
            limit = int(input('Enter Limit number (for pagination):'))
            currency = input('Enter Currency to Filter by rentals paid currency, one of (BTC,LTC,ETH,DASH):')
            parms = {'type':type,'algo':algo,'history':history,'rig':rig,'start':start,'limit':limit,'currency':currency}
            mrr.get("/rental",parms=parms)

        elif command == 45:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rental/{ids}".format(ids=ids))

        elif command == 46:
            rig = int(input('Enter Rig ID to rent:'))
            length = float(input('Enter Length in hours to rent:'))
            profile = int(input('Enter The profile ID to apply (see /account/profile)'))
            currency = input('Enter Currency to use, one of (BTC,LTC,ETH,DASH):')
            rate_type = input('Enter The hash type of rate. defaults to "mh", possible values: [hash,kh,mh,gh,th]')
            rate_price = float(input("Enter Price per [rate.type] per day to pay -- this is a filter only, it will use the rig's current price as long as it is <= this value"))
            parms = {'rig':rig,'length':length,'profile':profile,'currency':currency,'rate.type':rate_type,'rate.price':rate_price}
            mrr.put("/rental",parms=parms)

        elif command == 47:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            profile = int(input('Enter Profile ID to apply -- see /account/profile'))
            parms = {'profile':profile}
            mrr.put("/rental/{ids}}/profile".format(ids=ids),parms=parms)

        elif command == 48:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rental/{ids}/pool".format(ids=ids))

        elif command == 49:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            host = input('Pool host, the part after stratum+tcp://')
            port = int(input('Pool port, the part after the : in most pool host strings'))
            user = input('Your workername')
            Pass = input('Worker Password')
            priority = int(input('Enter priority 0-4 -- can be passed in after pool/ instead.'))
            parms = {'ids':ids,'host':host, 'port':port, 'user':user, 'pass':Pass, 'priority':priority}
            mrr.put("/rental/{ids}/pool".format(ids=ids), parms=parms)
        
        elif command == 50:
            priority = int(input('Enter priority 0-4 -- can be passed in after pool/ instead.'))            
            parms = {'priority':priority}
            mrr.delete("/rental/{ids}/pool".format(ids=ids),parms=parms)

        elif command == 51:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            length = float(input('Enter Length in hours to purchase an extension for:'))
            parms = {'length': length}
            mrr.put("/rental/{ids}/extend".format(ids=ids),parms=parms)

        elif command == 52:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            mrr.put("/rental/{ids}}/graph".format(ids=ids))

        elif command == 53:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rental/{ids}/log".format(ids=ids))

        elif command == 54:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            mrr.get("/rental/{ids}/message".format(ids=ids))

        elif command == 55:
            ids = input('Enter an rental ID or rental IDs in this format -> ID1;ID2;ID3 ...')
            message = input('Enter The message to add to a rental:')
            parms = {'message':message}
            mrr.put("/rental/{ids}/message".format(ids=ids),parms=parms)

        elif command == 56:
            mrr.get("/pricing")

        else:
            print("Invalid command number. Please try again.")



if __name__ == "__main__":
    main()