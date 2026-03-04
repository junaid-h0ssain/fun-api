from main import FunAPI


funapi = FunAPI()

@funapi.get("/users")
def get_users(req, res):
    res['status_code'] = "200 OK"
    res['headers'] = []
    res['text'] = "['my','name','is','funapi']"


