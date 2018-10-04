import json
import requests
import os
import shutil

from grape.auc_functions import *
from grape.upload import UploadFileForm
from grape import utils

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django import forms

owner_name = "Hellim"
result = []
API_URL="https://us.api.battle.net/wow/auction/data/sargeras?locale=en_US&apikey=by8ve5ez6s5vn3d7mg4ynxdbxbswyrdw"

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
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        userdata = request.POST.getlist("userdata[]")
        temp = get_user_data(userdata[0], userdata[1])
        out = json.dumps(temp, indent = 1)
        f = open("user_debug_log.txt", "w")
        f.write(out)
        f.close()
        return HttpResponse(out)
        
@csrf_exempt
def get_user_cookie(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        userdata = request.POST.getlist("userdata[]")
        temp = get_user_data_cookie(userdata[0], userdata[1])
        out = json.dumps(temp, indent = 1)
        f = open("user_debug_log.txt", "w")
        f.write(out)
        f.close()
        return HttpResponse(out)
        
@csrf_exempt
def test(request):
    if request.method == 'GET':
        return render(request, 'grape/index.html', {})
    else:
        temp = request.POST
        out = json.dumps(temp, indent = 1)
        return HttpResponse(out)
    
@csrf_exempt    
def add_user(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        userdata = request.POST.getlist("userdata[]")
        f = open("user_debug_log.txt", "w")
        f.write(json.dumps(userdata, indent = 1))
        f.close()
        username = userdata.pop(0)
        pwd = userdata.pop(0)
        region = []
        while len(region) < 3:
            region.append(userdata.pop(0))
        temp = add_user_entry(username, pwd, region, userdata)
        out = json.dumps(temp, indent = 1)
        return HttpResponse(out)
        
        
@csrf_exempt    
def update_user(request):
    if request.method == 'GET':
        return render(request, 'grape/test.html', {})
    else:
        
        '''f = open("user_debug_log.txt", "w")
        f.write(str(request.body))
        f.write("\n")
        f.close()'''
        f = open("user_debug_log.txt", "a")
        f.write(str(request.POST))
        f.close()
        userdata = request.POST.getlist("userdata[]")
        username = userdata.pop(0)
        pwd = userdata.pop(0)
        region = []
        while len(region) < 3:
            region.append(userdata.pop(0))
        temp = update_user_entry(username, pwd, region, userdata)
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
        
