import json
import gzip
import os
import collections
import io
from passlib.hash import pbkdf2_sha256

def get_items_locale(inc):
    with open ('debug2.txt', 'w') as f:
        f.write(json.dumps(inc, indent = 1))
    result = []
    locale = inc.pop(0)
    region = inc.pop(0)
    server = inc.pop(0)
    result.append(os.path.getmtime('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json'))
    with gzip.GzipFile('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json', 'rb') as data_file:
        items = json.loads(data_file.read().decode('ascii'))

    with open('/home/sweetpea/webapps/server_data/avg_price_'+ region + '.json') as prices_file:
        avg_prices = json.load(prices_file)

    with open('/home/sweetpea/public_html/recipes_v2.json') as recipes_file:
        recipes = json.load(recipes_file)

    if locale not in ('en_US', 'en_GB'):
        with io.open('/home/sweetpea/public_html/item_db_locale.json', 'r', encoding='utf8') as partial:
            items_locale = json.load(partial)['items']
    else:
        items_locale = [0, 0]

    for i in inc:
        if len(items_locale)>4:
            for j in items_locale:
                if j['name'] == items[i]["name"]:
                    if locale in ('pt_PT', 'pt_BR'):
                        items[i]["name"] = j['pt_BR']
                        break
                    elif locale in ('es_ES', 'es_MX'):
                        items[i]["name"] = j['es_ES']
                        break
                    else:
                        items[i]["name"] = j[locale]
                        break

        if len(avg_prices) > 0 and avg_prices[i][1] > 0:
            items[i]['average'] = avg_prices[i][0] / avg_prices[i][1]
        items[i]['img_url'] = "https://wow.zamimg.com/images/wow/icons/large/" + items[i]['img_url'] + ".jpg"
        if items[i]['img_url'].endswith(".jpg.jpg"):
            items[i]['img_url'] = items[i]['img_url'][46:-4]
        if i in recipes:
            items[i]["rank3"] = recipes[i]["rank3"]
            items[i]["alchemy"] = recipes[i]["alchemy"]
            for k in recipes[i]["components"]:
                if len(items_locale)>4:
                    for j in items_locale:
                        if j['name'] == k["name"]:
                            if locale in ('pt_PT', 'pt_BR'):
                                k["name"] = j['pt_BR']
                                break
                            elif locale in ('es_ES', 'es_MX'):
                                k["name"] = j['es_ES']
                                break
                            else:
                                k["name"] = j[locale]
                                break

                k['price'] = items[str(k['id'])]['price']
                k['img_url'] = "https://wow.zamimg.com/images/wow/icons/large/" + k['img_url'] + ".jpg"
            items[i]['components'] = recipes[i]["components"]
        result.append(items[i])


    #with open ('debug.json', 'w') as f:
        #f.write(json.dumps(result, indent = 1))
    return result

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

def add_user_entry(json_dict):
    username = json_dict['login']
    pwd = json_dict['pwhash']
    active_list = json_dict['active_list']
    region =[]
    region.append(json_dict['region'])
    region.append(json_dict['server'])
    region.append(json_dict['slug'])
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        pwd_hash = pbkdf2_sha256.hash(pwd)
        user_data = {'username': username, 'lang': json_dict['lang'], 'locale_lang': json_dict['locale_lang'], 'hash': pwd_hash, 'active_list':active_list, 'itemLists': json_dict['itemLists'], 'region':region}
        usernames.append(username)
        users.append(user_data)
        out = {'users': users, 'usernames': usernames}
        with open ('user_db_v2.json', 'w') as f:
            f.write(json.dumps(out, indent = 2))
        return {'auth_token':pbkdf2_sha256.hash(pwd_hash),'error_msg':''}
    else:
        return 'Error - user already exists'

def add_user_entry_new(json_dict):
    username = json_dict['login']
    pwd = json_dict['pwhash']
    active_list = json_dict['active_list']
    region =[]
    region.append(json_dict['region'])
    region.append(json_dict['server'])
    region.append(json_dict['slug'])
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        pwd_hash = pbkdf2_sha256.hash(pwd)
        user_data = {'username': username, 'hash': pwd_hash, 'active_list':active_list, 'itemLists': json_dict['itemLists'], 'region':region}
        usernames.append(username)
        users.append(user_data)
        out = {'users': users, 'usernames': usernames}
        with open ('user_db_v2.json', 'w') as f:
            f.write(json.dumps(out, indent = 2))
        return {'auth_token':pbkdf2_sha256.hash(pwd_hash),'error_msg':''}
    else:
        return 'Error - user already exists'

def get_user_data(json_dict):
    username = json_dict['login']
    pwd = json_dict['pwhash']
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        return 'Error - invalid email or password'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(pwd, i['hash']) == True:
            try:
                return {'region': i['region'], 'lang': i['lang'], 'locale_lang': i['locale_lang'], 'active_list':i['active_list'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
            except:
                return {'region': i['region'], 'lang': i['lang'], 'locale_lang': i['locale_lang'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
        if i['username'] == username and pbkdf2_sha256.verify(pwd, i['hash']) == False:
            return 'Error - invalid email or password'

def get_user_data_new(json_dict):
    username = json_dict['login']
    pwd = json_dict['pwhash']
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        return 'Error - invalid email or password'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(pwd, i['hash']) == True:
            try:
                return {'region': i['region'], 'active_list':i['active_list'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
            except:
                return {'region': i['region'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
        if i['username'] == username and pbkdf2_sha256.verify(pwd, i['hash']) == False:
            return 'Error - invalid email or password'

def get_user_data_cookie(json_dict):
    username = json_dict['login']
    auth_token = json_dict['pwhash']
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        return 'Error - invalid email or password'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == True:
            try:
                return {'region': i['region'], 'lang': i['lang'], 'locale_lang': i['locale_lang'], 'active_list':i['active_list'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
            except:
                return {'region': i['region'], 'lang': i['lang'], 'locale_lang': i['locale_lang'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == False:
            return 'Error - invalid email or password'

def get_user_data_cookie_new(json_dict):
    username = json_dict['login']
    auth_token = json_dict['pwhash']
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        return 'Error - invalid email or password'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == True:
            try:
                return {'region': i['region'], 'active_list':i['active_list'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
            except:
                return {'region': i['region'], 'itemLists': i['itemLists'], 'auth_token': pbkdf2_sha256.hash(i['hash']), 'error_msg':''}
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == False:
            return 'Error - invalid email or password'


def update_user_entry(json_dict):
    username = json_dict['login']
    auth_token = json_dict['pwhash']
    active_list = json_dict['active_list']
    region =[]
    region.append(json_dict['region'])
    region.append(json_dict['server'])
    region.append(json_dict['slug'])
    with open ('debug_auth.json', 'w') as f:
        f.write(auth_token)
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        return 'Error - no such user exists'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == True:
            i['itemLists'] = json_dict['itemLists']
            i['locale_lang'] = json_dict['locale_lang']
            i['lang'] = json_dict['lang']
            i['region'] = region
            i['active_list'] = active_list
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == False:
            return 'Invalid password'
    out = {'users': users, 'usernames': usernames}
    with open ('user_db_v2.json', 'w') as f:
        f.write(json.dumps(out, indent = 2))
    return  {'auth_token':pbkdf2_sha256.hash(i['hash']), 'error_msg':''}

def update_user_entry_new(json_dict):
    username = json_dict['login']
    auth_token = json_dict['pwhash']
    active_list = json_dict['active_list']
    region =[]
    region.append(json_dict['region'])
    region.append(json_dict['server'])
    region.append(json_dict['slug'])
    with open ('debug_auth.json', 'w') as f:
        f.write(auth_token)
    with open('user_db_v2.json') as r:
        usernames = json.load(r)['usernames']
    with open('user_db_v2.json') as q:
        users = collections.OrderedDict()
        users = json.load(q, object_pairs_hook=collections.OrderedDict)['users']
    if username not in usernames:
        return 'Error - no such user exists'
    for i in users:
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == True:
            i['itemLists'] = json_dict['itemLists']
            i['region'] = region
            i['active_list'] = active_list
        if i['username'] == username and pbkdf2_sha256.verify(i['hash'], auth_token) == False:
            return 'Invalid password'
    out = {'users': users, 'usernames': usernames}
    with open ('user_db_v2.json', 'w') as f:
        f.write(json.dumps(out, indent = 2))
    return  {'auth_token':pbkdf2_sha256.hash(i['hash']), 'error_msg':''}

#print get_user_data('admin', 'optsem63')
#print get_user_data_cookie('admin', '$pbkdf2-sha256$29000$CaFU6v1f6/2/t7Z2bs3ZWw$1tm2eyy5sPn9Jl4NjA3GoZLFxn0lpWN805esdhxQGgw')
