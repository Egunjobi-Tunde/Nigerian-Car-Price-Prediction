# -*- coding: utf-8 -*-
"""Nigerian Car Price Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RtrEB_oX2Q9llgG2KysiBNuIg-EEtpdv
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
sns.set_style("darkgrid")
sns.set_palette('RdYlGn')

#model
from sklearn.preprocessing import LabelEncoder,StandardScaler,MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression

import gradio as gr
import joblib

df = pd.read_csv("/content/Nigerian_Car_Prices.csv")

df.head()

df.info()

"""### Data Cleaning"""

df = df.drop('Build', axis = 1)

df = df.dropna()

df.shape

df['Price'] = df['Price'].str.replace(',', '') 
df['Price'] = df['Price'].astype(float)  

df['Year of manufacture'] = df['Year of manufacture'].astype(int)

df.describe()

"""### EDA

### Feature Engineering
"""

#the brand new is just 5, it will be drop
# Dropping the 'Brand New' category
df = df[df['Condition'] != 'Brand New']

X = df.drop(['Unnamed: 0', 'Price'], axis = 1)
y = df.Price

make_counts = X['Make'].value_counts()


# Get the values to replace with 'Others'
make_others = make_counts[make_counts < 14].index.tolist()

# Replace values with 'Others'
X['Make'] = X['Make'].apply(lambda x: 'Others' if x in make_others else x)

X_train,X_test, y_train,y_test = train_test_split(X,y, test_size = 0.2, random_state=10)


# Initializing the encoders and scaler for each column
make_encoder = LabelEncoder()
fuel_encoder = LabelEncoder()
transmission_encoder = LabelEncoder()
condition_encoder = LabelEncoder()
scaler = MinMaxScaler()

# Encoding and scaling each column individually
X_train['Make'] = make_encoder.fit_transform(X_train['Make'])
X_test['Make'] = make_encoder.transform(X_test['Make'])

X_train['Fuel'] = fuel_encoder.fit_transform(X_train['Fuel'])
X_test['Fuel'] = fuel_encoder.transform(X_test['Fuel'])

X_train['Transmission'] = transmission_encoder.fit_transform(X_train['Transmission'])
X_test['Transmission'] = transmission_encoder.transform(X_test['Transmission'])

X_train['Condition'] = condition_encoder.fit_transform(X_train['Condition'])
X_test['Condition'] = condition_encoder.transform(X_test['Condition'])

X_train[['Year of manufacture', 'Mileage', 'Engine Size']] = scaler.fit_transform(X_train[['Year of manufacture', 'Mileage', 'Engine Size']])
X_test[['Year of manufacture', 'Mileage', 'Engine Size']] = scaler.transform(X_test[['Year of manufacture', 'Mileage', 'Engine Size']])

# Save the encoders and scaler
joblib.dump(make_encoder, "make_encoder.joblib",compress=3)
joblib.dump(fuel_encoder, "fuel_encoder.joblib",compress=3)
joblib.dump(transmission_encoder, "transmission_encoder.joblib",compress=3)
joblib.dump(condition_encoder, "condition_encoder.joblib",compress=3)
joblib.dump(scaler, "scaler.joblib",compress=3)

"""#### Needed Model"""

# Initialize the models
rf_model = RandomForestRegressor(random_state=42)
xgb_model = XGBRegressor(random_state=42)
lr_model = LinearRegression()

# Fit the models on the training data
rf_model.fit(X_train, y_train)
xgb_model.fit(X_train, y_train)
lr_model.fit(X_train, y_train)

# Make predictions on the testing data
rf_preds = rf_model.predict(X_test)
xgb_preds = xgb_model.predict(X_test)
lr_preds = lr_model.predict(X_test)

# Evaluate the models using root mean squared error (RMSE)
rf_rmse = mean_squared_error(y_test, rf_preds, squared=False)
xgb_rmse = mean_squared_error(y_test, xgb_preds, squared=False)
lr_rmse = mean_squared_error(y_test, lr_preds, squared=False)

# Print the RMSE scores
print(f"Random Forest RMSE: {rf_rmse:.2f}")
print(f"XGBoost RMSE: {xgb_rmse:.2f}")
print(f"Linear Regression RMSE: {lr_rmse:.2f}")

#  R2 score
rf_r2 = r2_score(y_test, rf_preds)
print("Random Forest R2 Score:", rf_r2)


xgb_r2 = r2_score(y_test, xgb_preds)
print("XGBoost R2 Score:", xgb_r2)


lr_r2 = r2_score(y_test, lr_preds)
print("Linear Regression R2 Score:", lr_r2)

joblib.dump(xgb_model, "car_model.joblib", compress=3)

"""**Note: Many Models have been built, but only the needed ones were kept**"""

sns.histplot(xgb_preds, label='prediction',color='red')
sns.histplot(y_test, label='actual price', color = 'blue')
plt.title('Prediction Vs Actual')
plt.legend()
plt.show()

"""### Prediction"""

import joblib
def predict_car_price(make, year, condition, mileage, engine_size, fuel, transmission):
    # Load the encoders and scaler
    make_encoder = joblib.load("make_encoder.joblib")
    fuel_encoder = joblib.load("fuel_encoder.joblib")
    transmission_encoder = joblib.load("transmission_encoder.joblib")
    condition_encoder = joblib.load("condition_encoder.joblib")
    scaler = joblib.load("scaler.joblib")

    # Preprocess the input
    make_encoded = make_encoder.transform([make])[0]
    numerical_value = scaler.transform([[year,mileage, engine_size]])
    year_scaled = numerical_value[0][0]
    mileage_scaled = numerical_value[0][1]
    engine_size_scaled = numerical_value[0][2]
    fuel_encoded = fuel_encoder.transform([fuel])[0]
    condition_encoded = condition_encoder.transform([condition])[0]
    transmission_encoded = transmission_encoder.transform([transmission])[0]

    input_data = [[make_encoded, year_scaled, condition_encoded, mileage_scaled, engine_size_scaled, fuel_encoded, transmission_encoded]]
    input_df = pd.DataFrame(input_data, columns=['Make', 'Year of manufacture', 'Condition', 'Mileage', 'Engine Size', 'Fuel', 'Transmission'])

    # Make predictions
    predicted_price = xgb_model.predict(input_df)
    return round(predicted_price[0], 2)

predict_car_price('Toyota', 2010,'Nigerian Used', 3000, 2300, 'Petrol', 'Automatic')

"""### Gradio Interface"""

import gradio as gr
import joblib
def predict_car_price(make, year, condition, mileage, engine_size, fuel, transmission):
    # Load the encoders and scaler
    make_encoder = joblib.load("make_encoder.joblib")
    fuel_encoder = joblib.load("fuel_encoder.joblib")
    transmission_encoder = joblib.load("transmission_encoder.joblib")
    condition_encoder = joblib.load("condition_encoder.joblib")
    scaler = joblib.load("scaler.joblib")

    make_encoded = make_encoder.transform([make])[0]
    numerical_value = scaler.transform([[year,mileage, engine_size]])
    year_scaled = numerical_value[0][0]
    mileage_scaled = numerical_value[0][1]
    engine_size_scaled = numerical_value[0][2]
    fuel_encoded = fuel_encoder.transform([fuel])[0]
    condition_encoded = condition_encoder.transform([condition])[0]
    transmission_encoded = transmission_encoder.transform([transmission])[0]
    input_data = [[make_encoded, year_scaled, condition_encoded, mileage_scaled, engine_size_scaled, fuel_encoded, transmission_encoded]]
    input_df = pd.DataFrame(input_data, columns=['Make', 'Year of manufacture', 'Condition', 'Mileage', 'Engine Size', 'Fuel', 'Transmission'])

    # Make predictions
    predicted_price = xgb_model.predict(input_df)
    return round(predicted_price[0], 2)
make_dropdown = gr.inputs.Dropdown(['Acura', 'Audi', 'BMW', 'Chevrolet', 'Dodge', 'Ford', 'Honda',
       'Hyundai', 'Infiniti', 'Kia', 'Land Rover', 'Lexus', 'Mazda',
       'Mercedes-Benz', 'Mitsubishi', 'Nissan', 'Peugeot',
       'Pontiac', 'Toyota', 'Volkswagen', 'Volvo'], label="Make")
condition_dropdown = gr.inputs.Dropdown(['Foreign Used', 'Nigerian Used'], label="Condition")
fuel_dropdown = gr.inputs.Dropdown(["Petrol", "Diesel", "Electric"], label="Fuel")
transmission_dropdown = gr.inputs.Dropdown(["Manual", "Automatic", "AMT"], label="Transmission")
year_slider = gr.inputs.Slider(minimum=1992, maximum=2021, step=1, default=2010, label="Year")
mileage_slider = gr.inputs.Slider(minimum=1, maximum=300000, step=10, default=80000, label="Mileage")
engine_size_slider = gr.inputs.Slider(minimum=1, maximum=20000, step=1, default=100, label="Engine Size")

iface = gr.Interface(
fn=predict_car_price,
inputs=[make_dropdown, year_slider, condition_dropdown, mileage_slider, engine_size_slider, fuel_dropdown, transmission_dropdown],
outputs="number",
title="Car Price Prediction",
    description="Predict the price of a car based on its details, in Naira.",
    examples=[
        ["Toyota", 2010, "Nigerian Used", 80000, 2.0, "Petrol", "Automatic"],
        ["Mercedes-Benz", 2015, "Foreign Used", 50000, 1000, "Diesel", "AMT"],
    ],css=".gradio-container {background-color: lightgreen}"
)

iface.launch(share = True)