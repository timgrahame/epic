import json
import datetime
import requests
import io
from urllib.request import urlopen
import time
import os
os.environ["SDL_AUDIODRIVER"] = "dsp"
import pygame
pygame.init()

os.environ["DISPLAY"] = ":0"

pygame.display.init()

# Fix for "XDG_RUNTIME_DIR not set" error
if "XDG_RUNTIME_DIR" not in os.environ:
    os.environ["XDG_RUNTIME_DIR"] = "/tmp"

# Settings
check_delay = 120  # minutes
rotate_delay = 20  # seconds

# Set up the drawing window
screen = pygame.display.set_mode([480, 480], pygame.FULLSCREEN)
pygame.mouse.set_visible(0)

# Fill the background with black
screen.fill((0, 0, 0))

# Display loading image
image = pygame.image.load(r"./loading.jpg")
screen.blit(image, (0, 0))
pygame.display.flip()

print("Checking for new photos every " + str(check_delay) + " minutes")
print("Rotating photos every " + str(rotate_delay) + " seconds")

# Initialize font
font = pygame.font.Font(None, 50)  # Default font, size 36
clock_color = (255, 255, 255)  # White color for text

# Global variables for weather caching
weather_last_updated = None
weather_icon = None
weather_temp = None


# Function to render text with an outline
def render_text_with_outline(font, text, text_color, outline_color):
    base_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)
    text_width, text_height = base_surface.get_size()
    outline_surface_with_padding = pygame.Surface(
        (text_width + 2, text_height + 2), pygame.SRCALPHA
    )
    offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for offset in offsets:
        outline_surface_with_padding.blit(outline_surface, (1 + offset[0], 1 + offset[1]))
    outline_surface_with_padding.blit(base_surface, (1, 1))
    return outline_surface_with_padding


# Fetch weather data with caching
def fetch_and_cache_weather(api_key, location, refresh_interval=5):
    global weather_last_updated, weather_icon, weather_temp
    now = datetime.datetime.now()

    # Check if it's time to refresh the weather data
    if not weather_last_updated or (now - weather_last_updated).total_seconds() > refresh_interval * 60:
        print("Fetching updated weather data...")
        icon_code, temp = fetch_weather_data(api_key, location)
        if icon_code:
            weather_icon = download_weather_icon(icon_code)
            weather_temp = temp
            weather_last_updated = now  # Update the last fetch time
        else:
            print("Failed to fetch weather data.")


# Fetch weather data from OpenWeatherMap
def fetch_weather_data(api_key, location="Boston,UK"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)  # Set a timeout
        response.raise_for_status()
        data = response.json()
        icon_code = data["weather"][0]["icon"]
        temp = data["main"]["temp"]
        return icon_code, temp
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None, None  # Return None instead of crashin

# Download weather icon from OpenWeatherMap
def download_weather_icon(icon_code):
    try:
        url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        icon_file = io.BytesIO(response.content)
        return pygame.image.load(icon_file)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading weather icon: {e}")
        return None  # Return None instead of crashing

# Create image URLs from EPIC data
def create_image_urls(photos):
    urls = []
    for photo in photos:
        dt = datetime.datetime.strptime(photo["date"], "%Y-%m-%d %H:%M:%S")
        imageurl = f"https://epic.gsfc.nasa.gov/archive/natural/{dt.year}/{str(dt.month).zfill(2)}/{str(dt.day).zfill(2)}/jpg/{photo['image']}.jpg"
        urls.append(imageurl)
    return urls

# fetch epic data():
def fetch_epic_data():
    url = "https://epic.gsfc.nasa.gov/api/natural"
    max_retries = 3
    backoff_factor = 2  # Exponential backoff (2, 4, 8 seconds)

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            json_data = response.json()
            return json_data

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to NASA EPIC API: {e}")
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Unable to fetch EPIC data.")
                return None


# Save images locally
def save_photos(imageurls):
    print("Saving photos")
    counter = 0
    for imageurl in imageurls:
        image_file = io.BytesIO(urlopen(imageurl).read())
        image = pygame.image.load(image_file)
        cropped = pygame.Surface((900, 900))
        cropped.blit(image, (-30, -30), (55, 55, 2000, 2000))
        cropped = pygame.transform.scale(cropped, (480, 480))
        pygame.image.save(cropped, f"./{counter}.jpg")
        counter += 1
    print("Photos saved")


# Rotate and display photos with date, time, and weather
def rotate_photos(num_photos, rotate_delay, api_key, location):
    counter = 0

    # Ensure weather data is up-to-date
    fetch_and_cache_weather(api_key, location, refresh_interval=15)

    while counter < num_photos:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        image = pygame.image.load(r"./" + str(counter) + ".jpg")
        screen.blit(image, (0, 0))

        current_time = datetime.datetime.now().strftime("%H:%M")
        current_date = datetime.datetime.now().strftime("%d %B %Y")

        date_surface = render_text_with_outline(font, current_date, text_color=clock_color, outline_color=(0, 0, 0))
        clock_surface = render_text_with_outline(font, current_time, text_color=clock_color, outline_color=(0, 0, 0))
        temp_surface = None
        if weather_temp is not None:
            temp_surface = render_text_with_outline(font, f"{weather_temp}°C", text_color=clock_color, outline_color=(0, 0, 0))

        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2

        if weather_icon:
            icon_x = screen_center_x - weather_icon.get_width() // 2
            icon_y = screen_center_y - weather_icon.get_height() - 160
            screen.blit(weather_icon, (icon_x, icon_y))
        
        if temp_surface:
            temp_x = screen_center_x - temp_surface.get_width() // 2
            temp_y = icon_y + weather_icon.get_height() - 15
            screen.blit(temp_surface, (temp_x, temp_y))

        date_x = screen_center_x - date_surface.get_width() // 2
        date_y = temp_y + temp_surface.get_height() + 280
        clock_x = screen_center_x - clock_surface.get_width() // 2
        clock_y = date_y + date_surface.get_height() + 10

        screen.blit(date_surface, (date_x, date_y))
        screen.blit(clock_surface, (clock_x, clock_y))

        pygame.display.flip()
        counter += 1
        time.sleep(rotate_delay)


# Main loop
running = True
first_run = True
last_data = ""
newest_data = ""
last_check = datetime.datetime.now() - datetime.timedelta(hours=1)
num_photos = 0

api_key = "<your key>"  # Replace with your API key
location = "Boston,UK"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

    if last_check < datetime.datetime.now() - datetime.timedelta(minutes=check_delay) or first_run:
        print(f"{datetime.datetime.now()} Checking for new images.")
        last_check = datetime.datetime.now()
        json_data = fetch_epic_data()
        if json_data:
            newest_data = json_data[0]["date"]
        else:
            newest_data = None  # Handle gracefully        
        if last_data != newest_data:
            print("New images found!")
            last_data = newest_data
            imageurls = create_image_urls(json_data)
            save_photos(imageurls)
            num_photos = len(imageurls)
            rotate_photos(num_photos, 1, api_key, location)
        else:
            print("No new images.")

    rotate_photos(num_photos, rotate_delay, api_key, location)

pygame.quit()
