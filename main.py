import os
import requests
from dotenv import load_dotenv


class WeatherReport:
    """A class to store and format weather information retrieved from the API."""

    def __init__(self, city, country, temp, feels_like, humidity, description, wind_speed):
        self.city = city
        self.country = country
        self.temp = temp
        self.feels_like = feels_like
        self.humidity = humidity
        self.description = description
        self.wind_speed = wind_speed

    @classmethod
    def from_api_json(cls, data):
        """Factory method to extract relevant fields from the raw JSON response."""
        return cls(
            city=data.get("name", "Unknown"),
            country=data.get("sys", {}).get("country", ""),
            temp=data.get("main", {}).get("temp", 0.0),
            feels_like=data.get("main", {}).get("feels_like", 0.0),
            humidity=data.get("main", {}).get("humidity", 0),
            description=data.get("weather", [{}])[0].get("description", "N/A"),
            wind_speed=data.get("wind", {}).get("speed", 0.0),
        )

    def display(self):
        """Prints a clean and formatted weather summary."""
        print("\n" + "=" * 45)
        print(f"       WEATHER REPORT: {self.city.upper()}, {self.country}")
        print("=" * 45)
        print(f" Condition   : {self.description.capitalize()}")
        print(f" Temperature : {self.temp:.1f} °C")
        print(f" Feels Like  : {self.feels_like:.1f} °C")
        print(f" Humidity    : {self.humidity}%")
        print(f" Wind Speed  : {self.wind_speed} m/s")
        print("=" * 45 + "\n")


def fetch_weather(city_name: str, api_key: str) -> WeatherReport:
    """Calls the OpenWeatherMap API and returns a WeatherReport object."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",  # Retrieve temperature in Celsius
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        # Handle specific HTTP error status codes
        if response.status_code == 401:
            print("Error: Invalid or unactivated API Key (401 Unauthorized).")
            print("Note: New OpenWeatherMap keys may take 10 to 30 minutes to activate.")
            return None
        elif response.status_code == 404:
            print(f"Error: City '{city_name}' not found (404 Not Found).")
            return None
        elif response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}: {response.text}")
            return None

        # Parse JSON response
        data = response.json()
        return WeatherReport.from_api_json(data)

    except requests.exceptions.ConnectionError:
        print("Network Error: Could not connect to the API. Check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        print("Timeout Error: The request took too long to complete.")
        return None
    except requests.exceptions.RequestException as error:
        print(f"An unexpected request error occurred: {error}")
        return None


def main():
    # Load environment variables from the .env file
    load_dotenv()

    # Read the API key from the environment
    api_key = os.getenv("OPENWEATHER_API_KEY")

    # Validate that the API key exists and is not the default placeholder
    if not api_key or api_key.strip() == "your_api_key_here":
        print("Configuration Error: Missing API key.")
        print("Please open the '.env' file and set 'OPENWEATHER_API_KEY' with your valid key.")
        return

    print("--- OpenWeatherMap API Client ---")
    user_city = input("Enter city name (press Enter for default 'Cairo'): ").strip()
    if not user_city:
        user_city = "Cairo"

    print(f"Fetching current weather for '{user_city}'...")
    weather_report = fetch_weather(user_city, api_key)

    if weather_report:
        weather_report.display()


if __name__ == "__main__":
    main()

