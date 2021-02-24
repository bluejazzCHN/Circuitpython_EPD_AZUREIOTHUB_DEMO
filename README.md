# Circuitpython_EPD_AZUREIOTHUB_DEMO

## Buid weather station online demo to show how to use circuitpython EPD and Azure IOT : 2021 BluejazzCHN, written for Adafruit Industries

### Device:
    * EPS32 S2 wrover mcu
    * 1.54 EPD waveshare 1.54
    * External ESP21 wroom airlift wifi with 1.71 nina fireware
### Service:
    * Weather forecast:http://api.caiyunapp.com/
    * IOT: azure.com
### Comment:
    * Connect weather service and IOT service using API, because adafruit_esp32SPI only one TLS connection. 
    * if exceed one you will get OSError 23, so in this demo connect weahter service with http, and connect IOT service with https.
### Lib:
    * adafruit_ssd1681 for EPD driver
    * adafruit_esp32spi for adafruit airelift wifi
