# -*- coding: utf-8 -*-
# Iris 9900HD XBMC Addon

import sys
import httplib

import urllib, urllib2, cookielib, datetime, time, re, os, string
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs, xbmc
import cgi, gzip
from StringIO import StringIO
import json

canal=None

channelListUrl= '/json/channel/list'
#switchChannel= this.sendCmd('channel/switch', { cid: cid }, callback);

UTF8          = 'utf-8'

addon         = xbmcaddon.Addon('plugin.video.iris-9900-hd')
__addonname__ = addon.getAddonInfo('name')
__language__  = addon.getLocalizedString


home          = addon.getAddonInfo('path').decode(UTF8)
icon          = xbmc.translatePath(os.path.join(home, 'icon.png'))
addonfanart   = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))

qp  = urllib.quote_plus
uqp = urllib.unquote_plus

def log(txt):
    message = '%s: %s' % (__addonname__, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)
    
def cleanname(name):    
    return name.replace('&apos;',"'").replace('&#8217;',"'").replace('&amp;','&').replace('&#39;',"'").replace('&quot;','"')

def demunge(munge):
        try:
            munge = urllib.unquote_plus(munge).decode(UTF8)
        except:
            pass
        return munge


USER_AGENT    = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36'
defaultHeaders = {'User-Agent':USER_AGENT, 
                 'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
                 'Accept-Encoding':'gzip,deflate,sdch',
                 'Cookie': 'qlqhzyhjljcfffyy=21636d1e642c874112d9674ac8e8b002',
                 'Accept-Language':'en-US,en;q=0.8'} 

def getRequest(url, user_data=None, headers = defaultHeaders , alert=True):

              log("getRequest URL:"+str(url))
              opener = urllib2.build_opener()
              urllib2.install_opener(opener)

              log("getRequest URL:"+str(url))
              req = urllib2.Request(url.encode(UTF8), user_data, headers)

              try:
                 response = urllib2.urlopen(req)
                 if response.info().getheader('Content-Encoding') == 'gzip':
                    log("Content Encoding == gzip")
                    buf = StringIO( response.read())
                    f = gzip.GzipFile(fileobj=buf)
                    link1 = f.read()
                 else:
                    link1=response.read()

              except urllib2.URLError, e:
                 if alert:
                     xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( __addonname__, e , 10000) )
                 link1 = ""

              if not (str(url).endswith('.zip')):
                 link1 = str(link1).replace('\n','')
              return(link1)


def as_complex(lista):
    return complex(dct['current'], dct['chnlist_head'], dct['main'], dct['subs'], dct['chnlist'])


def ListaCanales(fanart):
              ilist = []
              azheaders = defaultHeaders
              azheaders['X-Requested-With'] = 'XMLHttpRequest'
              url='http://' + addon.getSetting('ip_deco') + channelListUrl
              log('Ruta para obtener canales: ' + url)              
              pg = getRequest(url, None, azheaders)
              lista=json.loads(pg)
              lista2=lista['chnlist']
              #print(lista2)
              for item in lista2:
                    try:
                         #log('Nombre: ' + item['name'])
                         #log('ID: ' + str(item['id']))
                         name = cleanname(item['name']).encode(UTF8)
                         id = cleanname(str(item['id'])).encode(UTF8)
                         #log(name)
                         #log(id)
                         mode = 'VC'
                         pathe='http://' + addon.getSetting('ip_deco') + '/live.ts'
                         u = '%s?url=%s&name=%s&mode=%s&id=%s' % (sys.argv[0],qp(url), qp(name), mode, qp(id))
                         print u
                         liz=xbmcgui.ListItem(name, '','DefaultVideo.png', icon,path=pathe)
                         liz.setProperty( "Folder", "false" )
                         liz.setProperty("IsPlayable", "true")
                         liz.setInfo( 'Video', { "Title": name, })
                         ilist.append((u, liz, True))
                    except:
                      pass
              xbmcplugin.addDirectoryItems(int(sys.argv[1]), ilist, len(ilist))

def VerCanal(cid):
        log("++++++++++++++++++++++++++++++++++ VOY A CAMBIAR DE CANAL +++++++++++++++++++++++++++++++++")
	azheaders = defaultHeaders
	azheaders['X-Requested-With'] = 'XMLHttpRequest'
	url='http://' + addon.getSetting('ip_deco') + '/api/channel/switch'
        url2='http://' + addon.getSetting('ip_deco') + channelListUrl
        url3='http://' + addon.getSetting('ip_deco') + '/json/epg/nownext?cid=' + str(cid)
        print "++++++++++++++ " + url3 
	values = {'cid': qp(cid)}
	data = urllib.urlencode(values)            
        current_id=''
        while str(cid) != str(current_id):
            pg2 = getRequest(url, data, azheaders)
            xbmc.sleep(2000)           
            pg = getRequest(url2, None, azheaders)
            lista=json.loads(pg)
            lista2=lista['current']
            current_id=lista2['channel_id']
	pg3=getRequest(url3, None, azheaders)
        epgJson=json.loads(pg3)
        epg=epgJson['epg_nownext']
        now=epg['now']
        titulo=now['name']
	url = 'http://' + addon.getSetting('ip_deco') + '/live.ts'
        item=xbmcgui.ListItem(path=url.encode(UTF8, 'ignore'), iconImage="DefaultVideo.png", thumbnailImage=icon)
        item.setProperty("IsPlayable", "true")
        item.setProperty( "Folder", "false" )
        item.setInfo( 'Video', { "Title": titulo, })
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item)
        xbmc.Player().play(item=url, listitem=item)
        return


# PROCEDIMIENTO PRINCIPAL
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

parms = {}
try:
    parms = dict( arg.split( "=" ) for arg in ((sys.argv[2][1:]).split( "&" )) )
    for key in parms:
       parms[key] = demunge(parms[key])
except:
    parms = {}

p = parms.get

mode = p('mode',None)

if mode==  None:  ListaCanales(p('fanart'))
elif mode=='VC':  VerCanal(p('id'))

xbmcplugin.endOfDirectory(int(sys.argv[1]))
