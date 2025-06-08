from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from meteostat import Point, Daily
from sklearn.preprocessing import LabelEncoder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import warnings
warnings.filterwarnings('ignore')
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import os
import traceback

# Flask uygulaması ve CORS ayarları
app = Flask(__name__)
CORS(app)

# Model yolları - models klasöründen yükle
MODEL_CANCELLED_PATH = os.path.join('models', 'model_cancelled.joblib')
MODEL_CODE_PATH = os.path.join('models', 'model_cancel_code.joblib')
MODEL_DELAY_PATH = os.path.join('models', 'model_delay.joblib')

# İptal kodları açıklamaları
CANCELLATION_CODES = {
    0: 'A: Havayolu/Taşıyıcı kaynaklı',
    1: 'B: Hava durumu kaynaklı',
    2: 'C: Ulusal Hava Sistemi kaynaklı',
    3: 'D: Güvenlik kaynaklı',
    4: 'N: İptal yok'
}

# Gecikme sınıfları açıklamaları
DELAY_CLASSES = {
    0: "Zamanında veya erken",
    1: "Hafif gecikme (1-15 dakika)",
    2: "Orta gecikme (16-30 dakika)",
    3: "Ciddi gecikme (30+ dakika)"
}

# Havayolu ve şehir eşleştirmeleri
AIRLINE_MAPPING = {
    'THY': 'AA',  # Turkish Airlines -> American Airlines
    'PEGASUS': 'WN',  # Pegasus -> Southwest
    'ANADOLUJET': 'EV',  # AnadoluJet -> ExpressJet
    'SUNEXPRESS': 'F9'  # SunExpress -> Frontier
}

CITY_MAPPING = {
    'Istanbul': 'New York, NY',
    'Izmir': 'Los Angeles, CA',
    'Ankara': 'Chicago, IL',
    'Antalya': 'Miami, FL',
    'Bodrum': 'Orlando, FL',
    'Dalaman': 'Tampa, FL',
    'Trabzon': 'Seattle, WA',
    'Adana': 'Houston, TX',
    'Gaziantep': 'Dallas, TX',
    'Kayseri': 'Denver, CO'
}

# Global nesneleri tanımla
model_cancelled = None
model_code = None
model_delay = None
imputer = None
scaler = None
imputer_delay = None
scaler_delay = None
airline_encoder = None
city_encoder = None

# Model eğitiminde kullanılan özellik sırası
FEATURE_ORDER = [
    'YEAR_NORMALIZED', 'MONTH', 'DAY', 'DAY_OF_WEEK', 'SEASON',
    'MONTH_SIN', 'MONTH_COS', 'DAY_SIN', 'DAY_COS',
    'AIR', 'ORG', 'DST', 'CRS_DEP_TIME', 'CRS_ARR_TIME',
    'DISTANCE', 'DISTANCE_CATEGORY', 'DEP_TIME_DETAILED',
    'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd',
    'wpgt', 'pres', 'tsun', 'WEATHER_COMPOSITE',
    'ROUTE_POPULARITY_LOG', 'AIRLINE_RELIABILITY'
]

def load_models():
    """Model ve diğer dosyaları yükler"""
    global model_cancelled, model_code, model_delay, imputer, scaler, imputer_delay, scaler_delay, airline_encoder, city_encoder

    try:
        model_cancelled = joblib.load(MODEL_CANCELLED_PATH)
        model_code = joblib.load(MODEL_CODE_PATH)
        model_delay = joblib.load(MODEL_DELAY_PATH)
        
        # Encoder'ları yükle
        airline_encoder = joblib.load(os.path.join('models', 'label_enc_airline.joblib'))
        city_encoder = joblib.load(os.path.join('models', 'label_enc_origin.joblib'))
        
        # Orijinal imputer ve scaler'ı yükle
        imputer = joblib.load(os.path.join('models', 'imputer.joblib'))
        scaler = joblib.load(os.path.join('models', 'scaler.joblib'))
        
        # Gecikme modeli için imputer ve scaler'ı yükle
        imputer_delay = joblib.load(os.path.join('models', 'imputer_delay.joblib'))
        scaler_delay = joblib.load(os.path.join('models', 'scaler_delay.joblib'))
        
        return True
    except Exception as e:
        print(f"Model yükleme hatası: {str(e)}")
        return False

# Geocoding servisi
class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="flight_predictor")
        self.cache = {}

    def get_coordinates(self, city_name, country=None):
        cache_key = f"{city_name}, {country}" if country else city_name
        if cache_key in self.cache:
            return self.cache[cache_key]
        try:
            location = self.geolocator.geocode(cache_key, timeout=10)
            if location:
                coords = {'lat': location.latitude, 'lon': location.longitude}
                self.cache[cache_key] = coords
                return coords
            return {'lat': 0, 'lon': 0}  # Varsayılan koordinatlar
        except Exception:
            return {'lat': 0, 'lon': 0}  # Hata durumunda varsayılan

geocoding_service = GeocodingService()

def get_weather_data(city_name, date):
    """Hava durumu verisi alır, hata durumunda varsayılan değerler döndürür"""
    default_weather = {
        'tmin': 0, 'tmax': 0, 'prcp': 0, 'snow': 0,
        'wdir': 0, 'wspd': 0, 'wpgt': 0, 'pres': 1013.25, 'tsun': 0
    }

    try:
        coords = geocoding_service.get_coordinates(city_name)
        point = Point(coords['lat'], coords['lon'])
        weather_data = Daily(point, date, date).fetch()

        if weather_data.empty:
            return default_weather

        weather_dict = weather_data.iloc[0].fillna(0).to_dict()
        result = {}
        for key in default_weather.keys():
            result[key] = weather_dict.get(key, default_weather[key])
        return result
    except Exception:
        return default_weather

def weather_composite_score(weather):
    """Hava durumu composite score hesaplar"""
    score = 0

    # Yağış etkisi
    if weather['prcp'] > 0:
        score += min(weather['prcp'] / 10, 3)  # Max 3 puan

    # Kar etkisi (daha ağır)
    if weather['snow'] > 0:
        score += min(weather['snow'] / 5, 4)   # Max 4 puan

    # Rüzgar etkisi
    if weather['wspd'] > 10:
        score += min((weather['wspd'] - 10) / 10, 2)  # Max 2 puan

    # Sıcaklık ekstremleği
    if weather['tmax'] > 35 or weather['tmin'] < -10:
        score += 1

    # Basınç etkisi
    if weather['pres'] < 1000 or weather['pres'] > 1025:
        score += 0.5

    return min(score, 10)  # Maximum 10

def categorize_time_detailed(time):
    """Uçuş zamanını kategorize eder"""
    if pd.isna(time):
        return 0
    hour = int(time // 100)
    if 5 <= hour < 8:
        return 1   # Erken sabah (yoğun)
    elif 8 <= hour < 12:
        return 2   # Sabah (orta)
    elif 12 <= hour < 15:
        return 3   # Öğlen (düşük)
    elif 15 <= hour < 19:
        return 4   # Öğleden sonra (yoğun)
    elif 19 <= hour < 22:
        return 5   # Akşam (orta)
    else:
        return 6   # Gece (düşük)

def prepare_features(data):
    """İstek verisinden model özellikleri hazırlar"""
    try:
        # Tarihi parse et
        flight_date = datetime.strptime(data['date'], '%Y-%m-%d')
        
        # Yıl normalizasyonu
        min_year = 2015  # Model eğitimindeki minimum yıl
        max_year = 2024  # Model eğitimindeki maximum yıl
        year_normalized = (flight_date.year - min_year) / (max_year - min_year)

        # Mevsimsel özellikler
        season = {12: 0, 1: 0, 2: 0,  # Kış
                 3: 1, 4: 1, 5: 1,   # İlkbahar
                 6: 2, 7: 2, 8: 2,   # Yaz
                 9: 3, 10: 3, 11: 3}[flight_date.month]

        # Yaz ayı için ideal hava durumu değerleri
        if season == 2:  # Yaz
            weather = {
                'tmin': 22.0,
                'tmax': 30.0,
                'prcp': 0.0,
                'snow': 0.0,
                'wdir': 180.0,
                'wspd': 3.0,
                'wpgt': 0.0,
                'pres': 1015.0,
                'tsun': 10.0
            }
        else:
            # Diğer mevsimler için varsayılan değerler
            weather = {
                'tmin': 15.0,
                'tmax': 25.0,
                'prcp': 0.0,
                'snow': 0.0,
                'wdir': 180.0,
                'wspd': 5.0,
                'wpgt': 0.0,
                'pres': 1015.0,
                'tsun': 8.0
            }

        # Havayolu ve şehir kodlarını dönüştür
        airline_code = safe_encode(airline_encoder, data.get('airline', 'Unknown'), 0)
        origin_code = safe_encode(city_encoder, data.get('origin', 'Unknown'), 0)
        dest_code = safe_encode(city_encoder, data.get('destination', 'Unknown'), 0)

        # Zaman değerlerini düzenle
        dep_time = int(data.get('departure_time', '00:00').replace(':', ''))
        arr_time = int(data.get('arrival_time', '00:00').replace(':', ''))

        # Mesafe değerini al ve kategorize et
        distance = float(data.get('distance', 0))
        distance_category = pd.cut([distance], 
                                 bins=[0, 400, 800, 1500, 3000, 6000],
                                 labels=[0, 1, 2, 3, 4])[0]

        # Trigonometric features
        month_sin = np.sin(2 * np.pi * flight_date.month / 12)
        month_cos = np.cos(2 * np.pi * flight_date.month / 12)
        day_sin = np.sin(2 * np.pi * flight_date.day / 31)
        day_cos = np.cos(2 * np.pi * flight_date.day / 31)

        # Hava durumu composite score
        weather_score = weather_composite_score(weather)

        # Uçuş zamanı kategorisi
        dep_time_detailed = categorize_time_detailed(dep_time)

        # Route popularity ve airline reliability için sabit değerler
        route_popularity_log = 5.0  # Yüksek rota popülerliği
        airline_reliability = 0.05  # Düşük iptal oranı

        # Model özelliklerini oluştur
        features = {
            'YEAR_NORMALIZED': year_normalized,
            'MONTH': flight_date.month,
            'DAY': flight_date.day,
            'DAY_OF_WEEK': flight_date.weekday(),
            'SEASON': season,
            'MONTH_SIN': month_sin,
            'MONTH_COS': month_cos,
            'DAY_SIN': day_sin,
            'DAY_COS': day_cos,
            'AIR': airline_code,
            'ORG': origin_code,
            'DST': dest_code,
            'CRS_DEP_TIME': dep_time,
            'CRS_ARR_TIME': arr_time,
            'DISTANCE': distance,
            'DISTANCE_CATEGORY': distance_category,
            'DEP_TIME_DETAILED': dep_time_detailed,
            'tmin': weather['tmin'],
            'tmax': weather['tmax'],
            'prcp': weather['prcp'],
            'snow': weather['snow'],
            'wdir': weather['wdir'],
            'wspd': weather['wspd'],
            'wpgt': weather['wpgt'],
            'pres': weather['pres'],
            'tsun': weather['tsun'],
            'WEATHER_COMPOSITE': weather_score,
            'ROUTE_POPULARITY_LOG': route_popularity_log,
            'AIRLINE_RELIABILITY': airline_reliability
        }

        # Özellikleri sıralı bir şekilde numpy array'e dönüştür
        features_array = np.array([[features[name] for name in FEATURE_ORDER]])

        # Veriyi impute et
        features_imputed = imputer.transform(features_array)

        # Ölçeklendirme
        features_scaled = scaler.transform(features_imputed)

        return features_scaled[0]  # Tek boyutlu array döndür

    except Exception as e:
        print(f"Özellik hazırlama hatası: {str(e)}")
        return None

def prepare_delay_features(data):
    """Gecikme modeli için özellik hazırlar"""
    try:
        # Tarihi parse et
        flight_date = datetime.strptime(data['date'], '%Y-%m-%d')
        
        # Havayolu ve şehir kodlarını dönüştür
        airline_code = safe_encode(airline_encoder, data.get('airline', 'Unknown'), 0)
        origin_code = safe_encode(city_encoder, data.get('origin', 'Unknown'), 0)
        dest_code = safe_encode(city_encoder, data.get('destination', 'Unknown'), 0)

        # Zaman değerlerini düzenle
        dep_time = int(data.get('departure_time', '00:00').replace(':', ''))
        arr_time = int(data.get('arrival_time', '00:00').replace(':', ''))

        # Mesafe değerini al
        distance = float(data.get('distance', 0))

        # Yaz ayı için ideal hava durumu değerleri
        if flight_date.month in [6, 7, 8]:  # Yaz
            weather = {
                'tmin': 22.0,
                'tmax': 30.0,
                'prcp': 0.0,
                'snow': 0.0,
                'wdir': 180.0,
                'wspd': 3.0,
                'wpgt': 0.0,
                'pres': 1015.0,
                'tsun': 10.0
            }
        else:
            # Diğer mevsimler için varsayılan değerler
            weather = {
                'tmin': 15.0,
                'tmax': 25.0,
                'prcp': 0.0,
                'snow': 0.0,
                'wdir': 180.0,
                'wspd': 5.0,
                'wpgt': 0.0,
                'pres': 1015.0,
                'tsun': 8.0
            }

        # Gecikme modeli için özellikleri oluştur (imputer'ın beklediği tüm özellikler)
        features = {
            'YEAR': flight_date.year,
            'MONTH': flight_date.month,
            'DAY': flight_date.day,
            'AIR': airline_code,
            'ORG': origin_code,
            'DST': dest_code,
            'CRS_DEP_TIME': dep_time,
            'DISTANCE': distance,
            'tmin': weather['tmin'],
            'tmax': weather['tmax'],
            'prcp': weather['prcp'],
            'snow': weather['snow'],
            'wdir': weather['wdir'],
            'wspd': weather['wspd'],
            'wpgt': weather['wpgt'],
            'pres': weather['pres'],
            'tsun': weather['tsun'],
            'DEP_TIME': dep_time,  # İmputer'ın beklediği ek özellik
            'CRS_ARR_TIME': arr_time  # İmputer'ın beklediği ek özellik
        }

        # Özellikleri sıralı bir şekilde numpy array'e dönüştür
        features_array = np.array([[features[name] for name in sorted(features.keys())]])

        # Veriyi impute et (gecikme modeli için)
        features_imputed = imputer_delay.transform(features_array)

        # Ölçeklendirme (gecikme modeli için)
        features_scaled = scaler_delay.transform(features_imputed)

        # Model için gerekli olan 17 özelliği seç
        model_features = features_scaled[0][:17]  # İlk 17 özelliği al

        return model_features  # Tek boyutlu array döndür

    except Exception as e:
        print(f"Gecikme özellik hazırlama hatası: {str(e)}")
        return None

def safe_encode(encoder, value, default=0):
    """Güvenli bir şekilde encode eder, hata durumunda default değeri döndürür"""
    try:
        # Havayolu kodları için büyük harfe çevir
        if value in AIRLINE_MAPPING.values():
            value = str(value).upper()
        # Şehir isimleri için orijinal formatı koru
        else:
            value = str(value)
        result = encoder.transform([value])[0]
        return int(result)
    except Exception as e:
        print(f"Encoding error for {value}: {str(e)}")
        return default

@app.route('/predict', methods=['POST'])
def predict():
    """Hızlı düzeltme ile tahmin fonksiyonu"""
    try:
        data = request.json
        print("\nGelen istek verisi:", data)

        if model_cancelled is None:
            if not load_models():
                return jsonify({'error': 'Modeller yüklenemedi'}), 500

        features_scaled = prepare_features(data)
        if features_scaled is None:
            return jsonify({'error': 'Özellik hazırlama hatası'}), 400

        # İptal tahmini
        cancelled_pred = model_cancelled.predict([features_scaled])[0]
        cancelled_proba = model_cancelled.predict_proba([features_scaled])[0]

        print(f"Ham tahmin: İptal={cancelled_pred}, Olasılık={cancelled_proba}")

        # === HİZLI DÜZELTMELERİ UYGULA ===
        flight_date = datetime.strptime(data['date'], '%Y-%m-%d')
        dep_time = int(data.get('departure_time', '00:00').replace(':', ''))
        distance = float(data.get('distance', 0))
        
        # Düzeltme faktörü hesapla
        correction_factor = 1.0
        correction_reasons = []
        
        # 1. Yaz ayları düzeltmesi
        if flight_date.month in [6, 7, 8]:
            correction_factor *= 0.3  # %70 azaltma
            correction_reasons.append("Yaz ayı")
        
        # 2. Gündüz uçuşları düzeltmesi  
        if 800 <= dep_time <= 1800:
            correction_factor *= 0.5  # %50 azaltma
            correction_reasons.append("Gündüz uçuşu")
        
        # 3. Kısa mesafe düzeltmesi
        if distance < 1000:
            correction_factor *= 0.6  # %40 azaltma
            correction_reasons.append("Kısa mesafe")
        
        # 4. Popüler havayolları düzeltmesi
        if data.get('airline') in ['AA', 'DL', 'UA']:
            correction_factor *= 0.7  # %30 azaltma
            correction_reasons.append("Güvenilir havayolu")
        
        # Düzeltmeyi uygula
        if correction_factor < 1.0:
            original_cancel_prob = cancelled_proba[1]
            adjusted_cancel_prob = original_cancel_prob * correction_factor
            
            # Minimum %2, maksimum %95 sınırı
            adjusted_cancel_prob = max(0.02, min(0.95, adjusted_cancel_prob))
            
            cancelled_proba = np.array([1 - adjusted_cancel_prob, adjusted_cancel_prob])
            
            print(f"Düzeltmeler uygulandı: {correction_reasons}")
            print(f"Düzeltme faktörü: {correction_factor}")
            print(f"Orijinal: {original_cancel_prob:.4f} -> Düzeltilmiş: {adjusted_cancel_prob:.4f}")
        
        # Yeni karar ver (yüksek threshold)
        THRESHOLD = 0.45
        cancelled_pred = 1 if cancelled_proba[1] > THRESHOLD else 0
        
        print(f"Final karar: İptal={cancelled_pred} (Threshold: {THRESHOLD})")
        
        # Güven skoru
        confidence = max(cancelled_proba)
        
        # Sonuç hazırla
        result = {
            'predictions': {
                'cancelled': bool(cancelled_pred),
                'cancelled_probability': {
                    'not_cancelled': float(cancelled_proba[0]),
                    'cancelled': float(cancelled_proba[1])
                },
                'confidence': float(confidence),
                'model_adjustments': {
                    'corrections_applied': correction_reasons,
                    'correction_factor': correction_factor,
                    'threshold_used': THRESHOLD
                }
            }
        }

        # İptal kodu tahmini
        if cancelled_pred == 1:
            code_pred = int(model_code.predict([features_scaled])[0])
            code_probs = model_code.predict_proba([features_scaled])[0]
            result['predictions']['cancellation_code'] = CANCELLATION_CODES[code_pred]
            result['predictions']['cancellation_code_probabilities'] = {}
            for i, prob in enumerate(code_probs):
                if i in CANCELLATION_CODES:
                    result['predictions']['cancellation_code_probabilities'][CANCELLATION_CODES[i]] = float(prob)
        else:
            # İptal olmayan uçuşlar için gecikme tahmini
            delay_features = prepare_delay_features(data)
            if delay_features is None:
                return jsonify({'error': 'Gecikme özellik hazırlama hatası'}), 400
                
            delay_pred = int(model_delay.predict([delay_features])[0])
            delay_probs = model_delay.predict_proba([delay_features])[0]
            
            result['predictions']['delay'] = {
                'delay_class': DELAY_CLASSES[delay_pred],
                'delay_probabilities': {}
            }
            
            for i, prob in enumerate(delay_probs):
                if i in DELAY_CLASSES:
                    result['predictions']['delay']['delay_probabilities'][DELAY_CLASSES[i]] = float(prob)

        return jsonify(result)

    except Exception as e:
        traceback_str = traceback.format_exc()
        print(f"Hata: {str(e)}\nStack trace: {traceback_str}")
        return jsonify({
            'error': f"Tahmin hatası: {str(e)}",
            'details': traceback_str
        }), 400
        
@app.route('/airlines', methods=['GET'])
def get_airlines():
    """Desteklenen havayollarını döndürür"""
    if airline_encoder is None:
        load_models()

    if airline_encoder is not None:
        return jsonify({'airlines': list(airline_encoder.classes_)})
    else:
        return jsonify({'error': 'Havayolu kodlayıcı yüklenemedi'}), 500

@app.route('/cities', methods=['GET'])
def get_cities():
    """Desteklenen şehirleri döndürür"""
    if city_encoder is None:
        load_models()

    if city_encoder is not None:
        return jsonify({'cities': list(city_encoder.classes_)})
    else:
        return jsonify({'error': 'Şehir kodlayıcı yüklenemedi'}), 500

@app.route('/test', methods=['GET'])
def test():
    """API'nin çalıştığını test eder"""
    return jsonify({'status': 'ok', 'message': 'API çalışıyor'})

if __name__ == '__main__':
    # Modelleri yükle
    if not load_models():
        print("Modeller yüklenemedi! Uygulama kapatılıyor...")
        exit(1)
    
    # Sunucuyu başlat
    app.run(host='0.0.0.0', port=5050, debug=False)