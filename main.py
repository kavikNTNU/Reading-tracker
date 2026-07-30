from fastapi import FastAPI

app = FastAPI()
#print("Hello world test0")
@app.get("/")
def read_root():
    #print("Hello world test")
    return {"Hello": "World"}
