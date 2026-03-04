from main import FunAPI


def my_middleware(res):
    print("Middleware works")

def another_middleware_local(res):
    print("Another Middleware works")

funapi = FunAPI(middleware=[my_middleware])

@funapi.get("/users/{id}", middleware=[another_middleware_local])
def get_users(req, res, id):
    # res.send("['welcome','from','funapi']", 202)
    res.send(id, "200")

@funapi.post("/users")
def create_user(req, res):
    res.send("User Created", "201")

@funapi.put("/users")
def update_user(req, res):
    res.send("User Updated", "200")

@funapi.delete("/users")
def delete_user(req, res):
    res.send("User Deleted", "200")


