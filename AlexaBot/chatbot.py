import pywhatkit as pwk # general use
import random as rd # random number generator
import wikipedia as wiki # search wikipedia
import pyjokes as pj # generate random jokes
import pyttsx3 # text to speech, use pyttsx3 version 2.91 since latest version is broken.
import requests # make API requests
import os
from dotenv import load_dotenvg
from datetime import datetime

########################################
#   List of key features implemented   #
#                                      #
#   [/] Search the web                 #
#   [/] Text to speech                 #
#   [/] Search Wikipedia               #
#   [/] Random number generator        #
#   [/] Get weather                    #
#   [/] Get time                       #
#   [/] Play music                     #
#   [/] Tell a joke                    #
#   [/] Get date                       #
#                                      #
########################################

# load API keys
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TIMEZONE_API_KEY = os.getenv("TIMEZONE_API_KEY")
BASE_URL = "http://api.weatherapi.com/v1/current.json"

# filler words to ignore
filler_words = ["what", "is", "the", "in", "for", "like", "today", "at", "please", "now", "time", "date", "weather", "alexa", "it"]


# Initialize text-to-speech engine
engine = pyttsx3.init()

# Voice mode
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# method to call text to speech
# accepts strings
def speak(text):
    engine.say(text)
    engine.runAndWait()

# requests location from user ip without taking it.
def get_location_from_ip():
    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    return data.get("city")

# command to get the current weather of a given city, 
# or the weather today in user's location
def get_weather(city):
    if "today" in city:
        query = get_location_from_ip() # use ip for location detection
    else:
        query = city

    params = {
        "key": WEATHER_API_KEY,
        "q": query,
        "aqi": "no"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    #print(data) # debug

    if "error" in data:
        return "I could not find the weather for that location."
    
    location = data["location"]["name"]
    country = data["location"]["country"]
    temp_c = data["current"]["temp_c"]
    condition = data["current"]["condition"]["text"]
    
    return f"The weather in {location}, {country} is {condition} with {temp_c}°C."

def get_time(place_name):
    try:
        place_name = place_name.strip()
        print(f"Getting time for: {place_name}")

        #Get coordinates
        geo_url = f"https://geocode.maps.co/search?q={place_name}"
        geo_response = requests.get(geo_url, timeout=10)
        geo_data = geo_response.json()

        if not geo_data:
            parts = place_name.split()
            if len(parts) > 1:
                retry_name_time = parts[-1]
                #print(f"Retrying with simpler name: {retry_name_time}") # debug
                geo_response = requests.get(f"https://geocode.maps.co/search?q={retry_name_time}", timeout=10)
                geo_data = geo_response.json()

        if not geo_data:
            print("Place not found.")
            speak("I could not find that place.")
            return

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Get timezone and current time
        tz_url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={TIMEZONE_API_KEY}&format=json&by=position&lat={lat}&lng={lon}"
        tz_response = requests.get(tz_url, timeout=10)
        tz_data = tz_response.json()

        if tz_data.get("status") != "OK":
            print("Could not get time data.")
            speak("I could not get the time for that place.")
            return

        time_str_24 = tz_data["formatted"]
        time_obj = datetime.strptime(time_str_24, "%Y-%m-%d %H:%M:%S")
        time_str_12 = time_obj.strftime("%I:%M %p")
        print(f"The current time in {place_name} is {time_str_12}")
        speak(f"The current time in {place_name} is {time_str_12}")

    except Exception as e:
        print("Error getting time:", e)
        speak("I could not get the time right now.")

def get_date(place_name):
    place_name = place_name.strip()
    try:
        print(f"Getting date for: {place_name}")

        # Get coordinates
        geo_url = f"https://geocode.maps.co/search?q={place_name}"
        geo_response = requests.get(geo_url, timeout=10)
        geo_data = geo_response.json()

        if not geo_data:
            parts = place_name.split()
            if len(parts) > 1:
                retry_name_date = parts[-1]
                # print(f"Retrying with simpler name: {retry_name_date}") debug
                geo_response = requests.get(f"https://geocode.maps.co/search?q={retry_name_date}", timeout=10)
                geo_data = geo_response.json()

        if not geo_data:
            print("Place not found.")
            speak("I could not find that place.")
            return

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Get date data using TimeZoneDB API
        tz_url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={TIMEZONE_API_KEY}&format=json&by=position&lat={lat}&lng={lon}"
        tz_response = requests.get(tz_url, timeout=10)
        tz_data = tz_response.json()

        if tz_data.get("status") != "OK":
            print("Could not get date data.")
            speak("I could not get the date for that place.")
            return

        # Extract and format date
        date_str = tz_data["formatted"].split(" ")[0]  # YYYY-MM-DD
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y") # MM-DD-YYYY

        print(f"The current date in {place_name} is {formatted_date}")
        speak(f"The current date in {place_name} is {formatted_date}")

    except Exception as e:
        print("Error getting date:", e)
        speak("I could not get the date right now.")
    
    
# main call for Alexa
def run_alexa(user_input):
    try:
        # Make the input lowercase to reduce cases to deal with.
        user_input = user_input.lower()

        # Do not continue if user input does not start with keyword "alexa"
        if not user_input.startswith("alexa"):
            print("Sorry, I couldn't quite catch that.")
            speak("Sorry, I couldn't quite catch that.")
            return

        # if keyword "play" found in user input, 
        # then play the first video recommended in youtube feed.
        if "play" in user_input:
            song = user_input.replace("alexa", "").replace("play", "").strip()
            print('Playing '+ song)
            speak('Now playing '+ song)
            pwk.playonyt(user_input)

        # Get time by API request
        elif "time" in user_input:
            words = user_input.strip().split()
            place = None

            # reconstruct place name from user input
            for i, word in enumerate(words):
                if word.lower() not in filler_words:
                    place = " ".join(words[i:])
                    break
            if place:
                get_time(place)
            else:
                now = datetime.now()
                time_str = now.strftime("%I:%M %p")
                print(f"The current time is {time_str}")
                speak(f"The current time is {time_str}")
        
        elif "date" in user_input:
            words = user_input.strip().split()
            place = None

            for i, word in enumerate(words):
                if word.lower() not in filler_words:
                    place = " ".join(words[i:])
                    break
            if place:
                get_date(place)
            else:
                now = datetime.now()
                date_str = now.strftime("%B %d, %Y")
                print(f"Today's date is {date_str}")
                speak(f"Today's date is {date_str}")

        elif "weather" in user_input:
            # Remove "alexa" and "weather" from the sentence
            #command = user_input.replace("alexa", "").replace("weather", "").strip()

            # Split words and rebuild only the useful parts
            words = user_input.strip().split()
            city = None

            for i, word in enumerate(words):
                if word.lower() not in filler_words:
                    city = " ".join(words[i:])
                    break

            # If user only said "weather" or gave no city, use IP location
            if not city:
                city = "today"

            result = get_weather(city)
            print(result)
            speak(result)

        elif any(keyword in user_input for keyword in ["what", "who", "when"]):
            # Extract the query after the keyword
            for keyword in ["who", "what", "when"]:
                if keyword in user_input:
                    query_location = user_input.find(keyword) + len(keyword)
                    query = user_input[query_location:].strip()
                    break

            try:
                summary = wiki.summary(query, sentences=3)
                print(summary)
                speak(summary)
            except wiki.DisambiguationError as e:
                print("That topic is ambiguous. Searching Google instead.")
                speak("That topic is ambiguous. Searching Google instead.")
                pwk.search(query)
            except wiki.PageError:
                print("Topic not found on Wikipedia. Searching Google instead.")
                speak("Topic not found on Wikipedia. Searching Google instead.")
                pwk.search(query)

        elif "search" in user_input:
            query = user_input.strip().replace("alexa","").replace("search","")
            try:
                pwk.search(query)
            except:
                print("Search failed.")
                speak("Search failed.")

        elif "joke" in user_input:
            joke = pj.get_joke()
            print(joke)
            speak(joke)

        elif "help" in user_input:
            print("Here are the available commands: search, play, who, when, what, joke, date, weather, time, random")
            speak("Here are the available commands: search, play, who, when, what, joke, date, weather, time, random")

        elif "random" in user_input and "number" in user_input:
            if "between" or "from" in user_input:
                parts = user_input.split()
                try:
                    # find the numbers after the word "between" or "from"
                    i = parts.index("between") if "between" in parts else parts.index("from")
                    num1 = int(parts[i + 1])
                    num2 = int(parts[i + 3]) if parts[i + 2] in ["and", "to"] else int(parts[i + 2])
                    if num1 > num2:
                        num1, num2 = num2, num1
                    number = rd.randint(num1, num2)
                    print(f"Your random number {parts[i]} {num1} {parts[i+2]} {num2} is: {number}")
                    speak(f"Your random number {parts[i]} {num1} {parts[i+2]} {num2} is: {number}")
                    return
                except (ValueError, IndexError):
                    print("Could not parse the range. Generating a number between 0 and 100 instead.")
                    speak("Could not parse the range. Generating a number between 0 and 100 instead.")
            # fallback to default
            number = rd.randint(0, 100) # generate random number between 0 and 100
            print(f"Your random number is: {number}")
            speak(f"Your random number is: {number}")
        
        # Terminate program
        elif "shutdown" or "quit" or "exit" in user_input:
            speak("See you next time!")
            quit()

        # Fallback
        else:
            speak("Sorry, I couldn't quite catch that.")
            print("Sorry, I couldn't quite catch that.")

    except:
        print(f"Sorry, I couldn't quite catch that.")
        speak("Sorry, I couldn't quite catch that.")

def main():
    speak("Hi, I am Alexa your personal ChatBot! How can I help you today?")
    while True:
        user_input = input("Hi! I'm Alexa, your Chatbot assistant. Type a command starting with Alexa.\n")
        run_alexa(user_input)
        
main()