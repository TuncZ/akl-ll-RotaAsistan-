from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import requests
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔑 Google Maps API anahtarını buraya ekle
GOOGLE_API_KEY = 'AIzaSyDppQCusNzyEVBq4mgINSwQuu6gXjRQlwI'

reader = easyocr.Reader(['tr', 'en'])

@app.route('/api/nerede', methods=['POST'])
def nerede():
    if 'image' not in request.files:
        return jsonify({'error': 'Görsel bulunamadı'}), 400

    image = request.files['image']
    filename = image.filename
    if filename == '':
        return jsonify({'error': 'Dosya ismi boş!'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(save_path)

    try:
        # 1️⃣ OCR ile metni oku
        results = reader.readtext(save_path, detail=0)
        text = " ".join(results).strip()
        print("📖 Okunan metin:", text)

        if not text:
            return jsonify({'error': 'Metin okunamadı'}), 400

        # 2️⃣ Google Maps’te bu metni ara
        gmaps_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
        params = {
            'input': text,
            'inputtype': 'textquery',
            'fields': 'geometry,name,formatted_address',
            'key': GOOGLE_API_KEY,
        }

        response = requests.get(gmaps_url, params=params)
        data = response.json()

        if not data.get('candidates'):
            return jsonify({'error': 'Konum bulunamadı', 'text': text}), 404

        place = data['candidates'][0]
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        name = place.get('name', '')
        address = place.get('formatted_address', '')

        print("📍 En yakın eşleşen konum:", name, address)

        return jsonify({
            'text': text,
            'place_name': name,
            'address': address,
            'lat': lat,
            'lng': lng
        })

    except Exception as e:
        print("❌ HATA:", str(e))
        return jsonify({'error': 'İşlenemedi: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
