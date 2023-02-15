from fastapi import FastAPI
restapi = FastAPI()
@restapi.get("/")
def reed_root():
    return{"Hello": "World"}

@restapi.get("/datalogger/{id}")
def read_item(id: int):
    return {"id": id}
