#!/usr/bin/env python
# -*- coding: utf-8 -*-
#we are using WEIXIN SUGOU to extract the urls of the articles. But itn eeds us to be logged AND has problems with ip.
# command line syntax: “python wex_scrape.py USAGE NAMEFILE YEARSTART YEAREND QUERY”. 
# USAGE can be "'New Scrape' which creates new data files; 'Use Saved File' which processes existing data files; 
# "Join files"[NOT YET IMPLEMENTED]; "Produce CSV" to use processed files and generate a final CSV. 

import re, urllib2,  os, csv, time, random, collections, pandas as pd, sys, easygui 
from django.utils.encoding import smart_str
from datetime import date
from operator import sub
from easygui.boxes.multi_fillable_box import multenterbox
wechat_file={'title':'','date':'','url':'','images':0, 'images_url':'','file_html':''}
wechat_record=[]
#keys=wechat_file.keys()
keys=['title','date','url','images','images_url','file_html']
from bs4 import BeautifulSoup
code=[]
url_list_final=[]
urlfiletime=['a','b']
query=''
#sys.stdout = open('log'+date.today().strftime('%d-%m-%Y'), 'w+')

def rip_new():
    try:
        year_start=sys.argv[2]
        year_end=sys.argv[3]   
        query=sys.argv[4] 
    except:
        stuff=multenterbox(title='Weixin Scraper New Scrape', msg="Input the token, query, start & end Dates (DD-MM-YYYY)", fields=["Token:","Query:","Start (Blank for 1980)","End (Blank for today)"])
        token=(stuff[0])
        query=(stuff[1])
        year_start=str(stuff[2])
        year_end=str(stuff[3])
    #if (choice2=='Cancel'): break
#if there's not date inserted, take everything        
    if (year_start==''): 
        year_start='01-01-1980'
        print 'setting start date to 1980'
    if (year_end==''): 
        year_end=date.today().strftime("%d-%m-%y")
        print 'setting start date to '+year_end
    urlfiletime[0]=year_start
    urlfiletime[1]=year_end
#REMEMBER O LOGIN TO SOGOU AND CHECK THE TOKEN
    starturl="http://weixin.sogou.com/weixin?type=2&query="+query+"&tsn=5&ft="+year_start+"&et="+year_end+"&interation=null&w=01019900&usip="+query+"&from=tool&sst0="+token+"1490861235659&ie=utf8&dr=1"
    starturl=smart_str(starturl)
    print starturl
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8')]
    startpage_url=opener.open(starturl)
    time.sleep(random.randrange(5))
    startpage_html=startpage_url.read()
    startpage=BeautifulSoup(startpage_html,'html.parser')
    if "用户您好，您的访问过于频繁，为确认本次访问为正常用户行为，需要您协助验证" in startpage_html:
        print "whoops, issues with ip"
        with open ("issueurl.html","wb+") as file:
            file.write(startpage_html)
        file.close()
    results_raw=startpage.find(attrs={'class':'mun'})
    print results_raw
    k=str(results_raw)
    page=1
    print k
    results=int(re.sub("[^0-9]","",k.split("<!")[1]))
    pages=int(round(results/10))
    print "there are "+str(results)+" articles in total corresponding to "+str(pages)
    while (page<=pages+1):
        time.sleep(random.randrange(5))
        code_raw=urllib2.urlopen(starturl+'&page='+str(page))
        code=code_raw.read()
        #print code
        code_text=BeautifulSoup(code,'html.parser')
        #print "on to interpretation"
        urls=code_text.findAll(attrs={"class":"txt-box"})
        #print urls
        for url in urls:
            pezzi=url.find("a")
            #print pezzi
            if pezzi['href']:
                if('mp.weixin' in pezzi['href']) and (pezzi['href'] not in url_list_final):
                    url_list_final.append(pezzi['href'])
                    #print (pezzi['href'])
        page=page+1
        print "page "+str(page)+"/"+str(pages)
    file=open('scrapers_Url'+year_start+"to"+year_end+".dat",'w+') 
    for item in url_list_final:
        file.write(item+"\n")
    print "url list written"
    file.close()
    
def load_rip(): #let's load the saved urls to save scraping quotas
    stack=[]
    try:
        year_start=sys.argv[2]
        year_end=sys.argv[3]
        query=sys.argv[4] 
    except:
        query=str(raw_input("query:"))
        year_start=str(raw_input("date start yyyy-mm-dd:"))
        year_end=str(raw_input("date end yyyy-mm-dd:"))
    urlfiletime[0]=year_start
    urlfiletime[1]=year_end
    file=open('scrapers_Url'+year_start+'to'+year_end+'.dat','rw+')
    stack=file.readlines()
    print stack
    file.close()
    return stack
         
def list_duplicates(seq):
  seen = set()
  seen_add = seen.add
  # adds all elements it doesn't know yet to seen and all other to seen_twice
  seen_twice = set( x for x in seq if x in seen or seen_add(x) )
  # turn the set into a list (as requested)
  return list( seen_twice )       
         
         #Main Loop
 

choice=''
while (choice!='Cancel'):
    choice=''
    try:        
        choice=str(sys.argv[1])
    except:
        choice=easygui.buttonbox(msg='What would you like to do', title='Weixin Scraper (c) 2017 Matteo Tarantino', choices=('New Scrape', 'Use Saved File', "Join files", "Produce CSV", "Cancel" ), image=None) 

    if (choice=='New Scrape'): 
        rip_new()
    if (choice=='Use Saved File'):
        url_list_final=load_rip()
    seen = set()    
    print "duplicates?"
    duplicati=list_duplicates(url_list_final)
    url_list_final=[x for x in url_list_final if x not in duplicati]
    #print url_list_final
    print "total URL:"
    print len(url_list_final)
    k=0
    for i in url_list_final:
        img_count=0
        if (i):
            filename=''
            print k
            wechat_file={'title':'','date':'','url':'','images':0, 'images_url':'','file_html':''}
            try:
                page = urllib2.urlopen(i)
                page_content = page.read()
                soup=BeautifulSoup(page_content,'html.parser')
                title_doc=soup.find(id="activity-name")
                date_doc=soup.find(id="post-date") #get date
            except:
                print 'error'
            try: 
                date_doc=date_doc.string
                title_doc=title_doc.string
                title_doc=title_doc.strip("\r\n ") #remove spaces
            except:
                date_doc='01-01-1980'
                title_doc='ERROR'+str(k) 
        
            print title_doc, date_doc
            filename=date_doc+':'+title_doc #filename isdate + title except if anything went wrong in which case it's error
            print filename
        #except:
            #    print "something has gone wrong in url "+i   
            #    title_doc='UNKNOWN' 
            #    filename='errors'
            wechat_file['title']=title_doc
            wechat_file['date']=date_doc
            wechat_file['url']=i
            wechat_file['images']=img_count
            wechat_file['file_html']=filename+'.html'
            #print wechat_file   
            try:
                #os.mkdir(query)
                #os.chdir(query)
                os.mkdir(filename)
                os.chdir(filename)
                images_url_buffer=[]
                images=soup.findAll("img")
                for image in images: 
                    if 'data-src' in image.attrs: #check if it's the kind of image with a src; if it is, update the list 
                        #print image['data-src']
                        img_count=img_count+1
                        images_url_buffer.append(image['data-src'].strip('//'))
                        #print "iamge data-src="+image['data-src']
                    if 'src' in image.attrs:
                        #print image['data-src']
                        img_count=img_count+1
                        images_url_buffer.append(image['src'])
                        #print "iamge src="+image['src']
                        #print image
                print "total images:"+str(img_count)
                imageduplicates=list_duplicates(images_url_buffer)#find dupes
                images_url_buffer=[x for x in images_url_buffer if x not in imageduplicates] #let's remove any dupes!
                wechat_file['images']=len(images_url_buffer)
                print "total files to download "+str(wechat_file['images'])
                images_url_buffer=tuple(images_url_buffer)
            #try:
                img_dwn_counter=0
                for image in images_url_buffer: #download all images
                    img_dwn_counter=img_dwn_counter+1
                    #image=image.strip('\'"')
                    if image:
                        ftype='.jpeg'
                        if "gif" in image: 
                            ftype =".gif"
                        if "png" in image:
                            ftype =".png"
                        #print image
                        try:
                            rea=urllib2.Request(image)
                            conn=urllib2.urlopen(rea)
                            #print type
                            CHUNK=16*1024 #Read files in Binary and save them block by block
                            image_file_name=str(img_dwn_counter)+ftype   
                            #print image_file_name
                            with open(image_file_name, "wb") as local_file:
                                while True:
                                    chunk=conn.read(CHUNK)
                                    if not chunk:
                                        break
                                    local_file.write(chunk)
                        except:
                            print "problem with getting the file from "+image
                        try:
                            try: 
                                if soup.find("img",attrs={'data-src':image}):
                                    soup.find("img",attrs={'data-src':image})['src']=image_file_name
                                    print "there is data-src"
                            except:
                                print "no data-src"
                            try:
                                if soup.find("img",attrs={'src':image}):
                                    soup.find("img",attrs={'src':image})['src']=image_file_name
                                    print "there is src"
                            except:
                                print "no src either..."
                        except:
                            print "PROBLEM WITH:"+filename
                            print image
                 #   print "something wrong with downloading images?"
                html=soup.prettify('utf-8')
                with open(filename+'.html','wb') as file:
                    file.write(html)
                    #pdfkit.from_url(i,filename+'.pdf')
                os.chdir('..')
            except:
                print "file already exists!"
    
            #print wechat_record
            wechat_record.append(wechat_file)#uodate with all new data abd gten proceed to download hte images
            k=k+1
    df=''       
    #printTable (wechat_record)
    print 'now writing final CSV'
    df = pd.DataFrame(wechat_record)
    df = df.set_index(keys)
    df.to_csv("csv"+urlfiletime[0]+"_"+urlfiletime[1]+".csv",encoding="utf-8")
    break


    
