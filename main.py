from resources.lib.globals import *


def categories():      
    addDir('Today\'s Games',100,ICON,FANART)
    addDir('Yesterday\'s Games',105,ICON,FANART)
    #addDir('Favorite Team Recent Games','favteam',500,ICON,FANART)
    addDir('Goto Date',200,ICON,FANART)  
        

def todaysGames(game_day):    
    if game_day == None:
        game_day = localToEastern()

    print "GAME DAY = " + str(game_day)            
    settings.setSetting(id='stream_date', value=game_day)    

    display_day = stringToDate(game_day, "%Y-%m-%d")
    url_game_day = display_day.strftime('year_%Y/month_%m/day_%d')            
    prev_day = display_day - timedelta(days=1)                

    addDir('[B]<< Previous Day[/B]',101,PREV_ICON,FANART,prev_day.strftime("%Y-%m-%d"))

    date_display = '[B][I]'+ colorString(display_day.strftime("%A, %m/%d/%Y"),GAMETIME_COLOR)+'[/I][/B]'

    addPlaylist(date_display,str(game_day),900,ICON,FANART)
    
    #addPlaylist(date_display,display_day,'/playhighlights',999,ICON,FANART)

    url = 'http://gdx.mlb.com/components/game/mlb/'+url_game_day+'/grid_ce.json'    
    print "URL GAME DAY"
    print url

    req = urllib2.Request(url)    
    req.add_header('Connection', 'close')
    req.add_header('User-Agent', UA_PS4)

    try:    
        response = urllib2.urlopen(req)            
        json_source = json.load(response)                           
        response.close()                
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code          
        sys.exit()

       
    global RECAP_PLAYLIST
    global EXTENDED_PLAYLIST
    RECAP_PLAYLIST.clear()
    EXTENDED_PLAYLIST.clear()

    try:
        for game in json_source['data']['games']['game']:        
            createGameListItem(game, game_day)
    except:
        pass
    

    next_day = display_day + timedelta(days=1)
    addDir('[B]Next Day >>[/B]',101,NEXT_ICON,FANART,next_day.strftime("%Y-%m-%d"))    


def createGameListItem(game, game_day):
    icon = getGameIcon(game['home_team_id'],game['away_team_id'])
    #http://mlb.mlb.com/mlb/images/devices/ballpark/1920x1080/2681.jpg
    #B&W
    #fanart = 'http://mlb.mlb.com/mlb/images/devices/ballpark/1920x1080/'+game['venue_id']+'.jpg'   
    #Color
    fanart = 'http://www.mlb.com/mlb/images/devices/ballpark/1920x1080/color/'+game['venue_id']+'.jpg'
    
    if TEAM_NAMES == "0":
        away_team = game['away_team_name']
        home_team = game['home_team_name']  
    else:
        away_team = game['away_name_abbrev']
        home_team = game['home_name_abbrev']  


    fav_game = False
    
    if game['away_team_name'].encode('utf-8') in FAV_TEAM :
        fav_game = True
        away_team = colorString(away_team,getFavTeamColor())           
    
    if game['home_team_name'].encode('utf-8') in FAV_TEAM:
        fav_game = True
        home_team = colorString(home_team,getFavTeamColor())
    

    game_time = ''
    if game['status'] == 'Preview':
        game_time = game_day+' '+game['event_time']
        print game_time
        game_time = stringToDate(game_time, "%Y-%m-%d %I:%M %p")        
        game_time = easternToLocal(game_time)
       
        if TIME_FORMAT == '0':
             game_time = game_time.strftime('%I:%M %p').lstrip('0')
        else:
             game_time = game_time.strftime('%H:%M')

        game_time = colorString(game_time,UPCOMING)            

    else:
        game_time = game['status']

        if game_time == 'Final':                  
            game_time = colorString(game_time,FINAL)
            
        elif 'In Progress' in game_time:           
            if game['top_inning'] == 'Y':
                #up triangle
                #top_bottom = u"\u25B2"               
                top_bottom = "T"
            else:
                #down triangle
                #top_bottom = u"\u25BC"
                top_bottom = "B"                

            inning = game['inning']
            if int(inning) % 10 == 1 and int(inning) != 11:
                ordinal_indicator = "st"
            elif int(inning) % 10 == 2 and int(inning) != 12:
                ordinal_indicator = "nd"
            elif int(inning) % 10 == 3 and int(inning) != 13:
                ordinal_indicator = "rd"
            else:
                ordinal_indicator = "th"

            game_time = top_bottom + ' ' + inning + ordinal_indicator
            
            if int(inning) >= 9:
                color = CRITICAL
            else:
                color = LIVE

            game_time = colorString(game_time,color)
        
        else:            
            game_time = colorString(game_time,LIVE)
        
        
    event_id = str(game['calendar_event_id'])

    #live_video = game['gameLiveVideo']    
    print away_team + ' ' + home_team
    '''
    epg = None
    try:
        epg = json.dumps(game['game_media']['homebase']['media'])
    except:
        pass
    '''
    gid = game['id']

    live_feeds = 0
    archive_feeds = 0
    #teams_stream = game['away_name_abbrev'] + game['home_name_abbrev']
    teams_stream = game['away_code'] + game['home_code']
    stream_date = str(game_day)

    
    desc = ''       
    hide_spoilers = 0
    if NO_SPOILERS == '1' or (NO_SPOILERS == '2' and fav_game) or (NO_SPOILERS == '3' and game_day == localToEastern()) or (NO_SPOILERS == '4' and game_day < localToEastern()) or game['status'] == 'Preview':
        name = game_time + ' ' + away_team + ' at ' + home_team    
        hide_spoilers = 1
    else:    
        name = game_time + ' ' + away_team + ' ' + colorString(str(game['away_score']),SCORE_COLOR) + ' at ' + home_team + ' ' + colorString(str(game['home_score']),SCORE_COLOR)             

   
    name = name.encode('utf-8')
    if fav_game:
        name = '[B]'+name+'[/B]'
    
    title = away_team + ' at ' + home_team
    title = title.encode('utf-8')

    #Label free game of the day if applicable
    #if bool(game['content']['media']['epg'][0]['items'][0]['freeGame']) and game_day >= localToEastern():
    #name = name + colorString(" Free", FREE)
    
    #Set audio/video info based on stream quality setting
    audio_info, video_info = getAudioVideoInfo()
    #'duration':length
    info = {'plot':desc,'tvshowtitle':'MLB','title':title,'originaltitle':title,'aired':game_day,'genre':'Sports'}

    #Create Playlist for the days recaps and condensed
    '''
    try:         
        recap_url, condensed_url = getHighlightLinks(teams_stream, stream_date)
        global RECAP_PLAYLIST            
        listitem = xbmcgui.ListItem(title, thumbnailImage=icon)    
        listitem.setInfo( type="Video", infoLabels={ "Title": title })
        RECAP_PLAYLIST.add(recap_url, listitem)

        global EXTENDED_PLAYLIST    
        listitem = xbmcgui.ListItem(title, thumbnailImage=icon)      
        listitem.setInfo( type="Video", infoLabels={ "Title": title } )
        EXTENDED_PLAYLIST.add(condensed_url, listitem)
    except:
        pass
    '''
    addStream(name,title,event_id,gid,icon,fanart,info,video_info,audio_info,teams_stream,stream_date)



def streamSelect(event_id, gid, teams_stream, stream_date):    
    display_day = stringToDate(stream_date, "%Y-%m-%d")
    url_game_day = display_day.strftime('year_%Y/month_%m/day_%d')
    url = 'http://gdx.mlb.com/components/game/mlb/'+url_game_day+'/grid_ce.json'    
    
    req = urllib2.Request(url)    
    req.add_header('Connection', 'close')
    req.add_header('User-Agent', UA_PS4)

    try:    
        response = urllib2.urlopen(req)            
        json_source = json.load(response)                           
        response.close()                
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code          
        sys.exit()

    #Find selected game
    for game in json_source['data']['games']['game']:
        if gid == game['id']:
            try:
                epg = game['game_media']['homebase']['media']
                break
            except:
                #no stream info, abort! abort!
                msg = "No playable streams found."
                dialog = xbmcgui.Dialog() 
                ok = dialog.ok('Streams Not Found', msg)        
                sys.exit()
       

    stream_title = []    
    content_id = []
    free_game = []
    media_state = []
    playback_scenario = []    
    #archive_type = ['Highlights','Recap','Condensed','Full Game']    
    archive_type = ['Recap','Condensed','Full Game']
        
    for item in epg:                
        #if str(item['playback_scenario']) == "HTTP_CLOUD_TABLET_60":
        if str(item['playback_scenario']) == "HTTP_CLOUD_WIRED_60":                        
            #if str(item['playback_scenario']) == "HTTP_CLOUD_WIRED":
            stream_title.append(str(item['type'])[-4:].title() + " ("+item['display']+")")
            media_state.append(item['state'])             
            content_id.append(item['id'])  
            playback_scenario.append(str(item['playback_scenario']))       

        elif str(item['playback_scenario']) == "HTTP_CLOUD_AUDIO" and item['state'] != 'MEDIA_OFF':
            title = str(item['type']).title()
            title = title.replace('_', ' ')
            stream_title.append(title + " ("+item['display']+")")
            media_state.append(item['state'])             
            content_id.append(item['id'])  
            playback_scenario.append(str(item['playback_scenario']))          
        '''
        elif str(item['playback_scenario']) == "FLASH_2500K_1280X720" and item['type'] != 'condensed_game':
            title = str(item['type']).title()
            title = title.replace('_', ' ')
            stream_title.append(title + " ("+item['display']+")")
            media_state.append(item['state'])             
            content_id.append(item['id'])  
            playback_scenario.append("HTTP_CLOUD_WIRED_60") 
        '''
    #All past games should have highlights
    if len(stream_title) == 0 and stream_date > localToEastern():
        msg = "No playable streams found."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Streams Not Found', msg)        
        sys.exit()

    #Reverse Order for display purposes
    #stream_title.reverse()
    #ft.reverse()
    print "MEDIA STATE"
    print media_state

    stream_url = ''
    media_auth = ''
    
    play_highlights = 0
    if len(media_state) > 0:
        if media_state[0] == 'MEDIA_ARCHIVE':        
            dialog = xbmcgui.Dialog()         
            a = dialog.select('Choose Archive', archive_type)    
            '''            
            if a == 0:
                #Highlighs                
                #try:            
                #stream_url = getHighlightLinks(teams_stream, stream_date)                
                recap_url, condensed_url = getHighlightLinks(teams_stream, stream_date)                
                play_highlights = 1
                #except:
                #pass         
            elif
            '''
            if a < 2:
                recap, condensed = getHighlightLinks(teams_stream, stream_date)                
                if a == 0:
                    stream_url = recap['url']
                else:            
                    stream_url = condensed['url']

                if QUALITY == 'Always Ask':       
                    bandwidth = getStreamQuality(str(recap['url']))
                else:
                    bandwidth = find(QUALITY,'(',' kbps)')
                
                createHighlightStream(stream_url, bandwidth)
            elif a == 2:        
                dialog = xbmcgui.Dialog() 
                n = dialog.select('Choose Stream', stream_title)
                if n > -1:                            
                    stream_url, media_auth = fetchStream(content_id[n],event_id,playback_scenario[n])            
                    stream_url = createFullGameStream(stream_url,media_auth,media_state[n])                  
        else:
            dialog = xbmcgui.Dialog() 
            n = dialog.select('Choose Stream', stream_title)
            if n > -1:                        
                stream_url, media_auth = fetchStream(content_id[n],event_id,playback_scenario[n])            
                stream_url = createFullGameStream(stream_url,media_auth,media_state[n])           
    else:
        archive_type = ['Highlights']
        dialog = xbmcgui.Dialog()         
        a = dialog.select('Choose Archive', archive_type)                
        if a == 0:
            getHighlightLinks(teams_stream, stream_date)                
            play_highlights = 1
                                
    
    print "STREAM BEFORE PLAY"
    print stream_url    
    listitem = xbmcgui.ListItem(path=stream_url)        

    if stream_url != '':            
        #listitem.setMimeType("application/x-mpegURL")        
        xbmcplugin.setResolvedUrl(handle=addon_handle, succeeded=True, listitem=listitem)
        
    elif play_highlights == 1:             
        #-----------------------------------------------------------
        #Hack to get around resolved url wanting a single list item
        #-----------------------------------------------------------
        #Satisify the resolved url call
        listitem = xbmcgui.ListItem()    
        xbmcplugin.setResolvedUrl(handle=addon_handle, succeeded=False, listitem=listitem)
        xbmc.sleep(5)
        #Close the error dialog
        xbmc.executebuiltin('Dialog.Close(all,true)')
        xbmc.sleep(500)
        #-------------------------------------------------- 
        #Play highlights        
        xbmc.Player().play(HIGHLIGHT_PLAYLIST)         
               
    else:        
        #xbmcplugin.setResolvedUrl(addon_handle, False, listitem)
        xbmc.executebuiltin('Dialog.Close(all,true)')



def playAllHighlights():
    stream_title = ['Recap','Condensed'] 
    dialog = xbmcgui.Dialog() 
    n = dialog.select('View All', stream_title)
    
    if n == 0:
        xbmc.Player().play(RECAP_PLAYLIST)
    elif n == 1:
        xbmc.Player().play(EXTENDED_PLAYLIST)


def getGamesForDate(stream_date):
    stream_date_new = stringToDate(stream_date, "%Y-%m-%d")                
    year = stream_date_new.strftime("%Y")
    month = stream_date_new.strftime("%m")
    day = stream_date_new.strftime("%d")
    
    url = 'http://gdx.mlb.com/components/game/mlb/year_'+year+'/month_'+month+'/day_'+day+'/'
    print url

    req = urllib2.Request(url)    
    req.add_header('Connection', 'close')
    req.add_header('User-Agent', UA_IPAD)

    try:    
        response = urllib2.urlopen(req)            
        html_data = response.read()                                 
        response.close()                
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code          
        sys.exit()
    
    #<li><a href="gid_2016_03_13_arimlb_chamlb_1/"> gid_2016_03_13_arimlb_chamlb_1/</a></li>
    match = re.compile('<li><a href="gid_(.+?)/">(.+?)</a></li>',re.DOTALL).findall(html_data)   
    global RECAP_PLAYLIST
    global EXTENDED_PLAYLIST
    RECAP_PLAYLIST.clear()
    EXTENDED_PLAYLIST.clear()
    
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('MLB Highlights', 'Retrieving Streams ...')
    perc_increments = 100/len(match) 
    first_time_thru = True
    bandwidth = find(QUALITY,'(',' kbps)')

    for gid, junk in match:        
        pDialog.update(perc_increments, message='Downloading '+gid)        
        try:
            recap, condensed = getHighlightLinks(None, stream_date, gid)   
           
            if first_time_thru and QUALITY == 'Always Ask':                
                bandwidth = getStreamQuality(str(recap['url']))
                first_time_thru = False
            
                       
            listitem = xbmcgui.ListItem(recap['title'], thumbnailImage=recap['icon'])    
            listitem.setInfo( type="Video", infoLabels={ "Title": recap['title'] })
            RECAP_PLAYLIST.add(createHighlightStream(recap['url'],bandwidth), listitem)
            
            listitem = xbmcgui.ListItem(condensed['title'], thumbnailImage=condensed['icon'])      
            listitem.setInfo( type="Video", infoLabels={ "Title": condensed['title'] } )
            EXTENDED_PLAYLIST.add(createHighlightStream(condensed['url'],bandwidth), listitem)
        except:
            pass

        perc_increments += perc_increments
        

    pDialog.close()


def createHighlightStream(url, bandwidth):
    if bandwidth != '' and int(bandwidth) < 4500:
            url = url.replace('master_tablet_60.m3u8', 'asset_'+bandwidth+'K.m3u8')

    url = url + '|User-Agent='+UA_IPAD

    return url


def getHighlightLinks(teams_stream, stream_date, gid=None, bandwidth=None):
    #global HIGHLIGHT_PLAYLIST
    #HIGHLIGHT_PLAYLIST.clear()  
    print stream_date
    stream_date = stringToDate(stream_date, "%Y-%m-%d")                
    year = stream_date.strftime("%Y")
    month = stream_date.strftime("%m")
    day = stream_date.strftime("%d")    

    if gid == None:
        away = teams_stream[:3].lower()
        home = teams_stream[3:].lower()
        url = 'http://gdx.mlb.com/components/game/mlb/year_'+year+'/month_'+month+'/day_'+day+'/gid_'+year+'_'+month+'_'+day+'_'+away+'mlb_'+home+'mlb_1/media/mobile.xml'
    else:
        url = 'http://gdx.mlb.com/components/game/mlb/year_'+year+'/month_'+month+'/day_'+day+'/gid_'+gid+'/media/mobile.xml'
    print url

    req = urllib2.Request(url)    
    req.add_header('Connection', 'close')
    req.add_header('User-Agent', UA_IPAD)
    try:    
        response = urllib2.urlopen(req)            
        xml_data = response.read()                                 
        response.close()                
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code          
        sys.exit()
    
    match = re.compile('<media id="(.+?)"(.+?)<headline>(.+?)</headline>(.+?)<thumb type="22">(.+?)</thumb>(.+?)<url playback-scenario="HTTP_CLOUD_TABLET_60">(.+?)</url>',re.DOTALL).findall(xml_data)       
    bandwidth = find(QUALITY,'(',' kbps)') 
    
    recap = {}
    condensed = {}
    for media_id, media_tag, headline, junk1, icon, junk2, clip_url in match:                
        '''
        print clip_url
        if 'media-type="T"' in media_tag:
            if bandwidth != '' and int(bandwidth) < 4500:
                clip_url = clip_url.replace('master_tablet_60.m3u8', 'asset_'+bandwidth+'K.m3u8')
            
            clip_url = clip_url + '|User-Agent='+UA_IPAD
            print clip_url
            icon = 'http://mediadownloads.mlb.com/mlbam/'+year+'/'+month+'/'+day+'/images/mlbf_'+media_id+'_th_43.jpg'
            listitem = xbmcgui.ListItem(headline, thumbnailImage=icon)    
            listitem.setInfo( type="Video", infoLabels={ "Title": headline })
            #RECAP_PLAYLIST.add(temp_recap_stream_url, listitem)
            #HIGHLIGHT_PLAYLIST.add(clip_url, listitem)
        '''        

        if 'media-type="R"' in media_tag:           
            #icon = 'http://mediadownloads.mlb.com/mlbam/'+year+'/'+month+'/'+day+'/images/mlbf_'+media_id+'_th_43.jpg'  
            title = headline
            recap = {'url':clip_url, 'icon':icon, 'title':headline}
        elif 'media-type="C"' in media_tag:
            #icon = 'http://mediadownloads.mlb.com/mlbam/'+year+'/'+month+'/'+day+'/images/mlbf_'+media_id+'_th_43.jpg'            
            title = headline
            condensed = {'url':clip_url, 'icon':icon, 'title':headline}

    return recap, condensed



def createFullGameStream(stream_url, media_auth, media_state):
    #SD (800 kbps)|SD (1600 kbps)|HD (3000 kbps)|HD (5000 kbps)        
    bandwidth = ''
    bandwidth = find(QUALITY,'(',' kbps)')

    if QUALITY == 'Always Ask':
        bandwidth = getStreamQuality(stream_url)

    #Only set bandwidth if it's explicitly set
    if bandwidth != '':
        if media_state == 'MEDIA_ARCHIVE':                
            #ARCHIVE
            #http://mlblive-akc.mlb.com/ls04/mlbam/2016/03/02/MLB_GAME_VIDEO_DETNYA_HOME_20160302/master_wired.m3u8 
            #http://mlblive-akc.mlb.com/ls04/mlbam/2016/03/02/MLB_GAME_VIDEO_DETNYA_HOME_20160302/1800K/1800_complete-trimmed.m3u8
            stream_url = stream_url.replace(MASTER_FILE_TYPE, bandwidth+'K/'+bandwidth+'_complete-trimmed.m3u8') 

        elif media_state == 'MEDIA_ON':
            #LIVE    
            #5000K/5000_slide.m3u8 OR #3500K/3500_complete.m3u8
            # Slide = Live, Complete = Watch from beginning?
            stream_url = stream_url.replace(MASTER_FILE_TYPE, bandwidth+'K/'+bandwidth+'_complete.m3u8') 


    
    #cj = cookielib.LWPCookieJar()
    #cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
    stream_url = stream_url + '|User-Agent='+UA_PS4+'&Cookie='+media_auth

    print "STREAM URL: "+stream_url
    return stream_url
    



def fetchStream(content_id,event_id,playback_scenario):        
    stream_url = ''
    media_auth = ''       
    identity_point_id = ''
    fingerprint = '' 

    expired_cookies = True
    try:
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')) 
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)        

        #Check if cookies have expired
        at_least_one_expired = False
        num_cookies = 0
        for cookie in cj:                        
            num_cookies += 1
            print cookie.name
            print cookie.expires
            print cookie.is_expired()
            if cookie.is_expired():
                at_least_one_expired = True
                break

        if not at_least_one_expired:
            expired_cookies = False
    except:
        pass

    if expired_cookies or num_cookies == 0:
        login()


    cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))     
    cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
    for cookie in cj: 
        print cookie           
        if cookie.name == "ipid":
            identity_point_id = cookie.value
        elif cookie.name == "fprt":
            fingerprint = cookie.value

    if identity_point_id == '' or fingerprint == '':
        return stream_url, media_auth


    session_key = getSessionKey(content_id,event_id,identity_point_id,fingerprint)
    #Reload Cookies
    cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))     
    cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        

    if session_key == '':
        return stream_url, media_auth
    elif session_key == 'blackout':
        msg = "The game you are trying to access is not currently available due to local or national blackout restrictions.\n Full game archives will be available 48 hours after completion of this game."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Game Blacked Out', msg) 
        return stream_url, media_auth

   
    #epoch_time_now = str(int(round(time.time()*1000)))

    #-------------------------
    #Playback Scenario's
    #-------------------------
    '''
    HTTP_CLOUD_WIRED
    HTTP_CLOUD_WIRED_ADS
    HTTP_CLOUD_WIRED_IRDETO
    HTTP_CLOUD_WIRED_WEB
    HTTP_CLOUD_TABLET
    FMS_CLOUD
    HTTP_CLOUD_WIRED_60
    HTTP_CLOUD_WIRED_ADS_60
    HTTP_CLOUD_WIRED_IRDETO_60
    FLASH_500K_400X224
    HTTP_CLOUD_AUDIO
    AUDIO_FMS_32K
    HTTP_CLOUD_AUDIO_TS

    PS4 Calls
    "MF": "https://mlb-ws-mf.media.mlb.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3?",
    "mfPlay": "playbackScenario={playbackScenario}&platform={platform}&contentId={contentID}&identityPointId={identityPointID}&fingerprint={fingerprint}&format=json&auth=cookie",
    "mfCatalog": "platform={platform}&subject=LIVE_EVENT_COVERAGE&format=json&eventId={eventId}&fingerprint={fingerprint}&identityPointId={identityPointId}&auth=cookie",
    '''

    #https://mlb-ws.mlb.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3?identityPointId=31998790&fingerprint=dUVQMTF5bjRrd1N4Rnp0NlVTUk5wR1NMV0E4PXwxNDU3Mzc0NjI0MDU1fGlwdD1lbWFpbC1wYXNzd29yZA==&eventId=14-469489-2016-03-07&platform=WIN8&playbackScenario=HTTP_CLOUD_AUDIO&contentId=546192183&sessionKey=&subject=LIVE_EVENT_COVERAGE
    url = 'https://mlb-ws-mf.media.mlb.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3'
    #url = 'https://mlb-ws.mlb.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3'
    url = url + '?identityPointId='+identity_point_id
    url = url + '&fingerprint='+fingerprint
    url = url + '&contentId='+content_id    
    url = url + '&eventId='+event_id
    url = url + '&playbackScenario='+playback_scenario        
    url = url + '&subject=LIVE_EVENT_COVERAGE'
    url = url + '&sessionKey='+urllib.quote_plus(session_key)
    url = url + '&platform=PS4'
    url = url + '&format=json'
    #url = url + '&frameworkURL=https%3A%2F%2Fmlb-ws-mf.media.mlb.com&frameworkEndPoint=%2Fpubajaxws%2Fbamrest%2FMediaService2_0%2Fop-findUserVerifiedEvent%2Fv-2.3'
    #url = url + '&_='+epoch_time_now
    req = urllib2.Request(url)       
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-US,en;q=0.8")                       
    req.add_header("Connection", "keep-alive")    
    req.add_header("User-Agent", UA_PS4)

    response = opener.open(req)
    #xml_data = response.read()    
    json_source = json.load(response)                                   
    response.close()
    
    #stream_url = find(xml_data,'<url><![CDATA[',']]></url>')       

    if json_source['status_code'] == 1:
        print str(json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']).upper()
        if 'BLACKOUT' in str(json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']).upper():
            msg = "We're sorry.  We have determined that you are blacked out of watching the game you selected due to Major League Baseball exclusivities."
            dialog = xbmcgui.Dialog() 
            ok = dialog.ok('Game Blacked Out', msg) 
            sys.exit()
            xbmc.executebuiltin('Dialog.Close(all,true)')

        else:
            stream_url = json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['url']                
            #Find subtitles
            '''
            for item in json_source['user_verified_event'][0]['user_verified_content'][0]['domain_specific_attributes']:
                if item['name'] == 'closed_captions_location_ttml':
                    subtitles_url = item['value']
                    convertSubtitles(subtitles_url)
            '''
            session_key = json_source['session_key']            
            #Update Session Key
            settings.setSetting(id='session_key', value=session_key)   
    else:
        msg = json_source['status_message']
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Error Fetching Stream', msg)     
        
    
    for cookie in cj:         
        if cookie.name == "mediaAuth":
            media_auth = "mediaAuth="+cookie.value
            settings.setSetting(id='media_auth', value=media_auth)
    
    cj.save(ignore_discard=True)

    return stream_url, media_auth    
   



def getSessionKey(content_id,event_id,identity_point_id,fingerprint):    
    #session_key = ''
    session_key = str(settings.getSetting(id="session_key"))

    if session_key == '':               
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')) 
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))  

        epoch_time_now = str(int(round(time.time()*1000)))           
        url = 'https://mlb-ws-mf.media.mlb.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3'
        url = url + '?identityPointId='+identity_point_id
        url = url + '&fingerprint='+fingerprint
        url = url + '&eventId='+event_id
        url = url + '&subject=LIVE_EVENT_COVERAGE'
        url = url + '&platform=WIN8'
        url = url + '&frameworkURL=https://mlb-ws-mf.media.mlb.com&frameworkEndPoint=/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.3'
        url = url + '&_='+epoch_time_now

        req = urllib2.Request(url)       
        req.add_header("Accept", "*/*")
        req.add_header("Accept-Encoding", "deflate")
        req.add_header("Accept-Language", "en-US,en;q=0.8")                       
        req.add_header("Connection", "keep-alive")        
        req.add_header("User-Agent", UA_PC)
        req.add_header("Origin", "http://m.mlb.com")        
        req.add_header("Referer", "http://m.mlb.com/tv/e"+event_id+"/v"+content_id+"/?&media_type=video&clickOrigin=Media Grid&team=mlb&forwardUrl=http://m.mlb.com/tv/e"+event_id+"/v"+content_id+"/?&media_type=video&clickOrigin=Media%20Grid&team=mlb&template=mp5default&flowId=registration.dynaindex&mediaTypeTemplate=video")
        
        response = opener.open(req)
        xml_data = response.read()
        response.close()
        
        print "REQUESTED SESSION KEY"
        session_key = find(xml_data,'<session-key>','</session-key>')
        settings.setSetting(id='session_key', value=session_key)

        '''
        if json_source['status_code'] == 1:      
            if json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']['status'] == 'BlackedOutStatus':
                msg = "You do not have access to view this content. To watch live games and learn more about blackout restrictions, please visit NHL.TV"
                session_key = 'blackout'
            else:    
                session_key = str(json_source['session_key'])
                settings.setSetting(id='session_key', value=session_key)                              
        else:
            msg = json_source['status_message']
            dialog = xbmcgui.Dialog() 
            ok = dialog.ok('Error Fetching Stream', msg)            
        '''
    return session_key  
    

def myTeamsGames():    
    if FAV_TEAM != 'None':
        fav_team_id = getFavTeamId()

        end_date = localToEastern()
        end_date = stringToDate(end_date, "%Y-%m-%d")            
        start_date = end_date - timedelta(days=30) 
        start_date = start_date.strftime("%Y%m%d")
        end_date = end_date.strftime("%Y%m%d")
        season = start_date.strftime("%Y")
        

        url = 'http://mlb.mlb.com/lookup/named.schedule_vw.bam?end_date='+end_date+'&season='+season+'&team_id='+fav_team_id+'&start_date='+start_date
        #${expand},schedule.ticket&${optionalParams}'
        req = urllib2.Request(url)   
        req.add_header('User-Agent', UA_IPAD)
        response = urllib2.urlopen(req)    
        json_source = json.load(response)                           
        response.close()

        #<row game_pk="469406" record_source="S" game_id="2016/03/01/pitmlb-detmlb-1" game_type="S" month="3" game_date="2016-03-01T00:00:00" month_abbrev="Mar" month_full="March" day="3" day_abbrev="Tue" game_day="Tuesday" double_header_sw="N" gameday_sw="Y" interleague_sw="" game_nbr="1" series_nbr="1" series_game_nbr="1" game_time_et="2016-03-01T13:05:00" if_necessary="N" scheduled_innings="9" inning="9" top_inning_sw="N" away_team_id="134" away_all_star_sw="N" away_team_file_code="pit" away_team_city="Pittsburgh" away_team_full="Pittsburgh Pirates" away_team_brief="Pirates" away_team_abbrev="PIT" away_league_id="104" away_league="NL" away_sport_code="mlb" away_parent_id="" away_parent_org="" away_split_squad="N" home_team_id="116" home_all_star_sw="N" home_team_file_code="det" home_team_city="Detroit" home_team_full="Detroit Tigers" home_team_brief="Tigers" home_team_abbrev="DET" home_league_id="103" home_league="AL" home_sport_code="mlb" home_parent_id="" home_parent_org="" home_split_squad="N" venue_id="2511" venue="Joker Marchant Stadium" venue_short="" venue_city="Lakeland" venue_state="FL" venue_country="USA" milbtv_sw="N" home_tunein="" away_tunein="" game_time_local="3/1/2016 1:05:00 PM" time_zone_local="EST" game_time_home="3/1/2016 1:05:00 PM" time_zone_home="EST" game_time_away="3/1/2016 1:05:00 PM" time_zone_away="EST" resumed_on="" resumed_at="" resumed_from="" rescheduled_to="" rescheduled_at="" rescheduled_from="" game_status_ind="F" game_status_text="Final" reason="" home_probable_id="571510" home_probable="Boyd, Matt" home_probable_wl="0-0" home_probable_era="-.--" away_probable_id="543456" away_probable="Lobstein, Kyle" away_probable_wl="0-0" away_probable_era="-.--" home_team_wl="0-1" away_team_wl="1-0" home_score="2" away_score="4" home_result="L" away_result="W" win_pitcher_id="543746" win_pitcher="Scahill, Rob" win_pitcher_wl="1-0" win_pitcher_era="18.00" loss_pitcher_id="434137" loss_pitcher="Kensing, Logan" loss_pitcher_wl="0-1" loss_pitcher_era="18.00" editorial_stats_type="S" editorial_stats_season="2016"/>
        match = re.compile('<row (.+?)/">').findall(link)   

        for game_row in match:  
        
            for game in date['games']:        
                createGameListItem(game, date['date'])  

        
    else:
        msg = "Please select your favorite team from the addon settings"
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Favorite Team Not Set', msg)


def login():    
    #Check if username and password are provided    
    global USERNAME
    if USERNAME == '':        
        dialog = xbmcgui.Dialog()
        USERNAME = dialog.input('Please enter your username', type=xbmcgui.INPUT_ALPHANUM)        
        settings.setSetting(id='username', value=USERNAME)

    global PASSWORD
    if PASSWORD == '':        
        dialog = xbmcgui.Dialog()
        PASSWORD = dialog.input('Please enter your password', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        settings.setSetting(id='password', value=PASSWORD)

   
    if USERNAME != '' and PASSWORD != '':        
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')) 
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))   
         
        url = 'https://securea.mlb.com/authenticate.do'            
        login_data = 'uri=%2Faccount%2Flogin_register.jsp&registrationAction=identify&emailAddress='+USERNAME+'&password='+PASSWORD+'&submitButton='


        req = urllib2.Request(url, data=login_data, headers=
            {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
             "Accept-Encoding": "gzip, deflate",
             "Accept-Language": "en-US,en;q=0.8",
             "Content-Type": "application/x-www-form-urlencoded",                            
             "Origin": "https://securea.mlb.com",             
             "Connection": "keep-alive",
             #"Cookie": "SESSION_1=wf_forwardUrl===http://m.mlb.com/tv/e14-469412-2016-03-02/v545147283/?&media_type=video&clickOrigin=Media%20Grid&team=mlb~wf_flowId===registration.dynaindex~wf_template===mp5default~wf_mediaTypeTemplate===video~stage===3~flowId===registration.dynaindex~forwardUrl===http://m.mlb.com/tv/e14-469412-2016-03-02/v545147283/?&media_type=video&clickOrigin=Media%20Grid&team=mlb;",
             "Cookie": "SESSION_1=wf_forwardUrl%3D%3D%3Dhttp%3A%2F%2Fm.mlb.com%2Ftv%2Fe14-469412-2016-03-02%2Fv545147283%2F%3F%26media_type%3Dvideo%26clickOrigin%3DMedia%2520Grid%26team%3Dmlb%7Ewf_flowId%3D%3D%3Dregistration.dynaindex%7Ewf_template%3D%3D%3Dmp5default%7Ewf_mediaTypeTemplate%3D%3D%3Dvideo%7Estage%3D%3D%3D3%7EflowId%3D%3D%3Dregistration.dynaindex%7EforwardUrl%3D%3D%3Dhttp%3A%2F%2Fm.mlb.com%2Ftv%2Fe14-469412-2016-03-02%2Fv545147283%2F%3F%26media_type%3Dvideo%26clickOrigin%3DMedia%2520Grid%26team%3Dmlb%3B",
             "User-Agent": UA_PC})  
             
       
        try:
            response = opener.open(req) 
        except HTTPError as e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code    
            print url   
            
            #Error 401 for invalid login
            if e.code == 401:
                msg = "Please check that your username and password are correct"
                dialog = xbmcgui.Dialog() 
                ok = dialog.ok('Invalid Login', msg)

        #response = opener.open(req)              
        #user_data = response.read()
        response.close()
      

        cj.save(ignore_discard=True); 

def logout():
    cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))   
    try:  
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
    except:
        pass
    
    cj.clear()
    cj.save(ignore_discard=True);   

    settings.setSetting(id='session_key', value='') 
    dialog = xbmcgui.Dialog() 
    title = "Logout Successful" 
    dialog.notification(title, 'Logout completed successfully', ICON, 5000, False)

    
params=get_params()
name=None
mode=None
game_day=None
event_id=None
gid=None
teams_stream=None
stream_date=None

try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    game_day=urllib.unquote_plus(params["game_day"])
except:    
    pass
try:
    event_id=urllib.unquote_plus(params["event_id"])
except:
    pass
try:
    gid=urllib.unquote_plus(params["gid"])
except:
    pass
try:
    teams_stream=urllib.unquote_plus(params["teams_stream"])
except:
    pass
try:
    stream_date=urllib.unquote_plus(params["stream_date"])
except:
    pass


print "Mode: "+str(mode)
#print "URL: "+str(url)
print "Name: "+str(name)



if mode==None:        
    categories()  

elif mode == 100:      
    #Todays Games            
    todaysGames(None)    

elif mode == 101:
    #Prev and Next 
    todaysGames(game_day)    

elif mode == 104:    
    streamSelect(event_id, gid, teams_stream, stream_date)

elif mode == 105:
    #Yesterday's Games
    game_day = localToEastern()
    display_day = stringToDate(game_day, "%Y-%m-%d")            
    prev_day = display_day - timedelta(days=1)                
    todaysGames(prev_day.strftime("%Y-%m-%d"))

elif mode == 200:
    #Goto Date
    search_txt = ''
    dialog = xbmcgui.Dialog()
    game_day = dialog.input('Enter date (yyyy-mm-dd)', type=xbmcgui.INPUT_ALPHANUM)
    print game_day
    mat=re.match('(\d{4})-(\d{2})-(\d{2})$', game_day)        
    if mat is not None:    
        todaysGames(game_day)
    else:    
        if game_day != '':    
            msg = "The date entered is not in the format required."
            dialog = xbmcgui.Dialog() 
            ok = dialog.ok('Invalid Date', msg)

        sys.exit()        

elif mode == 400:    
    logout()

elif mode == 500:
    myTeamsGames()

elif mode == 900:        
    getGamesForDate(stream_date)
    playAllHighlights()    

elif mode == 999:
    sys.exit()

print mode
if mode==100 or mode==101 or mode==104 or mode==105 or mode==200 or mode==300 or mode==500: 
   setViewMode()
elif mode==None:
    getViewMode()
    
print "My view mode " + VIEW_MODE

if mode == 100:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
elif mode == 101:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False, updateListing=True)
else:
    xbmcplugin.endOfDirectory(addon_handle)