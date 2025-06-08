import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score, confusion_matrix
from sklearn.metrics import precision_recall_curve, roc_curve, auc
from google.colab import drive
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Google Drive'ı bağlama
drive.mount('/content/drive')
os.chdir('/content/drive/My Drive/Bitirme')

# Veri setini okuma
df = pd.read_csv("flights_Cancel_final.csv")

# Tarih işleme - YEAR'ın etkisini azaltmak için normalizasyon
df['FL_DATE'] = pd.to_datetime(df['FL_DATE'], format='%Y-%m-%d')
min_year = df['FL_DATE'].dt.year.min()
max_year = df['FL_DATE'].dt.year.max()

df['YEAR_NORMALIZED'] = (df['FL_DATE'].dt.year - min_year) / (max_year - min_year)
df['MONTH'] = df['FL_DATE'].dt.month
df['DAY'] = df['FL_DATE'].dt.day
df['DAY_OF_WEEK'] = df['FL_DATE'].dt.dayofweek

# Mevsimsel özellikler - daha detaylı
df['SEASON'] = df['MONTH'].map({12: 0, 1: 0, 2: 0,  # Kış
                                3: 1, 4: 1, 5: 1,   # İlkbahar
                                6: 2, 7: 2, 8: 2,   # Yaz
                                9: 3, 10: 3, 11: 3}) # Sonbahar

# Trigonometric features for cyclical data
df['MONTH_SIN'] = np.sin(2 * np.pi * df['MONTH'] / 12)
df['MONTH_COS'] = np.cos(2 * np.pi * df['MONTH'] / 12)
df['DAY_SIN'] = np.sin(2 * np.pi * df['DAY'] / 31)
df['DAY_COS'] = np.cos(2 * np.pi * df['DAY'] / 31)

# Hava durumu composite score - daha sofistike
def weather_composite_score(row):
    score = 0

    # Yağış etkisi
    if row['prcp'] > 0:
        score += min(row['prcp'] / 10, 3)  # Max 3 puan

    # Kar etkisi (daha ağır)
    if row['snow'] > 0:
        score += min(row['snow'] / 5, 4)   # Max 4 puan

    # Rüzgar etkisi
    if row['wspd'] > 10:
        score += min((row['wspd'] - 10) / 10, 2)  # Max 2 puan

    # Sıcaklık ekstremleği
    if row['tmax'] > 35 or row['tmin'] < -10:
        score += 1

    # Basınç etkisi
    if row['pres'] < 1000 or row['pres'] > 1025:
        score += 0.5

    return min(score, 10)  # Maximum 10

df['WEATHER_COMPOSITE'] = df.apply(weather_composite_score, axis=1)

# Uçuş zamanı kategorisi - daha detaylı
def categorize_time_detailed(time):
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

df['DEP_TIME_DETAILED'] = df['CRS_DEP_TIME'].apply(categorize_time_detailed)

# Mesafe kategorisi - daha dengeli
df['DISTANCE_CATEGORY'] = pd.cut(df['DISTANCE'],
                                bins=[0, 400, 800, 1500, 3000, 6000],
                                labels=[0, 1, 2, 3, 4])

# Label Encoding
label_enc_airline = LabelEncoder()
label_enc_origin = LabelEncoder()
label_enc_dest = LabelEncoder()
label_enc_cancel_code = LabelEncoder()

df['AIR'] = label_enc_airline.fit_transform(df['AIRLINE_CODE'])
df['ORG'] = label_enc_origin.fit_transform(df['ORIGIN_CITY_NAME'])
df['DST'] = label_enc_dest.fit_transform(df['DEST_CITY_NAME'])

# İptal kodları için özel işlem
df['CANCELLATION_CODE_FILLED'] = df['CANCELLATION_CODE'].fillna('N')  # N = Not Cancelled
df['CANCELLATION_CODE_ENCODED'] = label_enc_cancel_code.fit_transform(df['CANCELLATION_CODE_FILLED'])

# Route popularity (may affect cancellation)
route_counts = df.groupby(['ORG', 'DST']).size()
df['ROUTE_POPULARITY'] = df.apply(lambda x: route_counts.get((x['ORG'], x['DST']), 0), axis=1)
df['ROUTE_POPULARITY_LOG'] = np.log1p(df['ROUTE_POPULARITY'])

# Airline reliability score
airline_cancel_rate = df.groupby('AIR')['CANCELLED'].mean()
df['AIRLINE_RELIABILITY'] = df['AIR'].map(airline_cancel_rate)

# Gereksiz sütunları silme
columns_to_drop = ['AIRLINE_CODE', 'ORIGIN_CITY_NAME', 'DEST_CITY_NAME', 'FL_DATE',
                   'ROUTE_POPULARITY', 'CANCELLATION_CODE', 'CANCELLATION_CODE_FILLED']
df.drop(columns_to_drop, axis=1, inplace=True)

print("Class Dağılımı:")
print(df['CANCELLED'].value_counts())
print(f"İptal oranı: {df['CANCELLED'].mean():.3f}")

print("\nİptal Kodu Dağılımı:")
print(df['CANCELLATION_CODE_ENCODED'].value_counts())

# Özellikleri ve hedefleri hazırlama
y_cancelled = df['CANCELLED']
y_cancel_code = df['CANCELLATION_CODE_ENCODED']
X = df.drop(["CANCELLED", "CANCELLATION_CODE_ENCODED", "DEP_TIME"], axis=1)

print(f"Toplam özellik sayısı: {X.shape[1]}")
print("Özellikler:", list(X.columns))

# Verileri bölme
X_train, X_test, y_cancelled_train, y_cancelled_test = train_test_split(
    X, y_cancelled, test_size=0.3, stratify=y_cancelled, random_state=42
)

# İptal kodu için aynı indekslerle bölme
y_cancel_code_train = y_cancel_code.iloc[X_train.index]
y_cancel_code_test = y_cancel_code.iloc[X_test.index]

# Eksik değerleri doldurma
imputer = SimpleImputer(strategy='median')
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

# Ölçeklendirme
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_imputed)
X_test_scaled = scaler.transform(X_test_imputed)

# ==================== İPTAL MODELİ ====================
print("\n" + "="*50)
print("İPTAL MODELİ EĞİTİMİ")
print("="*50)

# Daha konservatif SMOTE
smote = SMOTE(sampling_strategy=0.15, random_state=42, k_neighbors=3)
X_train_resampled, y_cancelled_train_resampled = smote.fit_resample(X_train_scaled, y_cancelled_train)

print(f"Resampling sonrası dağılım:")
print(pd.Series(y_cancelled_train_resampled).value_counts())

# İptal modeli
model_cancelled = XGBClassifier(
    scale_pos_weight=4.0,  # Daha yüksek ağırlık
    n_estimators=150,
    max_depth=4,  # Daha derin ağaç
    learning_rate=0.05,  # Daha düşük öğrenme oranı
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=2.0,  # Daha fazla regularization
    reg_lambda=2.0,
    min_child_weight=20,  # Daha yüksek minimum ağırlık
    gamma=2.0,
    objective='binary:logistic',
    eval_metric='logloss',
    random_state=42,
    n_jobs=-1
)

# Model eğitimi
model_cancelled.fit(X_train_resampled, y_cancelled_train_resampled)

# Tahminler
y_pred_cancelled_proba = model_cancelled.predict_proba(X_test_scaled)

# Best threshold
best_threshold = 0.5
y_pred_cancelled_final = (y_pred_cancelled_proba[:, 1] >= best_threshold).astype(int)

print(f"\nSeçilen threshold: {best_threshold}")
print(f"CANCELLED Sınıfı - Doğruluk Oranı: {accuracy_score(y_cancelled_test, y_pred_cancelled_final):.3f}")
print(f"CANCELLED Sınıfı - Test Seti Performansı:")
print(classification_report(y_cancelled_test, y_pred_cancelled_final))
print(f"ROC-AUC Score: {roc_auc_score(y_cancelled_test, y_pred_cancelled_proba[:, 1]):.4f}")

# ==================== İPTAL KODU MODELİ ====================
print("\n" + "="*50)
print("İPTAL KODU MODELİ EĞİTİMİ")
print("="*50)

# Sadece iptal edilen uçuşlar için iptal kodu modeli
cancelled_mask_train = y_cancelled_train == 1
cancelled_mask_test = y_cancelled_test == 1

if cancelled_mask_train.sum() > 0:
    X_train_cancelled_only = X_train_scaled[cancelled_mask_train]
    y_cancel_code_train_cancelled = y_cancel_code_train.iloc[cancelled_mask_train.values]

    X_test_cancelled_only = X_test_scaled[cancelled_mask_test]
    y_cancel_code_test_cancelled = y_cancel_code_test.iloc[cancelled_mask_test.values]

    # İptal kodu dağılımını kontrol et
    print("İptal kodu dağılımı (sadece iptal edilen uçuşlar):")
    print(y_cancel_code_train_cancelled.value_counts())

    # İptal kodu modeli
    model_cancel_code = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=0.1,
        objective='multi:softprob',
        eval_metric='mlogloss',
        random_state=42,
        n_jobs=-1
    )

    # Model eğitimi
    model_cancel_code.fit(X_train_cancelled_only, y_cancel_code_train_cancelled)

    # Tahminler
    y_pred_cancel_code = model_cancel_code.predict(X_test_cancelled_only)
    y_pred_cancel_code_proba = model_cancel_code.predict_proba(X_test_cancelled_only)

    print(f"\nİptal Kodu - Doğruluk Oranı: {accuracy_score(y_cancel_code_test_cancelled, y_pred_cancel_code):.3f}")
    print(f"İptal Kodu - Test Seti Performansı:")
    print(classification_report(y_cancel_code_test_cancelled, y_pred_cancel_code))
else:
    print("İptal edilen uçuş bulunamadı!")
    model_cancel_code = None

# ==================== KAPSAMLI TAHMİN FONKSİYONU ====================
def predict_flight_complete(new_data, threshold=best_threshold):
    """
    Kapsamlı uçuş tahmini fonksiyonu - hem iptal hem de iptal kodu
    """
    # Veriyi hazırlama
    new_data = new_data[X.columns]

    # Eksik değerleri doldurma
    new_data_imputed = imputer.transform(new_data)

    # Ölçeklendirme
    new_data_scaled = scaler.transform(new_data_imputed)

    # İptal durumu tahmini
    cancelled_prob = model_cancelled.predict_proba(new_data_scaled)
    cancelled_pred = (cancelled_prob[:, 1] >= threshold).astype(int)

    # İptal kodu tahmini (sadece iptal edilecekse)
    cancel_code_pred = None
    cancel_code_prob = None
    cancel_code_desc = "Uçuş İptal Edilmeyecek"

    if cancelled_pred[0] == 1 and model_cancel_code is not None:
        cancel_code_pred = model_cancel_code.predict(new_data_scaled)
        cancel_code_prob = model_cancel_code.predict_proba(new_data_scaled)

        # İptal kodu açıklamaları
        code_descriptions = {
            0: "A - Airline/Carrier",  # Havayolu kaynaklı
            1: "B - Weather",          # Hava durumu
            2: "C - National Air System", # Ulusal hava sistemi
            3: "D - Security",         # Güvenlik
            4: "N - Not Cancelled"     # İptal edilmedi
        }

        # En olası iptal kodunu bul
        most_likely_code = cancel_code_pred[0]
        cancel_code_desc = code_descriptions.get(most_likely_code, f"Bilinmeyen Kod: {most_likely_code}")

    return {
        'cancelled_prediction': cancelled_pred[0],
        'cancelled_probability': cancelled_prob[0][1],
        'cancel_code_prediction': cancel_code_pred[0] if cancel_code_pred is not None else None,
        'cancel_code_probabilities': cancel_code_prob[0] if cancel_code_prob is not None else None,
        'cancel_code_description': cancel_code_desc,
        'threshold_used': threshold,
        'raw_cancelled_score': cancelled_prob[0][1]
    }

# ==================== TEST ÖRNEKLERİ ====================
# 1. Yaz ayı, güzel hava - İPTAL EDİLMEMELİ
summer_good_weather = pd.DataFrame({
    'CRS_DEP_TIME': [1000],
    'CRS_ARR_TIME': [1200],
    'DISTANCE': [500],
    'tmin': [20.0],
    'tmax': [28.0],
    'prcp': [0.0],
    'snow': [0.0],
    'wdir': [180.0],
    'wspd': [5.0],
    'wpgt': [0.0],
    'pres': [1015.0],
    'tsun': [9.0],
    'YEAR_NORMALIZED': [0.8],
    'MONTH': [7],
    'DAY': [15],
    'DAY_OF_WEEK': [1],
    'SEASON': [2],
    'MONTH_SIN': [np.sin(2 * np.pi * 7 / 12)],
    'MONTH_COS': [np.cos(2 * np.pi * 7 / 12)],
    'DAY_SIN': [np.sin(2 * np.pi * 15 / 31)],
    'DAY_COS': [np.cos(2 * np.pi * 15 / 31)],
    'WEATHER_COMPOSITE': [0.0],
    'DEP_TIME_DETAILED': [2],
    'DISTANCE_CATEGORY': [1],
    'AIR': [1],
    'ORG': [100],
    'DST': [200],
    'ROUTE_POPULARITY_LOG': [5.0],
    'AIRLINE_RELIABILITY': [0.05]
}, index=[0])

# 2. Kış ayı, kötü hava - İPTAL EDİLEBİLİR
winter_bad_weather = pd.DataFrame({
    'CRS_DEP_TIME': [1800],
    'CRS_ARR_TIME': [2100],
    'DISTANCE': [1200],
    'tmin': [-10.0],
    'tmax': [0.0],
    'prcp': [20.0],
    'snow': [15.0],
    'wdir': [270.0],
    'wspd': [25.0],
    'wpgt': [30.0],
    'pres': [990.0],
    'tsun': [0.0],
    'YEAR_NORMALIZED': [0.8],
    'MONTH': [1],
    'DAY': [15],
    'DAY_OF_WEEK': [0],
    'SEASON': [0],
    'MONTH_SIN': [np.sin(2 * np.pi * 1 / 12)],
    'MONTH_COS': [np.cos(2 * np.pi * 1 / 12)],
    'DAY_SIN': [np.sin(2 * np.pi * 15 / 31)],
    'DAY_COS': [np.cos(2 * np.pi * 15 / 31)],
    'WEATHER_COMPOSITE': [8.0],
    'DEP_TIME_DETAILED': [5],
    'DISTANCE_CATEGORY': [3],
    'AIR': [1],
    'ORG': [100],
    'DST': [200],
    'ROUTE_POPULARITY_LOG': [3.0],
    'AIRLINE_RELIABILITY': [0.15]
}, index=[0])

# Tahminler
print(f"\n{'='*60}")
print("KAPSAMLI TAHMİN TESTLERİ")
print(f"{'='*60}")

print(f"\n{'='*50}")
print("YAZ AYI GÜZEL HAVA TAHMİNİ")
print(f"{'='*50}")
summer_pred = predict_flight_complete(summer_good_weather)
print(f"İptal Durumu: {'❌ İptal Edilebilir' if summer_pred['cancelled_prediction'] == 1 else '✅ İptal Edilmeyecek'}")
print(f"İptal Olasılığı: {summer_pred['cancelled_probability']:.4f}")
print(f"İptal Kodu: {summer_pred['cancel_code_description']}")

print(f"\n{'='*50}")
print("KIŞ AYI KÖTÜ HAVA TAHMİNİ")
print(f"{'='*50}")
winter_pred = predict_flight_complete(winter_bad_weather)
print(f"İptal Durumu: {'❌ İptal Edilebilir' if winter_pred['cancelled_prediction'] == 1 else '✅ İptal Edilmeyecek'}")
print(f"İptal Olasılığı: {winter_pred['cancelled_probability']:.4f}")
print(f"İptal Kodu: {winter_pred['cancel_code_description']}")

if winter_pred['cancel_code_probabilities'] is not None:
    print(f"İptal Kodu Olasılıkları:")
    code_names = ['A-Airline', 'B-Weather', 'C-NAS', 'D-Security', 'N-NotCancelled']
    for i, prob in enumerate(winter_pred['cancel_code_probabilities']):
        print(f"  {code_names[i]}: {prob:.4f}")

# ==================== MODEL KAYDETME ====================
print(f"\n{'='*50}")
print("MODELLERİ KAYDETME")
print(f"{'='*50}")

# Ana modeller
joblib.dump(model_cancelled, 'model_cancelled.joblib')
joblib.dump(imputer, 'imputer.joblib')
joblib.dump(scaler, 'scaler.joblib')

if model_cancel_code is not None:
    joblib.dump(model_cancel_code, 'model_cancel_code.joblib')

# Label encoder'ları kaydet
joblib.dump(label_enc_airline, 'label_enc_airline.joblib')
joblib.dump(label_enc_origin, 'label_enc_origin.joblib')
joblib.dump(label_enc_dest, 'label_enc_dest.joblib')
joblib.dump(label_enc_cancel_code, 'label_enc_cancel_code.joblib')

# Özellik listesi ve threshold
model_config = {
    'features': list(X.columns),
    'best_threshold': best_threshold,
    'min_year': min_year,
    'max_year': max_year
}
joblib.dump(model_config, 'model_config.joblib')

print("Kaydedilen dosyalar:")
saved_files = [
    'model_cancelled.joblib',
    'imputer.joblib',
    'scaler.joblib',
    'label_enc_airline.joblib',
    'label_enc_origin.joblib',
    'label_enc_dest.joblib',
    'label_enc_cancel_code.joblib',
    'model_config.joblib'
]

if model_cancel_code is not None:
    saved_files.append('model_cancel_code.joblib')

for file in saved_files:
    print(f"✅ {file}")