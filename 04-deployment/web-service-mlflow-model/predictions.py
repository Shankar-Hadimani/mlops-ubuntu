from flask import Flask, request, jsonify
import pandas as pd
import mlflow
import pickle

RUN_ID = 'e041808c2a2849919731587f28600398'
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"

mlflow.set_tracking_uri(uri= MLFLOW_TRACKING_URI)
mlflow.set_experiment("green-taxi-ride-duration")

# ### download the artifact - vectorizer
# vectorizer_path = mlflow.artifacts.download_artifacts(run_id=RUN_ID, artifact_path='dict_vectorizer.bin')
# print(f"Dowloing the vectorizer artifact at path : {vectorizer_path}")

# ## read the artifact and assign dictionary vectorizer
# with open(vectorizer_path, 'rb') as f_in:
#     dv = pickle.load(f_in)


# Load model as a PyFuncModel.
logged_model = f'runs:/{RUN_ID}/model'
model = mlflow.pyfunc.load_model(logged_model)


def prepare_features(ride_dict):
    features={}
    features['PICKUP_DROPOFF'] = '%s_%s' %(ride_dict['PULocationID'],ride_dict['DOLocationID'] )
    features['trip_distance'] = ride_dict['trip_distance']
    return features


def predict(features):
    # X = dv.transform(features)
    # preds = model.predict(X)
    preds = model.predict(features)

    return float(preds[0])

### create an flask endpoint
app = Flask('predict_duration')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()
    features = prepare_features(ride_dict=ride)
    pred = predict(features)

    result = {
        "duration":pred,
        "model_version_runid":RUN_ID
    }

    return jsonify(result)


### setup main object entry point
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)