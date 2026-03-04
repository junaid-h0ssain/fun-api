from main import FunAPI


funapi = FunAPI()

@funapi.get("/users")
def get_users(req, res):
    res.send("['welcome','from','funapi']", "200 OK")


