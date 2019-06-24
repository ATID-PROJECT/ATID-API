

url_moodle = "webservice/rest/server.php?wstoken={0}&wsfunction={1}&moodlewsrestformat=json"

def createAssign(token, course_id, name, description, wikimode, firstpagetitle, defaultformat):
    function = "local_wstemplate_handle_assign"
    
    params = f"&name={name}\
            &description={description}\
            &course_id={course_id}\
            &wikimode={wikimode}\
            &firstpagetitle={firstpagetitle}\
            &defaultformat={defaultformat}\
        "

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = json.loads( r.text )
    return "ok"

def createChoice(token, course_id, name, description, allowupdate, allowmultiple, limitanswers):
    function = "local_wstemplate_handle_choice"
    
    params = f"&name={name}\
            &description={description}\
            &course_id={course_id}\
            &allowupdate={wikimode}\
            &allowmultiple={firstpagetitle}\
            &limitanswers={defaultformat}\
        "

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = json.loads( r.text )
    return "ok"

def creteDatabase(token, course_id, name, description, wikimode, firstpagetitle, defaultformat):
    function = "local_wstemplate_handle_data"
    
    params = f"&name={name}\
            &description={description}\
            &course_id={course_id}\
            &allowupdate={wikimode}\
            &allowmultiple={firstpagetitle}\
            &limitanswers={defaultformat}\
        "

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = json.loads( r.text )
    return "ok"

def createLTI(token, course_id, name, description, instructorchoicesendname, instructorchoicesendemailaddr, instructorchoiceacceptgrades,
    showdescription, showtitlelaunch, showdescriptionlaunch, typeid, launchcontainer,resourcekey, password, externtool_custom_params):
    function = "local_wstemplate_handle_data"
    
    params = f"&name={name}\
            &description={description}\
            &course_id={course_id}\
            &instructorchoicesendname={instructorchoicesendname}\
            &instructorchoicesendemailaddr={instructorchoicesendemailaddr}\
            &showdescription={showdescription}\
            &showtitlelaunch={showtitlelaunch}\
            &showdescriptionlaunch={showdescriptionlaunch}\
            &typeid={typeid}\
            &launchcontainer={launchcontainer}\
            &resourcekey={resourcekey}\
            &password={password}\
            &externtool_custom_params={externtool_custom_params}\
        "

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = json.loads( r.text )
    return "ok"

def createFeedback(token, course_id, name, description, wikimode, firstpagetitle, defaultformat):
    function = "local_wstemplate_handle_data"
    
    params = f"&name={name}\
            &description={description}\
            &course_id={course_id}\
            &instructorchoicesendname={instructorchoicesendname}\
            &instructorchoicesendemailaddr={instructorchoicesendemailaddr}\
            &instructorchoiceacceptgrades={instructorchoiceacceptgrades}\
            &showdescription={showdescription}\
            &showtitlelaunch={showtitlelaunch}\
            &showdescriptionlaunch={showdescriptionlaunch}\
            &typeid={typeid}\
            &launchcontainer={launchcontainer}\
            &resourcekey={resourcekey}\
            &password={password}\
            &externtool_custom_params={externtool_custom_params}\
        "

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = json.loads( r.text )
    return "ok"

def createForum(token, course_id, name, description, wikimode, firstpagetitle, defaultformat):
    function = "local_wstemplate_handle_data"
    
    params = f"&name={name}\
            &description={description}\
            &course_id={course_id}\
            &allowupdate={wikimode}\
            &allowmultiple={firstpagetitle}\
            &limitanswers={defaultformat}\
        "

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = json.loads( r.text )
    return "ok"

def createGlossary(token, course_id, name, description, type_, maxbytes, maxattachments, displaywordcount, forcesubscribe, trackingtype):
    function = "local_wstemplate_handle_forum"
    
    params = f"&name={name}\
            &description={description}\
            &course_id={course_id}\
            &type={type_}\
            &maxbytes={maxbytes}\
            &maxattachments={maxattachments}\
            &displaywordcount={displaywordcount}\
            &forcesubscribe={forcesubscribe}\
            &trackingtype={trackingtype}\
        "

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={})
    result = json.loads( r.text )
    return "ok"