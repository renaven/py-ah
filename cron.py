import kronos
import json
import requests
import gzip
from operator import itemgetter
from shutil import copyfile
from operator import itemgetter
from time import sleep

@kronos.register('20 * * * *')
def get_auc_data_eu():
    servers = {}
    avg_price_eu = {}
    api_calls_count = 0
    servers_updated_count = 0
    
    with open('/home/sweetpea/public_html/item_db_img_v2.json') as realm_file:
        realms = json.load(realm_file)['realms']
    with open('/home/sweetpea/public_html/item_db_img_v2.json') as avg_temp:
    	items = json.load(avg_temp)["items"]
    for j in realms["en_GB"]:
        servers[j['slug']] = ''
        #servers.append([j['slug'], "en_GB"])
    #servers = {'medivh' : '', 'exodar' : ''}
    for l in items:
        avg_price_eu[int(l)] = [0, 0]
    del items
    del realms
    for s in servers:
        if servers[s] != '':
            parent = servers[s]
            src = '/home/sweetpea/webapps/server_data/item_db_master_' +parent+ '_en_GB.json'
            dst = '/home/sweetpea/webapps/server_data/item_db_master_'+s+'_en_GB.json'
           
            copyfile(src, dst) 
            
            servers_updated_count += 1
            continue
        #time.sleep(5)
        items = {}
        raw_auctions = {}
        with open('/home/sweetpea/webapps/item_db_img.json') as data_file:
            for line in data_file:
                item = {}
                data = json.loads(line)
                item["id"] = data[0]
                item["name"] = data[1]
                item["img_url"] = data[2][45:-4]
                if len(data) > 3:
                    item["pet_id"] = data[3]
                item["price"] = 0
                item["quantity"] = 0
                item["average"] = 0
                items[data[0]] = item
                del item

        
        r = requests.get("https://eu.api.battle.net/wow/auction/data/"+s+"?locale=en_GB&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw", timeout=20)
        sleep(2)
        
        try:
            auction_dump_url = json.loads(r.text)["files"][0]["url"]
        except (ValueError, KeyError):
            f = open("/home/sweetpea/webapps/cron_debug_log.txt", "a")
            f.write('API error')
            f.write(r.text)
            f.write('\n')
            f.close()
            continue
        
        del r
        f = open("/home/sweetpea/webapps/cron_debug_log.txt", "a")
        #f.write('API error')
        f.write(auction_dump_url)
        f.write('\n')
        f.close()
        
        sleep(2)
        a = requests.get(auction_dump_url)
        api_calls_count += 1

        auc_data = a.json()["auctions"]
        conn_data = a.json()["realms"]
        del a
        connected_realms = []
        for r in conn_data:
            connected_realms.append(r['slug'])
        del conn_data
        
        
        for h in connected_realms:
            
            servers[h] = s
        
        for g in auc_data:
            if g['item'] == 82800:
                g['item'] = int('82800' + str(g['petSpeciesId']))
            if g['item'] in items and int(g['buyout']) > 0:
                try:
                    raw_auctions[g['item']][0] += g['quantity']
                    raw_auctions[g['item']].append({'item' : g['item'], 'buyout' : g['buyout'], 'quantity' : g['quantity'], 'per_item' : g['buyout'] / g['quantity']})
                except:
                    raw_auctions[g['item']] = [g['quantity'], {'item' : g['item'], 'buyout' : g['buyout'], 'quantity' : g['quantity'], 'per_item' : g['buyout'] / g['quantity']}]

        del auc_data
        
        for j in items:
            if j not in raw_auctions:
                continue
                 
            total_q = raw_auctions[j].pop(0)
            mkt_q = 0
            mkt_gold = 0
            auctions = raw_auctions[j]
            
            auctions_sorted = sorted(auctions, key=itemgetter('per_item'))
            for k in auctions_sorted:
                mkt_gold += k['buyout']
                mkt_q += k['quantity']
                if mkt_q > 0.15 * total_q:
                    break
            if total_q == mkt_q == 0:
                continue
            items[j]['price'] = mkt_gold / mkt_q
            items[j]['quantity'] = total_q

        del raw_auctions
        del auctions_sorted
        for h in items:
            if items[h]["price"] > 0:
                try:
                    avg_price_eu[h][0] += items[h]["price"]
                    avg_price_eu[h][1] += 1
                except:
                    continue



        with gzip.GzipFile('/home/sweetpea/webapps/server_data/item_db_master_'+s+'_en_GB.json', 'w') as f:
             f.write(json.dumps(items).encode('utf-8'))
        del items
        servers_updated_count += 1


    b = open("/home/sweetpea/webapps/server_data/avg_price_en_GB.json", "w")
    b.write(json.dumps(avg_price_eu))
    b.close()
    del avg_price_eu
    
    f = open("/home/sweetpea/webapps/cron_debug_log.txt", "a")
    f.write("Servers updated: "+str(servers_updated_count))
    f.write('\n')
    f.write("API calls: "+str(api_calls_count))
    f.close()


@kronos.register('1 * * * *')
def get_auc_data_us():
    servers = {}
    avg_price_us = {}
    api_calls_count = 0
    servers_updated_count = 0
    
    with open('/home/sweetpea/public_html/item_db_img_v2.json') as realm_file:
        realms = json.load(realm_file)['realms']
    with open('/home/sweetpea/public_html/item_db_img_v2.json') as avg_temp:
    	items = json.load(avg_temp)["items"]
    for j in realms["en_US"]:
        servers[j['slug']] = ''
        #servers.append([j['slug'], "en_US"])
    #servers = {'medivh' : '', 'exodar' : ''}
    for l in items:
        avg_price_us[int(l)] = [0, 0]
    del items
    del realms
    for s in servers:
        #time.sleep(3)
        if servers[s] != '':
            parent = servers[s]
            src = '/home/sweetpea/webapps/server_data/item_db_master_' +parent+ '_en_US.json'
            dst = '/home/sweetpea/webapps/server_data/item_db_master_'+s+'_en_US.json'
           
            copyfile(src, dst) 

            
            servers_updated_count += 1
            continue
        #time.sleep(5)
        items = {}
        raw_auctions = {}
        with open('/home/sweetpea/webapps/item_db_img.json') as data_file:
            for line in data_file:
                item = {}
                data = json.loads(line)
                item["id"] = data[0]
                item["name"] = data[1]
                item["img_url"] = data[2][45:-4]
                if len(data) > 3:
                    item["pet_id"] = data[3]
                item["price"] = 0
                item["quantity"] = 0
                item["average"] = 0
                items[data[0]] = item
                del item

        
        r = requests.get("https://us.api.battle.net/wow/auction/data/"+s+"?locale=en_US&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw", timeout=20)
        #time.sleep(3)
        
        try:
            auction_dump_url = json.loads(r.text)["files"][0]["url"]
        except (ValueError, KeyError):
            f = open("/home/sweetpea/webapps/cron_debug_log.txt", "a")
            f.write('API error')
            f.write(r.text)
            f.write('\n')
            f.close()
            continue
        
        del r
        f = open("/home/sweetpea/webapps/cron_debug_log.txt", "a")
        #f.write('API error')
        f.write(auction_dump_url)
        f.write('\n')
        f.close()
        
        #time.sleep(5)
        a = requests.get(auction_dump_url, timeout=30)
        api_calls_count += 1

        auc_data = a.json()["auctions"]
        conn_data = a.json()["realms"]
        del a
        connected_realms = []
        for r in conn_data:
            connected_realms.append(r['slug'])
        del conn_data
        
        
        for h in connected_realms:
            
            servers[h] = s
        
        for g in auc_data:
            if g['item'] == 82800:
                g['item'] = int('82800' + str(g['petSpeciesId']))
            if g['item'] in items and int(g['buyout']) > 0:
                try:
                    raw_auctions[g['item']][0] += g['quantity']
                    raw_auctions[g['item']].append({'item' : g['item'], 'buyout' : g['buyout'], 'quantity' : g['quantity'], 'per_item' : g['buyout'] / g['quantity']})
                except:
                    raw_auctions[g['item']] = [g['quantity'], {'item' : g['item'], 'buyout' : g['buyout'], 'quantity' : g['quantity'], 'per_item' : g['buyout'] / g['quantity']}]

        del auc_data
        
        for j in items:
            if j not in raw_auctions:
                continue
                 
            total_q = raw_auctions[j].pop(0)
            mkt_q = 0
            mkt_gold = 0
            auctions = raw_auctions[j]
            
            auctions_sorted = sorted(auctions, key=itemgetter('per_item'))
            for k in auctions_sorted:
                mkt_gold += k['buyout']
                mkt_q += k['quantity']
                if mkt_q > 0.15 * total_q:
                    break
            if total_q == mkt_q == 0:
                continue
            items[j]['price'] = mkt_gold / mkt_q
            items[j]['quantity'] = total_q

        del raw_auctions
        del auctions_sorted
        for h in items:
            if items[h]["price"] > 0:
                try:
                    avg_price_us[h][0] += items[h]["price"]
                    avg_price_us[h][1] += 1
                except:
                    continue



        with gzip.GzipFile('/home/sweetpea/webapps/server_data/item_db_master_'+s+'_en_US.json', 'w') as f:
             f.write(json.dumps(items).encode('utf-8'))
        del items
        servers_updated_count += 1

    f = open("/home/sweetpea/webapps/cron_debug_log.txt", "a")
    f.write("Server update finished, writing avg price data...")
    f.write('\n')
    f.close()
    
    b = open("/home/sweetpea/webapps/server_data/avg_price_en_US.json", "w")
    b.write(json.dumps(avg_price_us))
    b.close()
    del avg_price_us
    
    f = open("/home/sweetpea/webapps/cron_debug_log.txt", "a")
    f.write("Servers updated: "+str(servers_updated_count))
    f.write('\n')
    f.write("API calls: "+str(api_calls_count))
    f.close()


@kronos.register('40 3 * * *')
def update_data():
    id_array = []
    servers = [["tichondrius", "en_US"], ["dalaran", "en_US"], ["stormrage", "en_US"], ["illidan", "en_US"], ["sargeras", "en_US"], ["area-52", "en_US"], ["frostmourne", "en_US"], ["darkspear", "en_US"], ["emerald-dream", "en_US"], ["moon-guard", "en_US"], ["proudmoore", "en_US"], ["outland", "en_GB"], ["sargeras", "en_GB"], ["silvermoon", "en_GB"], ["draenor", "en_GB"], ["stormscale", "en_GB"], ["gordunni", "en_GB"], ["kazzak", "en_GB"], ["ravencrest", "en_GB"], ["twisting-nether", "en_GB"], ["sylvanas", "en_GB"], ["soulflayer", "en_GB"]]
    #servers = [['sargeras', 'en_US']]
    invalid_ids = ["5108", "15726","5140","9186","5487","823","11206"]
    
    with open('/home/sweetpea/webapps/item_db_img.json') as data_file:    
        for line in data_file:
            data = json.loads(line)
            id_array.append(data[0])
            
    for s in servers:
        
        if s[1] == "en_GB":
            r = requests.get("https://eu.api.battle.net/wow/auction/data/"+s[0]+"?locale="+s[1]+"&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw")
        elif s[1] == "en_US":
            r = requests.get("https://us.api.battle.net/wow/auction/data/"+s[0]+"?locale="+s[1]+"&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw")
        auction_dump_url = json.loads(r.text)["files"][0]["url"]
        a = requests.get(auction_dump_url)
        auc_data = a.json() 
        
        for i in auc_data["auctions"]:       
            if i['item'] == 82800 and int('82800' + str(i['petSpeciesId'])) not in id_array:
                f = open('/home/sweetpea/webapps/item_db_img.json', 'a')
                id_array.append(int('82800' + str(i['petSpeciesId'])))
                item_pair = []
                item_id = '82800' + str(i['petSpeciesId'])
                item_pair.append(int('82800' + str(i['petSpeciesId'])))
                url_parts = ("https://us.api.battle.net/wow/pet/species/", str(i['petSpeciesId']),  "?locale=en_US&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw")
                PET_API_URL = "".join(url_parts)
                pet_r = requests.get(PET_API_URL)
                try:
                    pet_data = pet_r.json()
                    item_name = pet_data['name']
                    item_icon = pet_data['icon']
                    img_parts = ("https://wow.zamimg.com/images/wow/icons/large/", item_icon,  ".jpg")
                    IMAGE_URL = "".join(img_parts)
                    item_pair.append(item_name)
                    item_pair.append(IMAGE_URL)
                    item_pair.append(pet_data['creatureId'])
                    f.write(json.dumps(item_pair) + '\n')
                    f.close()
                except (KeyError, ValueError):
                    #print "Invalid ID"
                    invalid_ids.append(str(item_id))
                    continue
            if i["item"] not in id_array and i['item'] != 82800:
                f = open('/home/sweetpea/webapps/item_db_img.json', 'a')
                id_array.append(i["item"])
                item_pair = []
                item_id = str(i["item"])
                if item_id in invalid_ids:
                    continue
                item_pair.append(i["item"])
                url_parts = ("https://us.api.battle.net/wow/item/", item_id,  "?locale=en_US&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw")
                ITEM_API_URL = "".join(url_parts)
                item_r = requests.get(ITEM_API_URL)
                try:
                    item_data = item_r.json()
                    item_name = item_data["name"]
                    item_icon = item_data["icon"]
                    img_parts = ("https://wow.zamimg.com/images/wow/icons/large/", item_icon,  ".jpg")
                    IMAGE_URL = "".join(img_parts)
                    item_pair.append(item_name)
                    item_pair.append(IMAGE_URL)
                    f.write(json.dumps(item_pair) + '\n')
                    f.close() 
                except (KeyError, ValueError):
                    #print "Invalid ID"
                    invalid_ids.append(str(item_id))
                    continue

    input_array = []
    id_array = []
    duplicates = 0
    items_array = {}
    legacy_array = []
    
    with open('/home/sweetpea/webapps/item_db_img.json') as data_file:    
        for line in data_file:
            data = json.loads(line)
            input_array.append(data)
    
    with open('/home/sweetpea/webapps/realms.json') as realm_file:
        realms = json.load(realm_file)    
    
            
    out_array = sorted(input_array, key = lambda id: id[0])
            
    
    for i in out_array:
        if i[0] in id_array:
            duplicates += 1
            continue
        id_array.append(i[0])
        if len(i) == 4:
            item_data = {"id": i[0], "name": i[1], "img_url": i[2], "pet_id": i[3]}
        else:
            item_data = {"id": i[0], "name": i[1], "img_url": i[2]}
        items_array[i[0]] = item_data
        legacy_array.append(item_data)
        
    out = {"items": items_array, "realms":realms}
    out_legacy = {"items": legacy_array, "realms":realms}
    
    f = open('/home/sweetpea/public_html/item_db_img_v2.json', 'w')
    f.write(json.dumps(out, indent=1) )
    f.close()
    
    f = open('/home/sweetpea/public_html/item_db_img_sorted.json', 'w')
    f.write(json.dumps(out_legacy, indent=1) )
    f.close()