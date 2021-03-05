https://zalo.ai/docs/api/text-to-audio-converter

Config in configuration.yaml file for Home Assistant
```
tts_zalo:
  api_key: 'your_api_key'
  url: 'https://your_domain.duckdns.org' or 'http://192.168.1.100:8123'
  ````

Code in automation:
```
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
```
