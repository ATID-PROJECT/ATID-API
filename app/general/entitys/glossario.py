from dynaconf import settings
import requests
import sys

def createGlossario(url_base, token, course_id, name, description, mainglossary, defaultapproval, editalways, allowduplicatedentries, allowcomments, usedynalink,
displayformat, approvaldisplayformat, entbypage, showalphabet, showall, showspecial, allowprintview):
    
    function = "local_wstemplate_handle_glossary"
    params = f"&name={name}&description={description}&course_id={course_id}&mainglossary={mainglossary}&defaultapproval={defaultapproval}&editalways={editalways}&\
        allowduplicatedentries={allowduplicatedentries}&allowcomments={allowcomments}&usedynalink={usedynalink}&displayformat={displayformat}&approvaldisplayformat={approvaldisplayformat}&\
        entbypage={entbypage}&showalphabet={showalphabet}&showall={showall}&showspecial={showspecial}&allowprintview={allowprintview}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    print(final_url, file=sys.stderr)
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def updateGlossario(url_base, token, glossario_id, name, description, mainglossary, defaultapproval, editalways, allowduplicatedentries, allowcomments, usedynalink,
displayformat, approvaldisplayformat, entbypage, showalphabet, showall, showspecial, allowprintview):

    function = "update_glossario"
    
    params = f"&name={name}&description={description}&glossario_id={glossario_id}&mainglossary={mainglossary}&defaultapproval={defaultapproval}&editalways={editalways}&\
        allowduplicatedentries={allowduplicatedentries}&allowcomments={allowcomments}&usedynalink={usedynalink}&displayformat={displayformat}&approvaldisplayformat={approvaldisplayformat}&\
        entbypage={entbypage}&showalphabet={showalphabet}&showall={showall}&showspecial={showspecial}&allowprintview={allowprintview}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result