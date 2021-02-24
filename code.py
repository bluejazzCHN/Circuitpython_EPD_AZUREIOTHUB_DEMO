# Circuitpython EPD and Azure IOT : 2021 BluejazzCHN, written for Adafruit Industries

"""
Device:
    EPS32 S2 wrover mcu
    1.54 EPD
    External ESP21 wroom airlift wifi with 1.71 nina fireware
Service:
    Weather forecast:http://api.caiyunapp.com/
    IOT: azure.com
Comment:
    Connect weather service and IOT service using API, because adafruit_esp32SPI only one TLS connection , if exceed one you will get OSError 23
    so in this demo connect weahter service with http, and connect IOT service with https.
"""
import busio
import time
import board
import displayio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import terminalio
from adafruit_display_text import label
import neopixel
import adafruit_ssd1681
from adafruit_ntp import NTP
import random
import json
import alarm
import adafruit_imageload
import adafruit_requests as requests

METRIC = 1

# ------------------------------------------------------------------------------------
# Init drivers: spi wifi using adafruit_esp32spi, spi epd using adafruit_ssd1681
# ------------------------------------------------------------------------------------

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

#Init network interface
esp32_cs = DigitalInOut(board.IO1)
esp32_ready = DigitalInOut(board.IO2)                                                                 
esp32_reset = DigitalInOut(board.IO3)
wifi_spi = busio.SPI(board.IO4, board.IO5, board.IO6)
esp = adafruit_esp32spi.ESP_SPIcontrol(wifi_spi, esp32_cs, esp32_ready, esp32_reset)
if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")

#init status led
status_light = neopixel.NeoPixel(
    board.NEOPIXEL, 1, brightness=0.2
)

#init WIFI
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
print("Connecting to WiFi...")

wifi.connect()
print("Connected to WiFi!")

displayio.release_displays()

# This pinout works on a Feather M4 and may need to be altered for other boards.
epd_cs = board.IO36
epd_dc = board.IO37
epd_reset = board.IO38
epd_busy = board.IO39

epd_spi = busio.SPI(board.IO33, MOSI=board.IO34, MISO=board.IO35)

display_bus = displayio.FourWire(
    epd_spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
)
time.sleep(1)

display = adafruit_ssd1681.SSD1681(
    display_bus,
    width=200,
    height=200,
    busy_pin=epd_busy,
    highlight_color=0xFF0000,
    rotation=180,
)
display.rotation =1

# Init NTP for Auzre IOT
print("Getting the time...")

ntp = NTP(esp)
# Wait for a valid time to be received
while not ntp.valid_time:
    time.sleep(5)
    ntp.set_time()

print("Time:", str(time.time()))

#Define the main screen display IO group
g = displayio.Group(max_size=10,scale=1)





# ----------------------------
# Define various assets
# ----------------------------
BACKGROUND_BMP = "/bmps/weather_bg.bmp"
ICONS_LARGE_FILE = "/bmps/weather_icons_70px.bmp"
ICONS_SMALL_FILE = "/bmps/weather_icons_20px.bmp"
ICON_MAP = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
#skycon dict 
icon_dict = {
    'CLEAR_DAY':'01',
    'PARTLY_CLOUDY_DAY':'02',
    'CLOUDY':'03',
    '':'04',
    '':'09',
    'LIGHT_RAIN':'10',
    'MODERATE_RAIN':'10',
    'HEAVY_RAIN':'10',
    'STORM_RAIN':'11',
    'LIGHT_SNOW':'13',
    'MODERATE_SNOW':'13',
    'HEAVY_SNOW':'13',
    'STORM_SNOW':'13',
    'LIGHT_HAZE':'50',
    'MODERATE_HAZE':'50',
    'HEAVY_HAZE':'50',
}
 
def get_data_source_url(api="onecall", location=None):
    """Build and return the URL for the OpenWeather API."""
    if api.upper() == "FORECAST5":
        URL = "https://api.openweathermap.org/data/2.5/forecast?"
        URL += "q=" + location
    elif api.upper() == "ONECALL":
        URL = "https://api.openweathermap.org/data/2.5/onecall?exclude=minutely,hourly,alerts"
        URL += "&lat={}".format(location[0])
        URL += "&lon={}".format(location[1])
    else:
        raise ValueError("Unknown API type: " + api)
 
    return URL + "&appid=" + secrets["openweather_token"]
 
def get_latlon():
    """Use the Caiyun API to determine lat/lon for given city."""
    JSON_URL_1 = "http://api.caiyunapp.com/v2.5/{}/{},{}/daily.json".format(secrets["openweather_token"],secrets["longitude"],secrets["latitude"])
    JSON_URL_2 = "http://api.caiyunapp.com/v2.5/{}/{},{}/realtime.json".format(secrets["openweather_token"],secrets["longitude"],secrets["latitude"])

    # requests.set_socket(socket, esp)
    # esp._debug = True
    r1 = wifi.get(JSON_URL_1)
    r1_data = r1.json()
    r1.close()
    r2 = wifi.get(JSON_URL_2)
    r2_data = r2.json()
    r2.close()

    return r1_data,r2_data

 
def get_forecast(location):
    """Use OneCall API to fetch forecast and timezone data."""
    resp = magtag.network.fetch(get_data_source_url(api="onecall", location=location))
    json_data = resp.json()
    return json_data["daily"], json_data["current"]["dt"], json_data["timezone_offset"]
 
 
def make_banner(x=0, y=0):
    """Make a single future forecast info banner group."""
    day_of_week = label.Label(terminalio.FONT, text="DAY", color=0x000000)
    day_of_week.anchor_point = (0, 0.5)
    day_of_week.anchored_position = (0, 10)
 
    icon = displayio.TileGrid(
        icons_small_bmp,
        pixel_shader=icons_small_pal,
        x=25,
        y=0,
        width=1,
        height=1,
        tile_width=20,
        tile_height=20,
    )
 
    day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
    day_temp.anchor_point = (0, 0.5)
    day_temp.anchored_position = (50, 10)
 
    group = displayio.Group(max_size=3, x=x, y=y)
    group.append(day_of_week)
    group.append(icon)
    group.append(day_temp)
 
    return group
 
 
def temperature_text(tempK):
    if METRIC:
        # return "{:3.0f}C".format(tempK - 273.15)
        return "{:3.0f}C".format(tempK)
    else:
        return "{:3.0f}F".format(32.0 + 1.8 * (tempK - 273.15))
 
 
def wind_text(speedms):
    if METRIC:
        return "{:3.0f}m/s".format(speedms)
    else:
        return "{:3.0f}mph".format(2.23694 * speedms)
 
 
def update_banner(banner, data):
    """Update supplied forecast banner with supplied data."""
    banner[0].text = DAYS[time.localtime(data["dt"]).tm_wday][:3].upper()
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = temperature_text(data["temp"]["day"])
 
 
def update_today(data, realtime,tz_offset=0):
    """Update today info banner."""
    date = time.localtime(data["server_time"]+tz_offset)
    # sunrise = time.localtime(data["sunrise"] + tz_offset)
    # sunset = time.localtime(data["sunset"] + tz_offset)
    today_date.text = "{} {} {}, {}".format(
        DAYS[date.tm_wday].upper(),
        MONTHS[date.tm_mon - 1].upper(),
        date.tm_mday,
        date.tm_year,
    )

    print(icon_dict[data["result"]["daily"]["skycon"][0]["value"]])
    today_icon[0] = ICON_MAP.index(icon_dict[data["result"]["daily"]["skycon"][0]["value"]])
    today_morn_temp.text = temperature_text(data["result"]["daily"]["temperature"][0]["min"])
    today_day_temp.text = temperature_text(realtime["result"]["realtime"]["temperature"])
    today_night_temp.text = temperature_text(data["result"]["daily"]["temperature"][0]["max"])
    today_humidity.text = "{:3d}%".format(int(realtime["result"]["realtime"]["humidity"]*100))
    today_wind.text = wind_text(realtime["result"]["realtime"]["wind"]["speed"])
    today_sunrise.text = "{} AM".format(str(data["result"]["daily"]["astro"][0]["sunrise"]["time"]))
    today_sunset.text = "{} PM".format(str(data["result"]["daily"]["astro"][0]["sunset"]["time"]))
    today_airq.text = "AQI: {}".format(str(realtime["result"]["realtime"]["air_quality"]["aqi"]["chn"]))

# ----------------------------
# Weather icons sprite sheet
# ----------------------------
icons_large_bmp, icons_large_pal = adafruit_imageload.load(ICONS_LARGE_FILE)
icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)

# ===========
# U I
# ===========


 #build today background
f = open(BACKGROUND_BMP, "rb")
pic = displayio.OnDiskBitmap(f)
today_backgroud = displayio.TileGrid(pic, pixel_shader=displayio.ColorConverter())
g.append(today_backgroud)

#build today_elements
today_date = label.Label(terminalio.FONT, text="*"*30,color=0x000000)
today_date.anchor_point = (0, 0)
today_date.anchored_position = (15, 13)
 
city_name = label.Label(
    terminalio.FONT, text=secrets["openweather_location"], color=0x000000
)
city_name.anchor_point = (0, 0)
city_name.anchored_position = (15, 24)
 
today_icon = displayio.TileGrid(
    icons_large_bmp,
    pixel_shader=icons_small_pal,
    x=10,
    y=39,
    width=1,
    height=1,
    tile_width=70,
    tile_height=70,
)
 
today_morn_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_morn_temp.anchor_point = (0.5, 0)
today_morn_temp.anchored_position = (118, 59)
 
today_day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_day_temp.anchor_point = (0.5, 0)
today_day_temp.anchored_position = (149, 59)
 
today_night_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_night_temp.anchor_point = (0.5, 0)
today_night_temp.anchored_position = (180, 59)
 
today_humidity = label.Label(terminalio.FONT, text="100%", color=0x000000)
today_humidity.anchor_point = (0, 0.5)
today_humidity.anchored_position = (105, 95)
 
today_wind = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
today_wind.anchor_point = (0, 0.5)
today_wind.anchored_position = (155, 95)
 
today_sunrise = label.Label(terminalio.FONT, text="6:12 AM", color=0x000000)
today_sunrise.anchor_point = (0, 0.5)
today_sunrise.anchored_position = (45, 117)
 
today_sunset = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
today_sunset.anchor_point = (0, 0.5)
today_sunset.anchored_position = (130, 117)

today_airq = label.Label(terminalio.FONT, text="AQI: 49.5", color=0x000000)
today_airq.anchor_point = (0.5, 0)
today_airq.anchored_position = (45, 95)
 
today_banner = displayio.Group(max_size=12)
today_banner.append(today_date)
today_banner.append(city_name)
today_banner.append(today_icon)
today_banner.append(today_morn_temp)
today_banner.append(today_day_temp)
today_banner.append(today_night_temp)
today_banner.append(today_humidity)
today_banner.append(today_wind)
today_banner.append(today_sunrise)
today_banner.append(today_sunset)
today_banner.append(today_airq)
 
future_banners = [
    make_banner(x=210, y=18),
    make_banner(x=210, y=39),
    make_banner(x=210, y=60),
    make_banner(x=210, y=81),
    make_banner(x=210, y=102),
]
 
g.append(today_banner)
for future_banner in future_banners:
    g.append(future_banner)

status_light[0] = (50, 50, 50)

#Get the weather data and update today 
print("Getting oneline weather data...")
daily,realtime = get_latlon()
update_today(daily,realtime,28800)

display.show(g)
display.refresh()
status_light[0] = (0, 0, 0)

# ----------------------------
# Azure IOT Hub 
# ----------------------------
from adafruit_azureiot import IoTHubDevice  # pylint: disable=wrong-import-position
# Create an IoT Hub device client and connect
device = IoTHubDevice(socket, esp, secrets["device_connection_string"])

# # Subscribe to cloud to device messages
# # To send a message to the device, select it in the Azure Portal, select Message To Device,
# # fill in the message and any properties you want to add, then select Send Message
def cloud_to_device_message_received(body: str, properties: dict):
    print("Received message with body", body, "and properties", json.dumps(properties))

# Subscribe to the cloud to device message received events
device.on_cloud_to_device_message_received = cloud_to_device_message_received
print("Connecting to Azure IoT Hub...")

# Connect to IoT Central
device.connect()
print("Connected to Azure IoT Hub!")

# send device data to Azure IOT Hub once every wake
try:
    # Send a device to cloud message every minute
    # You can see the overview of messages sent from the device in the Overview tab
    # of the IoT Hub in the Azure Portal
    message = {"Temperature": today_day_temp.text}
    device.send_device_to_cloud_message(json.dumps(message))
    print("Sent data to IOTHub")
    device.loop()
except (ValueError, RuntimeError) as e:
    print("Connection error, reconnecting\n", str(e))
    # If we lose connectivity, reset the wifi and reconnect
    esp_wifi.reset()
    esp_wifi.connect()
    device.reconnect()


#enable deep sleep , sleep time is set by secrets
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + secrets['sleep_time'])

alarm.exit_and_deep_sleep_until_alarms(time_alarm)