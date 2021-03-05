# encoding: utf-8
"""
Text to Speech use open API: Text to Audio Converter Zalo AI
Document: https://zalo.ai/docs/api/text-to-audio-converter
Author: exlab247
Version 1.0 - Date Dec 12, 2020
---
Config in configuration.yaml file for Home Assistant
tts_zalo:
  api_key: 'your_api_key'
  url: 'https://your_domain.duckdns.org' or 'http://192.168.1.100:8123'

Code in automation
- alias: Example text2speech by zalo_api
  trigger:
    platform: state
    entity_id: switch.light
    to: 'on'
  action:
    service: tts_zalo.say
    data:
      entity_id: media_player.room_player
      message: 'Đèn vừa được bật sáng.'
      voice: 2 # Voices list: {1: Giọng nữ miền Nam, 2: Giọng nữ miền Bắc, 3: Giọng nam miền Nam, 4: Giọng nam miền Bắc}
      speed: 1 # speed: float value inside range [0.8, 1.2], larger is faster.
---
"""

import requests, json, os, time
import logging

SERVICE_NAME = 'tts_zalo'

audio_filename = 'tts_zalo.mp3'


_LOGGER = logging.getLogger(__name__)

def limit_message_size(message):
    zalo_character_limit = 1980
    index                = message.find(" ", zalo_character_limit)
    message              = message[0:index].strip()
    return message

def zalo_tts(api_key, speed, voice, message, audio_path):
    api_url        = 'https://api.zalo.ai/v1/tts/synthesize'
    api_key_header = {'apikey': str(api_key)}
    data_payload   = {'input': limit_message_size(message), 'speed': str(speed), 'encode_type': '1','speaker_id': str(voice)}
    content        = None
    wait_duration  = 0.5
    retries        = 20
    try:
        current_retry = 0
        data_url      = requests.post(api_url, data = data_payload, headers = api_key_header).json()['data']['url']
        get_request   = requests.get(data_url)
        status        = get_request.status_code

        while (status != 200 and current_retry < retries):
            time.sleep(wait_duration)
            get_request = requests.get(data_url)
            status      = get_request.status_code
            current_retry += 1
        if current_retry == retries:
            return False
        content = get_request.content
    except:
       return False

    with open(audio_path, "wb") as filehandler:
        filehandler.write(content)

    return True

def setup(hass, config):
    config_path = hass.config.path()
    tts_path    = os.path.join(config_path, "www/zalo_tts")

    if os.path.exists(tts_path) == False:
        os.makedirs(tts_path)
    audio_path = os.path.join(tts_path, audio_filename)

    def tts(data_call):
        api_key         = config[SERVICE_NAME]["api_key"]
        ha_external_url = config[SERVICE_NAME]["url"]
        voice     = data_call.data.get("voice")
        speed     = data_call.data.get("speed")
        entity_id = data_call.data.get("entity_id")
        message   = data_call.data.get("message")
        result = zalo_tts(api_key, speed, voice, message, audio_path)

        if result == False:
            _LOGGER.error("The request timed out or something went wrong!")
            return False

        ha_external_url = ha_external_url.strip()
        last_char       = ha_external_url[len(ha_external_url) - 1:]

        if last_char == "/":
            ha_external_url = ha_external_url[:len(ha_external_url) - 1]

        audio_url    = ha_external_url + '/local/zalo_tts/' + audio_filename
        service_data = {'entity_id': entity_id, 'media_content_id': audio_url, 'media_content_type': 'music'}

        hass.services.call('media_player', 'play_media', service_data)

    hass.services.register(SERVICE_NAME, "say", tts)
    return True
