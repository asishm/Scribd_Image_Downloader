__author__ = 'Asish Mahapatra: asishkm@gmail.com'

import requests
import re
import os
import img2pdf

# to do
# 1. handle no response aka timeouts
# 2. naive check if all files are downloaded

# assumes img folder is empty and has no subdirectories
# works only when the scribd document is composed solely of images (.jpg)

scribd_link = None

img_folder = './images'

pdf_file_name = '*.pdf'

DEBUG = True

output_folder = ''

json_pattern = re.compile(r'https.*scribdassets.*jsonp')
img_pattern = re.compile(r'orig.*(http.*scribd.{,45}jpg)')

def sort_json(link):
    if 'jpg' in link:
        pat = re.compile(r'([0-9]*)-.*jpg')
        s = link.index('jpg')-16
        val = re.search(pat, link[s:])
        return int(val.groups()[0])
    elif 'jsonp' in link:
        pat = re.compile(r'([0-9]*)-.*jsonp')
        s = link.index('jsonp')-16
        val = re.search(pat, link[s:])
        return int(val.groups()[0])

def write_image(img_file, img_link):
    f = open(img_file, 'wb')

    while 1:
        try:
            f.write(requests.get(img_link).content)
        except requests.ConnectionError:
            print 'break at getting img ', img_link
            continue
        break
    f.close()
    

def get_images(scribd_link, output_folder):
    global json_list, img_links

    scribd_conn = requests.get(scribd_link)

    json_list = re.findall(json_pattern, scribd_conn.content)
    img_links = re.findall(img_pattern, scribd_conn.content)
    json_list.extend(img_links)

    json_list = sorted(json_list, key = sort_json)

    n = str(len(str(len(json_list))))

    print len(json_list), 'files'
    print 'images downloaded to {}'.format(output_folder)

    for i, link in enumerate(json_list):

        img_name = '{:0{k}d}.jpg'.format(i+1, k = n)
        img_file = os.path.join(output_folder, img_name)
        if os.path.exists(img_file):
            print img_file, 'exists'
            continue

        if 'jpg' in link:
            write_image(img_file, link)
            print 'jpg there'
            continue
                     
        print 'Downloading img {}'.format(i+1)
        while 1:
            try:
                json_conn = requests.get(link)
            except requests.ConnectionError:
                print 'break at getting json',
                continue
            break
        resp = json_conn.content
        try:
            img_link = re.findall(img_pattern, resp)[0]
        except IndexError:
            print 'no img link'
            continue

        if DEBUG:
            print img_link
        
        write_image(img_file, img_link)

        
        print 'Completed img {} \n'.format(i+1)


def convert_to_pdf(img_folder, output_folder, scribd_link, pdf_file_name):

    file_names = os.walk(img_folder).next()[2]
    files = [os.path.join(img_folder, name) for name in file_names]

    pdf_bytes = img2pdf.convert(files, dpi = 100)

    with open(os.path.join(output_folder, pdf_file_name), 'wb') as f:
        f.write(pdf_bytes)

def get_pdf(scribd_link = scribd_link, pdf_file_name = pdf_file_name,
            img_folder = img_folder, output_folder = output_folder):
    
    get_images(scribd_link, img_folder)
    convert_to_pdf(img_folder, output_folder, scribd_link, pdf_file_name)
