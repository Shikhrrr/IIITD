import requests

url = "https://api.sarvam.ai/speech-to-text"
payload = {
    'model': 'saarika:v1',
    'language_code': 'hi-IN',
    'with_timestamps': 'false'
}
files = [
    ('file', ('audio.wav', open('Recording (8).wav', 'rb'), 'audio/wav'))
]
headers = {
    'api-subscription-key': 'sk_xwpyz1yp_ai9KCro5vn7r15YtStWA6lpg'
}

response = requests.post(url, headers=headers, data=payload, files=files)
print(response.text)
