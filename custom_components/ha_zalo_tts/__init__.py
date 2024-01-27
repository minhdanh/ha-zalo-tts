import requests, json, os, time, re
import logging

SERVICE_NAME = 'ha_zalo_tts'

audio_filename = 'tts_zalo.mp3'


_LOGGER = logging.getLogger(__name__)

def limit_message_size(message):
    zalo_character_limit = 1980
    message = re.sub(r'\s+', ' ', message)
    message = message.replace('\n', ' ')
    index                = message.find(" ", zalo_character_limit)
    if index != -1:
        message = message[0:index].strip()
    # else: index == -1 and lenght > 1980 ?
    return message

def zalo_tts(api_key, speed, voice, message, audio_path):
    api_url        = 'https://api.zalo.ai/v1/tts/synthesize'
    api_key_header = {'apikey': str(api_key)}
    data_payload   = {'input': limit_message_size(message), 'speed': str(speed), 'encode_type': '1','speaker_id': str(voice)}

    response = requests.post(api_url, data = data_payload, headers = api_key_header).json()
    if 'data' in response and 'url' in response['data']:
        return True, response['data']['url']
    return False, ""

def setup(hass, config):
    def tts(data_call):
        api_key            = config[SERVICE_NAME]["api_key"]
        voice              = data_call.data.get("voice")
        speed              = data_call.data.get("speed")
        entity_id          = data_call.data.get("entity_id")
        message            = data_call.data.get("message")
        success, audio_url = zalo_tts(api_key, speed, voice, message, audio_path)

        if success == False:
            _LOGGER.error("The request timed out or something went wrong!")
            return False

        service_data = {'entity_id': entity_id, 'media_content_id': audio_url, 'media_content_type': 'music'}
        hass.services.call('media_player', 'play_media', service_data)

    hass.services.register(SERVICE_NAME, "say", tts)
    return True
