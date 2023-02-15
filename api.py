from fastapi import FastAPI, Depends, HTTPException
import os
from dotenv import load_dotenv 

load_dotenv()
restapi = FastAPI()
apikey=os.getenv("API_KEY")
avain = APIKeyheader(name='avain')

def apikey_auth(APIKey: str = Depends(avain)):
    if avain != apikey:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Virheellinen API avain." )

@app.post("/datalogger/start/{id}, dependencies=[Depends(apikey_auth)])")
async def create_item(id: str):
    return {"nimi": id}

@app.post("/datalogger/finish, dependencies=[Depends(apikey_auth)])")
def reed_root():
    return {"datan keruu lopetetaan"}

@restapi.get("/")
def reed_root():
    return{"Hello": "World"}

@restapi.get("/datalogger/raportti/results?{id}", dependencies=[Depends(apikey_auth)])
async def read_item(id: str):
    return {"id": str}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080)
