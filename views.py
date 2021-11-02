import json
import requests
import os
import shutil
import collections
import io

from grape.auc_functions import *
from grape.upload import UploadFileForm
from grape import utils
from time import sleep
from time import time

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django import forms

result = []
API_URL="https://us.api.battle.net/wow/auction/data/sargeras?locale=en_US&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw"

@csrf_exempt
def user_edit(request):
    if request.method == 'GET':
        with open('user_db_v2.json', 'r') as r:
            data = json.load(r)
            return render(request, 'grape/users.html', {'data':data})

@csrf_exempt
def long_poll(request):
    curr_time = time()
    temp = request.POST
    f = open("long_poll_log.txt", "w")
    meta_temp = request.META
    f.write(str(meta_temp))
    f.write("\n")
    client_ip = meta_temp['REMOTE_ADDR']
    f.write(client_ip)
    f.write("\n")

    with open('/home/sweetpea/webapps/lp_reg.json') as request_log:
        pending_requests = json.load(request_log)

    pending_requests[str(client_ip)] = curr_time

    with open('/home/sweetpea/webapps/lp_reg.json', 'w') as request_log:
        result = json.dumps(pending_requests, indent = 2)
        request_log.write(result)

    #meta_dict = meta_temp.dict()
    #meta_list = list(meta_list)
    #meta_json = json.loads(meta_list[0])
    #f.write(json.dumps(json_dict, indent=1))
    #f.write("\n")
    f.write(str(temp))
    f.write("\n")
    act_dict = temp.dict()
    f.write(str(act_dict))
    f.write("\n")
    list_dict = list(act_dict)
    f.write(str(list_dict))
    f.write("\n")
    json_dict = json.loads(list_dict[0])
    f.write(json.dumps(json_dict, indent=1))
    f.write("\n")
    f.close()

    server = json_dict['server']
    region = json_dict['region']
    if str(json_dict['forceUpdate']) == 'true':
        mod_time = os.path.getmtime('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json')
        out = json.dumps([{'time':mod_time}, {'server':server}, {'region':region}, {'msg':'forced response'}], indent = 1)
        return HttpResponse(out)

    while json_dict['time'] == os.path.getmtime('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json'):
        sleep(30)
        try:
            with open('/home/sweetpea/webapps/lp_reg.json', 'r') as request_log:
                pending_requests = json.load(request_log)
            if pending_requests[str(client_ip)] > curr_time:
                #mod_time = os.path.getmtime('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json')
                out = json.dumps([{'time':000}, {'server':server}, {'region':region}, {'msg':'obsolete request terminated'}], indent = 1)
                return HttpResponse(out)
            sleep(2)
        except:
            with open('lp_err_log.json', 'a') as error_log:
                error_log.write('main cycle error')
            sleep(2)
            continue

    try:
        mod_time = os.path.getmtime('/home/sweetpea/webapps/server_data/item_db_master_' + server + '_' + region + '.json')
        out = json.dumps([{'time':mod_time}, {'server':server}, {'region':region}, {'msg':'update avaliable'}], indent = 1)
        f = open("long_poll_log_out.txt", "w")
        f.write(out)
        f.close()
        return HttpResponse(out)
    except:
        with open('lp_err_log.json', 'a') as error_log:
            error_log.write('response generation error')
        out = json.dumps([{'time':000}, {'server':server}, {'region':region}, {'msg':'error generating response'}], indent = 1)
        return HttpResponse(out)

@csrf_exempt
def get_file(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        file_urls = []
        for i in request.FILES:
            myfile = request.FILES[i]
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            file_urls.append(uploaded_file_url)
        #temp = {"files": file_urls}
        out = json.dumps(file_urls, indent = 1)
        f = open("file_transfer_log.txt", "w")
        f.write(out)
        f.write('\n')
        f.write(str(request.FILES))
        f.close()
        return HttpResponse(out)

@csrf_exempt
def axios_test(request):
    f = open("axios_log.txt", "w")

    if request.method == 'GET':
        f.write("GET request:"+"\n")
        f.close()
        return render(request, 'grape/test.html', {})
    else:

        f.write("POST request:"+"\n")
        temp = request.POST
        f.write(str(temp)+"\n")
        try:
            temp = request.json()
            f.write(".json request:"+"\n")
            f.write(str(temp)+"\n")
        except:
            f.write("error attempting to jsonify"+"\n")
        # f.write("\n")
        # act_dict = temp.dict()
        # f.write(str(act_dict))
        # f.write("\n")
        # list_dict = list(act_dict)
        # f.write(str(list_dict))
        # f.write("\n")
        # json_dict = json.loads(list_dict[0])
        # f.write(json.dumps(json_dict, indent=1))
        # f.write("\n")
        f.close()

        return HttpResponse("request received")

@csrf_exempt
def test_file(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        file_urls = []
        f = open("file_transfer_log_test.txt", "w")
        f.write(str(request.FILES))
        f.write('\n')
        myform = UploadFileForm(request.POST, request.FILES)
        f.write(str(myform))
        f.write('\n')
        f.close()
        for i in request.FILES:
            myfile = request.FILES[i]
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            file_urls.append(uploaded_file_url)
        out = json.dumps(file_urls, indent = 1)
        return HttpResponse(json.dumps({ 'success': True, 'files': out }))

@csrf_exempt
def delete_file(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        f = open("file_delete_log.txt", "w")
        f.write(str(request.POST))
        f.write('\n')
        filename = request.POST.getlist('name')[0]
        f.write(str(filename))
        f.close()
        if os.path.isfile('/home/sweetpea/public_html/media_up/' + str(filename)):
            os.remove('/home/sweetpea/public_html/media_up/' + str(filename))
            return HttpResponse('success')
        return HttpResponse('error - file not found')

@csrf_exempt
def get_user(request):
    temp = request.POST
    act_dict = temp.dict()
    list_dict = list(act_dict)
    json_dict = collections.OrderedDict()
    json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
    temp = get_user_data(json_dict)
    out = json.dumps(temp, indent = 1)
    return HttpResponse(out)

@csrf_exempt
def get_user_new(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        f = open("get_user_log.txt", "w")
        f.write("POST request:")
        f.write("\n")
        temp = request.POST
        f.write(str(temp))
        f.write("\n")
        act_dict = temp.dict()
        f.write(str(act_dict))
        f.write("\n")
        list_dict = list(act_dict)
        f.write(str(list_dict))
        f.write("\n")
        json_dict = collections.OrderedDict()
        json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
        f.write(json.dumps(json_dict, indent=1))
        f.write("\n")
        f.close()

        temp = get_user_data_new(json_dict)
        out = json.dumps(temp, indent = 1)
        f = open("get_user_log.txt", "a")
        f.write(out)
        f.close()
        return HttpResponse(out)

@csrf_exempt
def get_user_cookie(request):
    temp = request.POST
    act_dict = temp.dict()
    list_dict = list(act_dict)
    json_dict = collections.OrderedDict()
    json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)

    temp = get_user_data_cookie(json_dict)
    out = json.dumps(temp, indent = 1)
    return HttpResponse(out)

@csrf_exempt
def get_user_cookie_new(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        f = open("cookie_user_log.txt", "w")
        f.write("POST request:")
        f.write("\n")
        temp = request.POST
        f.write(str(temp))
        f.write("\n")
        act_dict = temp.dict()
        f.write(str(act_dict))
        f.write("\n")
        list_dict = list(act_dict)
        f.write(str(list_dict))
        f.write("\n")
        json_dict = collections.OrderedDict()
        json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
        f.write(json.dumps(json_dict, indent=1))
        f.write("\n")
        f.close()


        temp = get_user_data_cookie_new(json_dict)
        out = json.dumps(temp, indent = 1)
        f = open("cookie_user_log.txt", "a")
        f.write(out)
        f.close()
        return HttpResponse(out)

@csrf_exempt
def test(request):
    if request.method == 'GET':
        return render(request, 'grape/index.html', {})
    else:
        temp = request.POST
        f = open("test_log.txt", "w")
        f.write(str(temp))
        f.write("\n")
        act_dict = temp.dict()
        f.write(str(act_dict))
        f.write("\n")
        list_dict = list(act_dict)
        f.write(str(list_dict))
        f.write("\n")
        json_dict = json.loads(list_dict[0])
        f.write(json.dumps(json_dict, indent=1))
        f.write("\n")
        f.close()

        d = []
        d.append(json_dict['region'])
        d.append(json_dict['server'])
        for i in json_dict['itemLists']['list1']:
            d.append(str(i))

        items = get_items(d)
        mod_time = items.pop(0)
        #{'resp': [{'time':mod_time}, {'items':items}]}
        out = json.dumps([{'time':mod_time}, {'items':items}, {'error_msg':''}], indent = 1)
        f = open("test_log.txt", "a")
        f.write(out)
        f.close()
        return HttpResponse(out)

@csrf_exempt
def multiList(request):
    temp = request.POST
    f = open("test_log3.txt", "w")
    f.write(str(request.META))
    #f.write(str(request.META['REMOTE_ADDR']))
    f.write(str(temp))
    f.write("\n")
    act_dict = temp.dict()
    f.write(str(act_dict))
    f.write("\n")
    list_dict = list(act_dict)
    f.write(str(list_dict))
    f.write("\n")
    json_dict = collections.OrderedDict()
    json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
    f.write(json.dumps(json_dict, indent=1))
    f.write("\n")
    f.close()

    item_lists = collections.OrderedDict()
    #item_lists = {}
    for i in json_dict['itemLists']:
        d = []
        d.append(json_dict['lang'])
        d.append(json_dict['region'])
        d.append(json_dict['server'])
        for j in json_dict['itemLists'][i]:
            d.append(str(j['id']))

        items = get_items_locale(d)
        mod_time = items.pop(0)
        item_lists[i] = items
    #{'resp': [{'time':mod_time}, {'items':items}]}
    out = json.dumps([{'time':mod_time}, {'itemLists':item_lists}, {'error_msg':''}], indent = 1)
    f = open("test_log3.txt", "a")
    f.write(out)
    f.close()
    return HttpResponse(out)

@csrf_exempt
def multiList_test(request):
    if request.method == 'GET':
        return render(request, 'grape/index.html', {})
    else:
        temp = request.POST
        f = open("test_log3.txt", "w")
        f.write(str(request.META))
        #f.write(str(request.META['REMOTE_ADDR']))
        f.write(str(temp))
        f.write("\n")
        act_dict = temp.dict()
        f.write(str(act_dict))
        f.write("\n")
        list_dict = list(act_dict)
        f.write(str(list_dict))
        f.write("\n")
        json_dict = collections.OrderedDict()
        json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
        f.write(json.dumps(json_dict, indent=1))
        f.write("\n")
        f.close()

        item_lists = collections.OrderedDict()
        #item_lists = {}
        for i in json_dict['itemLists']:
            d = []
            d.append(json_dict['region'])
            d.append(json_dict['server'])
            for j in json_dict['itemLists'][i]:
                d.append(str(j['id']))

            items = get_items(d)
            mod_time = items.pop(0)
            item_lists[i] = items
        #{'resp': [{'time':mod_time}, {'items':items}]}
        out = json.dumps([{'time':mod_time}, {'itemLists':item_lists}, {'error_msg':''}], indent = 1)
        f = open("test_log3.txt", "a")
        f.write(out)
        f.close()
        return HttpResponse(out)

@csrf_exempt
def add_user(request):
    temp = request.POST
    act_dict = temp.dict()
    list_dict = list(act_dict)
    json_dict = collections.OrderedDict()
    json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
    temp = add_user_entry(json_dict)
    out = json.dumps(temp, indent = 1)
    return HttpResponse(out)

@csrf_exempt
def add_user_new(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        temp = request.POST
        f = open("add_user_log.txt", "w")
        f.write(str(temp))
        f.write("\n")
        act_dict = temp.dict()
        f.write(str(act_dict))
        f.write("\n")
        list_dict = list(act_dict)
        f.write(str(list_dict))
        f.write("\n")
        json_dict = collections.OrderedDict()
        json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
        f.write(json.dumps(json_dict, indent=1))
        f.write("\n")
        f.close()

        temp = add_user_entry_new(json_dict)
        out = json.dumps(temp, indent = 1)
        return HttpResponse(out)

@csrf_exempt
def update_user_new(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        temp = request.POST
        f = open("upd_user_log.txt", "w")
        f.write(str(temp))
        f.write("\n")
        act_dict = temp.dict()
        f.write(str(act_dict))
        f.write("\n")
        list_dict = list(act_dict)
        f.write(str(list_dict))
        f.write("\n")
        json_dict = collections.OrderedDict()
        #json_dict = list_dict[0]
        json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
        f.write(json.dumps(json_dict, indent=1))
        f.write("\n")
        f.close()


        temp = update_user_entry_new(json_dict)
        out = json.dumps(temp, indent = 1)
        return HttpResponse(out)


@csrf_exempt
def update_user(request):
    temp = request.POST
    act_dict = temp.dict()
    list_dict = list(act_dict)
    json_dict = collections.OrderedDict()
    json_dict = json.loads(list_dict[0], object_pairs_hook=collections.OrderedDict)
    temp = update_user_entry(json_dict)
    out = json.dumps(temp, indent = 1)
    return HttpResponse(out)


@csrf_exempt
def mix(request):

    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        d = []
        items = []

        f = open("debug_log.txt", "w")
        f.write(str(request.POST))
        f.write("\n")

        f.close()

        inc_array = request.POST.getlist("items[]")

        for i in inc_array:
            d.append(i)

        #f.write(str(d))
        #f.write("\n")

        items = get_items(d)
        mod_time = items.pop(0)
        {'resp': [{'time':mod_time}, {'items':items}]}
        out = json.dumps([{'time':mod_time}, {'items':items}, {'error_msg':''}], indent = 1)

        #f.write(out)
        #f.close
        return HttpResponse(out)

def handle_upload(f, fileattrs):
    """ Handle a chunked or non-chunked upload.
    """


    chunked = False
    dest_folder = os.path.join('/home/sweetpea/public_html/media_up/', fileattrs['qquuid'])
    dest = os.path.join(dest_folder, fileattrs['qqfilename'])

    # Chunked
    if fileattrs.get('qqtotalparts') and int(fileattrs['qqtotalparts']) > 1:
        chunked = True
        dest_folder = os.path.join('/home/sweetpea/public_html/media_up/', fileattrs['qquuid'])
        dest = os.path.join(dest_folder, fileattrs['qqfilename'], str(fileattrs['qqpartindex']))


    utils.save_upload(f, dest)


    # If the last chunk has been sent, combine the parts.
    if chunked and (fileattrs['qqtotalparts'] - 1 == fileattrs['qqpartindex']):


        utils.combine_chunks(fileattrs['qqtotalparts'],
            fileattrs['qqtotalfilesize'],
            source_folder=os.path.dirname(dest),
            dest=os.path.join('/home/sweetpea/public_html/media_up/', fileattrs['qquuid'], fileattrs['qqfilename']))


        shutil.rmtree(os.path.dirname(os.path.dirname(dest)))
