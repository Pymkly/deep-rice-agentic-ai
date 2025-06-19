import openmeteo_requests

import pandas as pd
import requests_cache
from dotenv import load_dotenv
from retry_requests import retry

load_dotenv()


class OpenMeteo:
	def __init__(self):
		self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
		self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
		self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
		self.url = "https://api.open-meteo.com/v1/forecast"

	def get_temperature(self, longitude, latitude):
		params = ['date', 'temperature_2m', 'apparent_temperature']
		return self.extract_info(longitude, latitude, params)

	def get_rain(self, longitude, latitude):
		params = ['date', 'rain', 'precipitation_probability']
		return self.extract_info(longitude, latitude, params)

	def get_soil_info(self, longitude, latitude):
		params = ['date', 'soil_temperature_0cm', 'soil_moisture_1_to_3cm']
		return self.extract_info(longitude, latitude, params)

	def get_visibility(self, longitude, latitude):
		params = ['date', 'cloud_cover', 'visibility']
		return self.extract_info(longitude, latitude, params)

	def extract_info(self, longitude, latitude, params):
		info = self.get_info(latitude, longitude)
		return info[params].to_markdown(index=False)

	def get_info(self, longitude, latitude):
		response = self.call_api(longitude, latitude)
		hourly = response.Hourly()
		hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
		hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
		hourly_rain = hourly.Variables(2).ValuesAsNumpy()
		hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
		hourly_soil_temperature_0cm = hourly.Variables(4).ValuesAsNumpy()
		hourly_soil_moisture_1_to_3cm = hourly.Variables(5).ValuesAsNumpy()
		hourly_cloud_cover = hourly.Variables(6).ValuesAsNumpy()
		hourly_visibility = hourly.Variables(7).ValuesAsNumpy()
		hourly_data = {"date": pd.date_range(
			start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
			end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = hourly.Interval()),
			inclusive = "left"
		)}
		hourly_data["temperature_2m"] = hourly_temperature_2m
		hourly_data["apparent_temperature"] = hourly_apparent_temperature
		hourly_data["rain"] = hourly_rain
		hourly_data["precipitation_probability"] = hourly_precipitation_probability
		hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
		hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm
		hourly_data["cloud_cover"] = hourly_cloud_cover
		hourly_data["visibility"] = hourly_visibility
		hourly_dataframe = pd.DataFrame(data = hourly_data)
		return hourly_dataframe

	def call_api(self, longitude, latitude):
		params = {
			"latitude": latitude,
			"longitude": longitude,
			"hourly": ["temperature_2m", "apparent_temperature", "rain", "precipitation_probability",
					   "soil_temperature_0cm", "soil_moisture_1_to_3cm", "cloud_cover", "visibility"]
		}
		responses = self.openmeteo.weather_api(self.url, params=params)
		response = responses[0]
		return response

