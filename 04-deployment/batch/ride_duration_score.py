import pandas as pd
import mlflow
import os
import uuid
import sys

from prefect import task, flow, get_run_logger
from prefect.context import get_run_context
from datetime import datetime
from dateutil.relativedelta import relativedelta


def generate_uuids(n):
    ride_ids =[]
    for i in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids

def read_data(filename:str):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime 
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    
    df['ride_id'] = generate_uuids(len(df))
    
    return df

def prepare_dictionaries(df:pd.DataFrame):
    categorical = ['PULocationID','DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    df['PICKUP_DROPOFF'] = df['PULocationID'] + '_' + df['DOLocationID']
    categorical = ['PICKUP_DROPOFF']
    numerical = ['trip_distance']
    dict_dataset = df[categorical + numerical].to_dict(orient='records')
    return dict_dataset


def load_model(run_id):
    
    # Load model as a PyFuncModel.
    logged_model = f"../web-service-mlflow-model/mlflow-artifacts/1/{run_id}/artifacts/model"
    model = mlflow.pyfunc.load_model(logged_model)
    return model
    
def save_results(df, y_pred, run_id, output_path):

    ### logger from prefect
    logger = get_run_logger()

    ### create empty dataframe
    result = pd.DataFrame()
    result['PULocationID'] = df['PULocationID']
    result['DOLocationID']=df['DOLocationID']
    result['actual_duration'] = df['duration']
    result['predicted_duration'] = y_pred
    result['diff'] = result['actual_duration'] - result['predicted_duration']
    result['model_version'] = run_id

    logger.info(f"saving the results to ...{output_path}")
    result.to_parquet(output_path, index=False) 

@task
def apply_model(input_path, output_path, run_id):

    ### logger from prefect
    logger = get_run_logger()

    logger.info(f"Reading the data from {input_path}")
    df = read_data(input_path)
    dicts = prepare_dictionaries(df)
    
    ## load model
    logger.info(f"Loading model from RUN_ID: {run_id}")
    model = load_model(run_id)
    
    ## predict model
    logger.info(f"Prediction is being done...")
    y_pred = model.predict(dicts)

    save_results(
            df=df,
            y_pred=y_pred, 
            run_id=run_id, 
            output_path=output_path)
    
    return None


def get_paths(run_date, taxi_type):

    prev_month = run_date - relativedelta(months=1)
    YEAR = prev_month.year
    MONTH = prev_month.month

    INPUT_PATH= f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{YEAR:04d}-{MONTH:02d}.parquet'
    OUTPUT_PATH = f'./output/{taxi_type}/{YEAR:04d}-{MONTH:02d}.parquet' 

    return INPUT_PATH,  OUTPUT_PATH

@flow
def ride_durartion_prediction(
    taxi_type:str, 
    run_id:str,
    run_date:datetime=None):

    if run_date is None:
        ctx = get_run_context()
        run_date=ctx.flow_run.expected_start_time

    INPUT_PATH,  OUTPUT_PATH = get_paths(run_date=run_date, taxi_type=taxi_type)

    apply_model(
        input_path=INPUT_PATH, 
        output_path=OUTPUT_PATH, 
        run_id=run_id
        )

    return None



def run():
    YEAR =  int(sys.argv[1])   # year - 2021
    MONTH=  int(sys.argv[2]) # month 2
    TAXI_TYPE =  sys.argv[3] # taxi color 'green'
    RUN_ID = sys.argv[4]  ### 'e041808c2a2849919731587f28600398' 

    ride_durartion_prediction(taxi_type=TAXI_TYPE,
    run_id=RUN_ID,
    run_date=datetime(year=YEAR, month=MONTH, day=1)
    )


if __name__=='__main__':
    run()