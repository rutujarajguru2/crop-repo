from flask import Flask, request, render_template
import numpy as np
import pandas as pd
import pickle
from azure.storage.blob import BlobServiceClient

# Creating Flask app
app = Flask(__name__)

# Azure Blob Storage credentials
account_name = 'pklstore'
account_key = 'TII+Cx+U/1QZU2nydcjplG0+6a3prHlFBppRRvz3FZtSi1o1uHUpqVV5IZ49wYt1CnXfVVnvMw2g+AStqyRkRQ=='
container_name = 'cropfiles'
blob_names = ['model.pkl', 'standscaler.pkl', 'minmaxscaler.pkl']

# Connect to Azure Blob Storage
blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net",
                                       credential=account_key)
container_client = blob_service_client.get_container_client(container_name)

# Fetching files from Azure Blob Storage
for blob_name in blob_names:
    blob_client = container_client.get_blob_client(blob_name)
    with open(blob_name, "wb") as my_blob:
        download_stream = blob_client.download_blob()
        my_blob.write(download_stream.readall())

# Load the model and scalers
model_filename = 'model.pkl'
standscaler_filename = 'standscaler.pkl'
minmaxscaler_filename = 'minmaxscaler.pkl'

with open(model_filename, 'wb') as f:
    blob_data = container_client.get_blob_client(model_filename).download_blob()
    blob_data.readinto(f)

with open(standscaler_filename, 'wb') as f:
    blob_data = container_client.get_blob_client(standscaler_filename).download_blob()
    blob_data.readinto(f)

with open(minmaxscaler_filename, 'wb') as f:
    blob_data = container_client.get_blob_client(minmaxscaler_filename).download_blob()
    blob_data.readinto(f)

model = pickle.load(open(model_filename, 'rb'))
sc = pickle.load(open(standscaler_filename, 'rb'))
ms = pickle.load(open(minmaxscaler_filename, 'rb'))

# Define Flask routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    N = request.form['Nitrogen']
    P = request.form['Phosporus']
    K = request.form['Potassium']
    temp = request.form['Temperature']
    humidity = request.form['Humidity']
    ph = request.form['Ph']
    rainfall = request.form['Rainfall']

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    single_pred = np.array(feature_list).reshape(1, -1)

    scaled_features = ms.transform(single_pred)
    final_features = sc.transform(scaled_features)
    prediction = model.predict(final_features)

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                 19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        result = "{} is the best crop to be cultivated right there".format(crop)
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
    return render_template('index.html', result=result)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
