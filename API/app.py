import joblib
from xmlrpc.client import Boolean
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List
from fastapi import FastAPI, Request
import json
from typing import Literal, List, Union

# description will apear in the doc
description = """
Welcome to GETAROUND prediction API

GetAround is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide.

We worked on price optimization. Thanks to automatic learning, we propose you the optimal prices for the owner of the cars to rent !

Here are two endpoints you can try:

## Preview

Simply returns preview of the dataset!

* `/preview` here you can have a preview of the cars pricing dataset


## Prediction

This is a Machine Learning endpoint that predict price given some car's informations. Here is the endpoint:

* `/predict` put your cars informations here and you'll get you rental price per day


Check out documentation below 👇 for more information on each endpoint. 
"""

# tags to easily sort roots
tags_metadata = [
    {
        "name": "Preview",
        "description": "Preview of the existing data",
    },

    {
        "name": "Prediction",
        "description": "Prediction of the rental price based on a machine learning model"
    }
]


# initialise API object
app = FastAPI(
    title="GETAROUND API",
    description=description,
    version="1.0",
    contact={
        "name": "CoralieGM",
        "url": "https://github.com/CoralieGM",
    },
    openapi_tags=tags_metadata
)

# Define features used in machine learning
class PredictionFeatures(BaseModel):
    model_key: str = "Mercedes"
    mileage: int = 181672
    engine_power: int = 105
    fuel: str = "diesel"
    paint_color: str = "white"
    car_type: str = "hatchback"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = False
    winter_tires: bool = True


@app.get("/Preview", tags=["Preview"])
async def random_data(rows: int= 3):
    try:
        if rows < 21 :
            data = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv")
            sample = data.sample(rows)
            response0= sample.to_json(orient='records')
        else:
            response0 = json.dumps({"message" : "Error! Please select a row number not more than 20."})
    except:
            response0 = json.dumps({"message" : "Error! Problem in accessing to historical data."})
    return response0


@app.post("/Prediction", tags=["Prediction"])
async def predict(predictionFeatures: PredictionFeatures):
    # Read data 
    df = pd.DataFrame(dict(predictionFeatures), index=[0])
    #print(df)

    # Load the models from local
    model_lr  = 'model.joblib'
    regressor = joblib.load(model_lr)
    prediction = regressor.predict(df)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)