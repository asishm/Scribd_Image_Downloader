__author__ = 'Asish Mahapatra: asishkm@gmail.com'

import requests
import re
import os
import img2pdf
from multiprocessing import Process, Manager
import sys
from math import ceil
import time

json_pattern = re.compile(r'https.*scribdassets.*jsonp')
img_pattern = re.compile(r'orig.*(http.*scribd.{,45}jpg)')

patterns = {'jpg': re.compile(r'([0-9]*)-.*jpg'),
            'jsonp': re.compile(r'([0-9]*)-.*jsonp')}

DEBUG = False

def sort_json(link):
    '''
        Gets the page number of the image or the jsonp file.
        Urls have the forum 'pagenum-randomhash.jpg / jsonp'
    '''
    for pattern in patterns:
        if pattern in link:
            s = link.index(pattern)-16
            val = re.search(patterns[pattern], link[s:])
            return int(val.groups()[0])

def img_jsonp_urls(scribd_link):
    '''
        Gets a sorted list of URLs based on page number with both
        jsonp or jpg extensions
    '''
    print 'at get_images'

    scribd_conn = requests.get(scribd_link)

    json_list = re.findall(json_pattern, scribd_conn.content)
    img_links = re.findall(img_pattern, scribd_conn.content)
    json_list.extend(img_links)

    json_list = sorted(json_list, key = sort_json)

    return json_list


def write_image(img_file, img_link):
    '''
        Downloads the image from img_link onto the img_file
    '''
    f = open(img_file, 'wb')

    while 1:
        try:
            f.write(requests.get(img_link).content)
        except requests.ConnectionError:
            print 'break at getting img ', img_link, img_file
            continue
        except Exception as e:
            print e, img_file
            continue
        break
    f.close()

def get_img_url(jsonp_link):
    '''
        Gets the image url from a .jsonp link
    '''
    while 1:
        try:
            json_conn = requests.get(jsonp_link)
        except requests.ConnectionError:
            print 'breaking at getting json',
            continue
        break
    resp = json_conn.content

    try:
        img_link = re.findall(img_pattern, resp)[0]
    except IndexError:
        print 'no img link'
        img_link = ''

    return img_link

def convert_to_pdf(img_list, output_folder, pdf_file_name):
    '''
        Converts a list of image files into a pdf at the ouput directory
    '''

    pdf_bytes = img2pdf.convert(img_list, dpi = 100)

    with open(os.path.join(output_folder, pdf_file_name), 'wb') as f:
        f.write(pdf_bytes)

def download_img(urls, start, end, img_dir, pdf_name, shared):
    '''
        Downloads the images from the start index to end index
        of the list of urls (urls) to the img_dir

        Also appends the paths of the images to the shared list
        created my Manager.manager().list()
    '''

    print 'at downloading_img'
    image_list = set()

    print len(urls), 'files'
    print 'images downloaded to {}'.format(img_dir)

    i = start
    end = min(end, len(urls))
    n = str(len(str(len(urls))))

    while i < end:

        img_name = '{}{:0{k}d}.jpg'.format(pdf_name, i+1, k = n)
        img_path = os.path.join(img_dir, img_name)
        image_list.add(img_path)
        if os.path.exists(img_path):
            print img_path, 'exists'
            i += 1
            continue

        if 'jsonp' in urls[i]:
            img_url = get_img_url(urls[i])
        else:
            img_url = urls[i]

        write_image(img_path, img_url)
        i += 1
        if DEBUG:
            print 'Completed img {}'.format(i+1)
    shared.extend(image_list)

if __name__ == '__main__':
    
    processes = []
    
    a = raw_input('''scribd link, pdf file name, \
img_folder, out_folder separated by spaces \n''')
    
    print a.split()
    scribd, pdf, img_folder, out_folder = a.split()

    N = int(raw_input('Enter number of separate processes: '))

    s = time.clock()
    print 'started at', time.ctime()
    
    combined_list = img_jsonp_urls(scribd)
    n = len(combined_list)

    manager = Manager()
    img_files = manager.list()

    k = n/N
    
    for i in range(N):
        start = k*i
        end = k*(i+1)
        if i == N-1:
            end = max(end, n)
        process = Process(target = download_img, args =
                          [combined_list, start, end, img_folder, pdf,
                           img_files])
        
        print 'process {} started'.format(i)
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    print 'image file names secured'

    img_files = sorted(list(img_files))

    print 'converting'

    convert_to_pdf(img_files, out_folder, pdf + '.pdf')
    print 'finished at', time.ctime()
    print 'time taken: {} seconds'.format(time.clock() - s)
