# Circuitpython_EPD_AZUREIOTHUB_DEMO

## Buid weather station online demo to show how to use circuitpython EPD and Azure IOT : 2021 BluejazzCHN, written for Adafruit Industries

### Device:
    * EPS32 S2 wrover mcu
    * 1.54 EPD waveshare 1.54
    * External ESP21 wroom airlift wifi with 1.71 nina fireware
### Service:
    * Weather forecast:http://api.caiyunapp.com/  this link use http, not use TLS, please pay an attention.
    * IOT: azure.com  this link us https support TLS meet the requirement of Azure IotHub
### Comment:
    * Connect weather service and IOT service using API, 
      because adafruit_esp32SPI only one TLS connection. 
    * if exceed one you will get OSError 23, so in this demo
      connect weahter service with http, and connect IOT 
      service with https.
### Libs:
    * adafruit_ssd1681 for EPD driver
    * adafruit_esp32spi for adafruit airlift wifi
### secrets.py
    * all the configs stored in secrets.py file
    * secrets schema is belowing:
```Python
      secrets = {
      'ssid' : '###',  #wifi ssid
      'password' : '###',  #wifi pwd
      'device_connection_string' : '###,   #Azure IotHub connection string ,please go to  azure portal copyand paste
      'openweather_location' : 'BeiJing, China', # location string
      'openweather_token' : '###',  # weather data service access token from caiyun api website
      'longitude':'116.601144',  # location longitude
      'latitude':'39.948574',    # location latitude
      'sleep_time':1800,         # deep sleep time in second
      }
 ```
    
