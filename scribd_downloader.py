__author__ = 'Asish Mahapatra: asishkm@gmail.com'

import requests
import re
import os
import img2pdf
from multiprocessing import Process, Manager
import sys


# works only when the scribd document is composed solely of images (.jpg)

img_folder = './images'

DEBUG = True

output_folder = ''

json_pattern = re.compile(r'https.*scribdassets.*jsonp')
img_pattern = re.compile(r'orig.*(http.*scribd.{,45}jpg)')

def sort_json(link):
    if 'jpg' in link:
        pat = re.compile(r'([0-9]*)-.*jpg')
        s = link.index('jpg')-16
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
    

def get_images(scribd_link):

    print 'at get_images'

    scribd_conn = requests.get(scribd_link)

    json_list = re.findall(json_pattern, scribd_conn.content)
    img_links = re.findall(img_pattern, scribd_conn.content)
    json_list.extend(img_links)

    json_list = sorted(json_list, key = sort_json)

    #n = str(len(str(len(json_list))))

    return json_list

def get_img_links(json_list):

    print 'at get_img_links'
    img_links = []
    
    for i, link in enumerate(json_list):
        if i%50 ==0:
            print i
        if 'jpg' in link:
            img_links.append(link)
        elif 'jsonp' in link:
            while 1:
                try:
                    json_conn = requests.get(link)
                except requests.ConnectionError:
                    print 'breaking at getting json',
                    continue
                break
            resp = json_conn.content

            try:
                img_link = re.findall(img_pattern, resp)[0]
            except IndexError:
                print 'no img link'
                continue

            img_links.append(img_link)

    #n = str(len(str(len(img_links))))
    return img_links

def download_img(img_links, start_index, end_index, img_folder, pdf_file_name, f):
    
    print 'at downloading_img'
    image_list = set()

    print len(img_links), 'files'
    print 'images downloaded to {}'.format(img_folder)

    i = start_index
    end_index = min(end_index, len(img_links))
    n = str(len((str(len(img_links)))))
    while i < end_index:

        img_name = '{}{:0{k}d}.jpg'.format(pdf_file_name,i+1, k = n)
        img_file = os.path.join(img_folder, img_name)
        image_list.add(img_file)
        if os.path.exists(img_file):
            print img_file, 'exists'
            continue
        
        write_image(img_file, img_links[i])
        i += 1
        
        print 'Completed img {} \n'.format(i+1)
    f.extend(image_list)


def convert_to_pdf(img_list, output_folder, pdf_file_name):

    pdf_bytes = img2pdf.convert(img_list, dpi = 100)

    with open(os.path.join(output_folder, pdf_file_name), 'wb') as f:
        f.write(pdf_bytes)

if __name__ == "__main__":
    global f, image_list
    processes = []
    a = raw_input('''scribd link, pdf file name, \
img_folder, out_folder separated by spaces \n''')
    print a.split()
    scribd, pdf, img_folder, out_folder = a.split()

    img_links = get_img_links(get_images(scribd))
    n = len(img_links)
    print 'image links scraped', n
    manager = Manager()
    f = manager.list()
    
    for i in range(5):
        process = Process(target = download_img, args =
                          [img_links, i*n/4, (i+1)*n/4, img_folder, pdf, f])
        print 'process {} started'.format(i)
        process.start()
        processes.append(process)

    for process in processes:
        process.join()
    print 'image list secured'
    image_list = sorted(list(f))

    print 'converting'
    convert_to_pdf(image_list, out_folder, pdf+'.pdf')
