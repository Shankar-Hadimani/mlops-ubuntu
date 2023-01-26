import predictions

ride = {
    "PULocationID":10,
    "DOLocationID":40,
    "trip_distance":50
}


features = predictions.prepare_features(ride_dict=ride)
pred = predictions.predict(features)
print(pred)
