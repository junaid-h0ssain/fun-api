from main import FunAPI


funapi = FunAPI()

@funapi.get("/users/{id}")
def get_users(req, res):
    res.send("['welcome','from','funapi']", 202)

@funapi.post("/users")
def create_user(req, res):
    res.send("User Created", "201")

@funapi.put("/users")
def update_user(req, res):
    res.send("User Updated", "200")

@funapi.delete("/users")
def delete_user(req, res):
    res.send("User Deleted", "200")

