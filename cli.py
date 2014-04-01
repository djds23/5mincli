import re
import os
import sys
import json
import urllib
import urllib2


def single_or_playlist(aolonid):
    '''find if we are single video or playlist id'''
    if len(aolonid)==6:
        url = 'http://api.5min.com/video/list/info.json?Video_Group_Id='+aolonid+'&num_of_videos=200'
        return pull_url(url)
    elif len(aolonid)==9:
        url = 'http://api.5min.com/video/'+aolonid+'/info.json?sid=577'
        return pull_url(url, single=True)
    else:
        return 'There is an issue with your id.'

def pull_url(url, single=False):
    '''request file and extract JSON'''
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        full_page = response.read()
        if single:
            return sort_json(full_page, single=True)
        else:
            return sort_json(full_page)
    except urllib2.URLError, e:
        return 'There was an error pulling the video: '+ e

def sort_json(full_page, single=False):
    '''take out the json and sort it, or end program with bad id'''
    json_obj = json.loads(full_page)
    try:
        exception = json_obj['api']['exception'] 
        if exception:
            print 'There was an exception:', exception 
            return exception
    except KeyError:
        items = json_obj['items']
        if single:
            return extract_elements(items, single=True)
        else:
            return extract_elements(items)
    
def extract_elements(items, key=0, title='title', description='description',
        api_id='id',studioName='studioName', player='player',single=False):
    '''pull out the elements we want'''
    if single:
        base =items[key]
        return write_single([base[title], base[description], base[studioName], base[player]['url'],base[player]['source'],base[api_id]], base['videoUrl'])
    else:
        bases = [items[i] for i, elements in enumerate(items)]
        return write_playlist([[base[title], base[description], base[studioName],base[api_id],base['videoUrl'], base[player]['url'],base[player]['source']]for base in bases])
        

def write_single(elements, url):
    '''write a log of requested elements for single videos'''
    with open('report.txt', 'w') as f:
        print 'Writing entry to report.txt..'
        for entry in elements:
            print 'Writing... ', entry
            if isinstance(entry, int):
                f.write(str(entry))
            elif isinstance(entry, unicode):
                f.write(entry.encode('ascii','ignore'))
            f.write('\n')
        download(url, str(elements[-1]))
        f.write('\n\nwritten by 5mincli')
        f.close()

def write_playlist(elements):
    '''write a log for each video in a playlist'''
    with open('list_report.txt', 'w') as f:
        for entry in elements:
            for contents in entry:
                print 'Writing... ', contents
                if isinstance(content, int):
                    f.write(str(content))
                elif isinstance(content, unicode):
                    f.write(content.encode('ascii','ignore'))
            f.write('\n')
            download(str(entry[4]),str(entry[3]))
        f.write('\n\nwritten by 5mincli')

def download(url, aolonid):
    '''download files and cleanup failures'''
    file_name = aolonid + '.mp4'
    try:
        print 'Attempting '+ aolonid
        urllib.urlretrieve(url, file_name)
        urllib.urlcleanup()
        print 'Cleaning up '+ aolonid
    except urllib.ContentTooShortError, e:
        return 'There was an exception with urlretrieve:', e

def cli():
    print 'the Cli for AolOn'
    print 'Input "exit" to exit the program.'
    print 'Paste your AolOn Id/playlist id below:'
    from_user = str(raw_input())
    if from_user.lower() == 'exit':
        sys.exit()
    single_or_playlist(from_user)

if __name__=='__main__':
    while True:
        cli()

