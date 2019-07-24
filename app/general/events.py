import requests
import sys

def getBestNote(url_base, token, userid, quizid):
    function = "mod_quiz_get_user_best_grade"
    
    params = f"&userid={userid}&quizid={quizid}"

    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    r = requests.post( final_url, data={})
    result = r.json()

    return result[0]

def userCompletQuiz(id_quiz, id_user, url_moodle):

    all_instances = db.run("MATCH (a:Network{url:'%s'})-[r2]-(c:Course{id:%s})-[r3]-(instance:QuizInstance{id_instance:%s}) return instance" % (url_moodle, course_id, item_id)).data()

    result = all_instances[0]['instance']

    uuid = result["id_quiz"]
    network = db.run( f"MATCH (network:Network{{url:'{url_moodle}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) return network").data()[0]['network']

    
    best_grade = getBestNote(url_moodle, network['token'], id_user, id_quiz)
    print(best_grade, file=sys.stderer)