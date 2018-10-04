import json
import gzip
import os
from passlib.hash import pbkdf2_sha256



def get_items(inc):
    
    result = []
    region = inc.pop(0)
    server = inc.pop(0)
    result.append(os.path.getmtime('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json'))
    with gzip.GzipFile('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json', 'rb') as data_file:        
        items = json.loads(data_file.read().decode('ascii'))
    
    with open('/home/sweetpea/webapps/server_data/avg_price_'+ region + '.json') as prices_file:    
        avg_prices = json.load(prices_file)
        
    with open('/home/sweetpea/public_html/recipes_v2.json') as recipes_file:
        recipes = json.load(recipes_file)
        
    
    
    for i in inc:
        if len(avg_prices) > 0 and avg_prices[i][1] > 0:
            items[i]['average'] = avg_prices[i][0] / avg_prices[i][1]
        items[i]['img_url'] = "https://wow.zamimg.com/images/wow/icons/large/" + items[i]['img_url'] + ".jpg"
        if items[i]['img_url'].endswith(".jpg.jpg"):
            items[i]['img_url'] = items[i]['img_url'][46:-4]
        if i in recipes:
            items[i]["rank3"] = recipes[i]["rank3"]
            items[i]["alchemy"] = recipes[i]["alchemy"]
            for k in recipes[i]["components"]:
                k['price'] = items[str(k['id'])]['price']
                k['img_url'] = "https://wow.zamimg.com/images/wow/icons/large/" + k['img_url'] + ".jpg"
            items[i]['components'] = recipes[i]["components"]
        result.append(items[i])
        
    
    with open ('debug.json', 'w') as f:
        f.write(json.dumps(result, indent = 1))
    return result
 
def add_user_entry(username, pwd, region, item_list=[]):
    with open('user_db.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db.json') as q:
        users = json.load(q)['users']
    if username not in usernames:
        pwd_hash = pbkdf2_sha256.hash(pwd)
        user_data = {'username': username, 'hash': pwd_hash, 'saved_items': item_list, 'region':region}
        usernames.append(username)
        users.append(user_data)
        out = {'users': users, 'usernames': usernames}
        with open ('user_db.json', 'w') as f:
            f.write(json.dumps(out, indent = 2))
        return {'auth_token':pbkdf2_sha256.hash(pwd_hash),'error_msg':'teeest'}
    else:
        return 'Error - user already exists'
            
def get_user_data(username, pwd):
    with open('user_db.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db.json') as q:
        users = json.load(q)['users']
    if username not in usernames:
        return 'Error - invalid email or password'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(pwd, i['hash']) == True:
            with open('/home/sweetpea/public_html/item_db_img_v2.json') as data_file:    
                result =[]
                data = json.load(data_file)['items']
                for j in i['saved_items']:
                    result.append({'name': data[j]['name'].lower(), 'id': int(data[j]['id'])})                
            return {'region': i['region'], 'items': result, 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':'toooost'}
        if i['username'] == username and pbkdf2_sha256.verify(pwd, i['hash']) == False:
            return 'Error - invalid email or password'
            
def get_user_data_cookie(username, auth_token):
    with open('user_db.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db.json') as q:
        users = json.load(q)['users']
    if username not in usernames:
        return 'Error - invalid email or password'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == True:
            with open('/home/sweetpea/public_html/item_db_img_v2.json') as data_file:    
                result =[]
                data = json.load(data_file)['items']
                for j in i['saved_items']:
                    result.append({'name': data[j]['name'].lower(), 'id': int(data[j]['id'])})                
            return {'region': i['region'], 'items': result, 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':'taaast'}
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == False:
            return 'Error - invalid email or password'
                
                
def update_user_entry(username, auth_token, region, item_list):
    with open ('debug_auth.json', 'w') as f:
        f.write(auth_token)
    with open('user_db.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db.json') as q:
        users = json.load(q)['users']
    if username not in usernames:
        return 'Error - no such user exists'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == True:
            i['saved_items'] = item_list
            i['region'] = region
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == False:
            return 'Invalid password'
    out = {'users': users, 'usernames': usernames}
    with open ('user_db.json', 'w') as f:
        f.write(json.dumps(out, indent = 2))
    return  {'auth_token':pbkdf2_sha256.hash(i['hash']), 'error_msg':'tiiiist'}

#print get_user_data('admin', 'optsem63')
#print get_user_data_cookie('admin', '$pbkdf2-sha256$29000$CaFU6v1f6/2/t7Z2bs3ZWw$1tm2eyy5sPn9Jl4NjA3GoZLFxn0lpWN805esdhxQGgw')