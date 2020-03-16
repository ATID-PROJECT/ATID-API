import urllib.request, json 
    
@start_controller.route('/')
def index(db: Graph, moodle_server, token):
    moodle_connection = f"{moodle_server}/webservice/rest/server.php?wstoken={token}&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
    with urllib.request.urlopen( moodle_connection ) as url:
        data = json.loads(url.read().decode())
        print(data)
    return "API ATID"