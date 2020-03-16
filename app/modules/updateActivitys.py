import sys
from . import *

def updateFromMoodle( db, type_item, url_moodle, course_id, item_id ):
    
    if type_item == "chat":
        upChat( db, url_moodle, course_id, item_id )
    elif type_item == "data":
        upData( db, url_moodle, course_id, item_id )
    elif type_item == "forum":
        upForum( db, url_moodle, course_id, item_id )
    elif type_item == "lti":
        upLTI( db, url_moodle, course_id, item_id )
    elif type_item == "Glossario":
        upGlossario( db, url_moodle, course_id, item_id )
    elif type_item == "wiki":
        upWiki( db, url_moodle, course_id, item_id )
    elif type_item == "quiz":
        upQuiz( db, url_moodle, course_id, item_id )
    elif type_item == "choice":
        #upChoice( db, url_moodle, course_id, item_id )
        pass

def upQuiz( db, url_moodle, course_id, item_id ):

    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:QuizInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_quiz"]

    quiz = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) return quiz").data()        
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) return network").data()[0]['network']

    quiz_updated = getQuiz( network['url'], network['token'], course_id, item_id )
    print(str(quiz_updated), file=sys.stderr)
    name = quiz_updated["name"]
    description = quiz_updated["description"]
    time_limit = quiz_updated["time_limit"]
    open_date = quiz_updated["timeopen"]
    end_date  = quiz_updated["timeclose"]
    new_page = quiz_updated["new_page"]
    shuffle = quiz_updated["shuffleanswers"]
    allow_time_limit = True if time_limit and len(time_limit)>0 else False
    allow_open_date = True if open_date and len(open_date)>0 else False
    allow_end_date = True if end_date and len(end_date)>0 else False

    query = f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) \
            SET quiz.name = '{name}',\
        quiz.description = '{description}',\
        quiz.time_limit = '{time_limit}',\
        quiz.open_date = '{open_date}',\
        quiz.end_date  = '{end_date}',\
        quiz.new_page = '{new_page}',\
        quiz.allow_time_limit = '{allow_time_limit}',\
        quiz.allow_open_date = '{allow_open_date}',\
        quiz.allow_end_date = '{allow_end_date}',\
        quiz.shuffle = '{shuffle}' return quiz"
    
    db.run(query).data()

    uuid_quiz = quiz[0]['quiz']['uuid']
    
    all_instances = db.run("MATCH (instance:QuizInstance{id_quiz: '%s'}) return instance" % (uuid_quiz)).data()
    
    #atualizar todas 'turmas' já criadas
    
    for instance in all_instances:

        result = instance['instance']
        if result['id_instance'] != item_id:
            updateQuiz(network['url'], network['token'], result['id_instance'], name, description, open_date, end_date )

def upWiki( db, url_moodle, course_id, item_id ):
    
    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:WikiInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_wiki"]

    wiki = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(wiki:Wiki{{uuid:'{uuid}'}}) return wiki").data()        
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(wiki:Wiki{{uuid:'{uuid}'}}) return network").data()[0]['network']

    wiki_updated = getWiki( network['url'], network['token'], course_id, item_id )
    
    name = dataDict["name"]
    description = dataDict["description"]
    wikimode = dataDict["wikimode"]
    firstpagetitle = dataDict["firstpagetitle"]
    defaultformat = dataDict["defaultformat"]

    query = f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(wiki:Wiki{{uuid:'{uuid}'}}) \
        SET wiki.name = '{name}',\
        wiki.description = '{description}',\
        wiki.wikimode = '{wikimode}',\
        wiki.firstpagetitle = '{firstpagetitle}',\
        wiki.defaultformat = '{defaultformat}'\
        return wiki"
    
    db.run(query).data()

    uuid_wiki = wiki[0]['wiki']['uuid']
    
    all_instances = db.run("MATCH (instance:WikiInstance{id_wiki: '%s'}) return instance" % (uuid_wiki)).data()
    
    #atualizar todas 'turmas' já criadas
    
    for instance in all_instances:

        result = instance['instance']
        if result['id_instance'] != item_id:
            updateWiki(network['url'], network['token'], result['id_instance'], name, description, wikimode, firstpagetitle, defaultformat)

def upGlossario( db, url_moodle, course_id, item_id ):
    
    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:GlossarioInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_glossario"]

    glossario = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(glossario:Glossario{{uuid:'{uuid}'}}) return glossario").data()        
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(glossario:Glossario{{uuid:'{uuid}'}}) return network").data()[0]['network']

    glossario_updated = getGlossary( network['url'], network['token'], course_id, item_id )
    
    name = glossario_updated["name"]
    description = glossario_updated["description"]
    type_glossario = glossario_updated["mainglossary"]
    allow_new_item = glossario_updated["defaultapproval"]
    allow_edit = glossario_updated["editalways"]
    allow_repeat_item = glossario_updated["allowduplicatedentries"]
    allow_comments = glossario_updated["allowcomments"]
    allow_automatic_links = glossario_updated["usedynalink"]
    type_view = glossario_updated["displayformat"]
    type_view_approved = glossario_updated["approvaldisplayformat"]
    num_items_by_page = glossario_updated["entbypage"]
    show_alphabet = glossario_updated["showalphabet"]
    show_todos = glossario_updated["showall"]
    show_special = glossario_updated["showspecial"]
    allow_print = glossario_updated["allowprintview"]

    query = f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(glossario:Glossario{{uuid:'{uuid}'}}) \
        SET glossario.name = '{name}',\
        glossario.description = '{description}',\
        glossario.type_glossario = '{type_glossario}',\
        glossario.allow_new_item = '{allow_new_item}',\
        glossario.allow_edit = '{allow_edit}',\
        glossario.allow_repeat_item = '{allow_repeat_item}',\
        glossario.allow_comments = '{allow_comments}',\
        glossario.allow_automatic_links = '{allow_automatic_links}',\
        glossario.type_view = '{type_view}',\
        glossario.type_view_approved = '{type_view_approved}',\
        glossario.num_items_by_page = '{num_items_by_page}',\
        glossario.show_alphabet = '{show_alphabet}',\
        glossario.show_todos = '{show_todos}',\
        glossario.show_special = '{show_special}',\
        glossario.allow_print = '{allow_print}'\
                return glossario"
    
    db.run(query).data()

    uuid_glossario = glossario[0]['glossario']['uuid']
    
    all_instances = db.run("MATCH (instance:GlossarioInstance{id_glossario: '%s'}) return instance" % (uuid_glossario)).data()
    
    #atualizar todas 'turmas' já criadas
    
    for instance in all_instances:

        result = instance['instance']
        if result['id_instance'] != item_id:
            updateGlossario(network['url'], network['token'], result['id_instance'], name, description, type_glossario, allow_new_item, allow_edit,
                allow_repeat_item,allow_comments,allow_automatic_links,type_view,type_view_approved,num_items_by_page,
                show_alphabet,show_todos,show_special,allow_print)
        
def upLTI( db, url_moodle, course_id, item_id ):
    
    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:ExternToolInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_extern_tool"]

    extern_tool = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(lti:ExternTool{{uuid:'{uuid}'}}) return lti").data()        
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(lti:ExternTool{{uuid:'{uuid}'}}) return network").data()[0]['network']

    lti_updated = getLTI( network['url'], network['token'], course_id, item_id )
    
    name = lti_updated["name"]
    
    description = lti_updated["description"]
    show_description_course = lti_updated["showdescription"]
    show_activity = lti_updated["showtitlelaunch"]
    show_description_activity = lti_updated["showdescriptionlaunch"]

    pre_config_url = lti_updated["typeid"]
    url_tool = lti_updated["toolurl"]
    url_tool_ssl = lti_updated["securetoolurl"]

    pre_config = lti_updated["launchcontainer"]
    key_consumer = lti_updated["resourcekey"]
    key_secret = lti_updated["password"]
    custom_params = lti_updated["instructorcustomparameters"]

    query = f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(externtool:ExternTool{{uuid:'{uuid}'}}) \
        SET externtool.name = '{name}',\
        externtool.description = '{description}',\
        externtool.show_description_course = '{show_description_course}',\
        externtool.show_activity = '{show_activity}',\
        externtool.show_description_activity = '{show_description_activity}',\
        externtool.pre_config_url = '{pre_config_url}',\
        externtool.url_tool = '{url_tool}',\
        externtool.url_tool_ssl = '{url_tool_ssl}',\
        externtool.pre_config = '{pre_config}',\
        externtool.key_consumer = '{key_consumer}',\
        externtool.key_secret = '{key_secret}',\
        externtool.custom_params = '{custom_params}'\
                return externtool"
    
    db.run(query).data()

    uuid_lti= extern_tool[0]['externtool']['uuid']
    
    all_instances = db.run("MATCH (instance:ExternToolInstance{id_extern_tool: '%s'}) return instance" % (uuid_lti)).data()
    
    #atualizar todas 'turmas' já criadas
    
    for instance in all_instances:

        result = instance['instance']
        if result['id_instance'] != item_id:
            updateExterntool(network['url'], network['token'], result['id_instance'], name, description, show_description_course, show_activity, show_description_activity,
                pre_config_url, url_tool, url_tool_ssl, pre_config, key_consumer, key_secret, custom_params)
        
def upForum( db, url_moodle, course_id, item_id ):
    
    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:ForumInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_forum"]

    forum = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(forum:Forum{{uuid:'{uuid}'}}) return forum").data()        
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(forum:Forum{{uuid:'{uuid}'}}) return network").data()[0]['network']

    forum_updated = getForum( network['url'], network['token'], course_id, item_id )
    
    name = forum_updated["name"]
    description = forum_updated["description"]
    type_forum = forum_updated["type"]
    maxbytes = forum_updated["maxbytes"]
    maxattachments = forum_updated["maxattachments"]
    displaywordcount = forum_updated["displaywordcount"]
    forcesubscribe = forum_updated["forcesubscribe"]
    trackingtype = forum_updated["trackingtype"]

    query = f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(forum:Forum{{uuid:'{uuid}'}}) \
        SET forum.name = '{name}',\
        forum.description = '{description}',\
        forum.type_forum = '{type_forum}',\
        forum.maxbytes = '{maxbytes}',\
        forum.maxattachments = '{maxattachments}',\
        forum.displaywordcount = '{displaywordcount}',\
        forum.forcesubscribe = '{forcesubscribe}',\
        forum.trackingtype = '{trackingtype}'\
                return forum"
    
    db.run(query).data()

    uuid_forum = chat[0]['forum']['uuid']
    
    all_instances = db.run("MATCH (instance:ForumInstance{id_forum: '%s'}) return instance" % (uuid_forum)).data()
    
    #atualizar todas 'turmas' já criadas
    
    for instance in all_instances:

        result = instance['instance']
        if result['id_instance'] != item_id:
            updateForum(network['url'], network['token'], result['id_instance'], name, description, type_forum, maxbytes, 
                maxattachments, displaywordcount, forcesubscribe, trackingtype)

def upData( db, url_moodle, course_id, item_id ):

    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:DatabaseInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_database"]

    database = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(data:Database{{uuid:'{uuid}'}}) return data").data()        
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(data:Database{{uuid:'{uuid}'}}) return network").data()[0]['network']

    data_updated = getDatabase( network['url'], network['token'], course_id, item_id )

    name = data_updated["name"]
    description = data_updated["description"]
    approval_required = data_updated["approval"]
    allow_edit_approval_entries = data_updated["manageapproved"]
    allow_comment = data_updated["comments"]
    required_before_viewing = data_updated["requiredentries"]
    max_entries = data_updated["maxentries"]

    open_date = data_updated["timeavailablefrom"]
    end_date = data_updated["timeavailableto"]
    read_only = data_updated["timeviewfrom"]
    read_only_end = data_updated["timeviewto"]

    allow_read_only_end = True if end_date else False
    allow_read_only = True if open_date else False
    allow_open_date = True if read_only else False
    allow_end_date = True if read_only_end else False

    query = f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(database:Database{{uuid:'{uuid}'}}) \
            SET database.name = '{name}',\
            database.description = '{description}',\
            database.approval_required = '{approval_required}',\
            database.allow_edit_approval_entries = '{allow_edit_approval_entries}',\
            database.allow_comment = '{allow_comment}',\
            database.required_before_viewing = '{required_before_viewing}',\
            database.max_entries = '{max_entries}',\
            database.open_date = '{open_date}',\
            database.end_date = '{end_date}',\
            database.read_only = '{read_only}',\
            database.read_only_end = '{read_only_end}',\
            database.allow_read_only_end = '{allow_read_only_end}',\
            database.allow_read_only = '{allow_read_only}',\
            database.allow_open_date = '{allow_open_date}',\
            database.allow_end_date = '{allow_end_date}'\
             return database"
    
    db.run(query).data()

    uuid_data = database[0]['data']['uuid']
    
    all_instances = db.run("MATCH (instance:DatabaseInstance{id_database: '%s'}) return instance" % (uuid_data)).data()
    
    #atualizar todas 'turmas' já criadas
    
    for instance in all_instances:
        result = instance['instance']

        if result['id_instance'] != item_id:
            updateDatabase(network['url'], network['token'], result['id_instance'], name, description, approval_required, allow_edit_approval_entries, allow_comment, 
                required_before_viewing, max_entries, open_date, end_date, read_only, read_only_end)

def upChat( db, url_moodle, course_id, item_id ):

    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:ChatInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_chat"]

    chat = db.run( f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(chat:Chat{{uuid:'{uuid}'}}) return chat").data()        
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(chat:Chat{{uuid:'{uuid}'}}) return network").data()[0]['network']

    chat_updated = getChat( network['url'], network['token'], course_id, item_id )

    name = chat_updated["name"]
    description = chat_updated["description"]
    
    query = f"MATCH (a:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(chat:Chat{{uuid:'{uuid}'}}) \
        SET chat.name = '{name}',\
        chat.description = '{description}' return chat"
    
    db.run(query).data()

    uuid_chat = chat[0]['chat']['uuid']
    
    all_instances = db.run("MATCH (instance:ChatInstance{id_chat: '%s'}) return instance" % (uuid_chat)).data()
    
    #atualizar todas 'turmas' já criadas
    
    for instance in all_instances:
        
        result = instance['instance']
        if result['id_instance'] != item_id:
            updateChat(network['url'], network['token'], result['id_instance'], name, description)