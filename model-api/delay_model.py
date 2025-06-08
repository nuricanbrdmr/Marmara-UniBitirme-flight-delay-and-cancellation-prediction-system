import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from google.colab import drive
import os
import warnings
import matplotlib.pyplot as plt
import joblib
warnings.filterwarnings('ignore')

# Google Drive'ı bağlama
drive.mount('/content/drive')

# Çalışma dizinini ayarlama
os.chdir('/content/drive/My Drive/Bitirme')

df = pd.read_csv(r"flights_Delay_final.csv")
df.head(5)

# İptal edilmiş uçuşları kaldırma
df = df[df['CANCELLED'] == 0]

# Tarih sütununu datetime'a çevirme ve yıl, ay, gün olarak ayırma
df['FL_DATE'] = pd.to_datetime(df['FL_DATE'], format='%Y-%m-%d')
df['YEAR'] = df['FL_DATE'].dt.year
df['MONTH'] = df['FL_DATE'].dt.month
df['DAY'] = df['FL_DATE'].dt.day

# Kategorik sütunlar için LabelEncoder
label_enc = LabelEncoder()
df['AIR'] = label_enc.fit_transform(df['AIRLINE_CODE'])
df['ORG'] = label_enc.fit_transform(df['ORIGIN_CITY'])
df['DST'] = label_enc.fit_transform(df['DEST_CITY'])

# Gereksiz sütunları silme
df.drop(['AIRLINE_CODE', 'ORIGIN_CITY', 'DEST_CITY', 'CANCELLED', 'FL_DATE', 'CANCELLATION_CODE', "CRS_ARR_TIME"], axis=1, inplace=True)

df.head()

# Veri Ön İşleme
# Eksik değerleri doldurma
print("Eksik değerler dolduruluyor...")
imputer = SimpleImputer(strategy='median')
df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

# Ölçeklendirme (StandardScaler)
scaler = StandardScaler()
df[df.columns] = scaler.fit_transform(df[df.columns])

# Gecikme sürelerini sınıflara ayırma (Hedef değişken oluşturma)
df['DELAY_CLASS'] = df['DEP_DELAY'].apply(lambda x: 0 if x <= 0 else
                                         (1 if x <= 15 else
                                          (2 if x <= 30 else 3)))

# Sınıf dağılımını kontrol etme
print("\nSınıf dağılımı:")
print(df['DELAY_CLASS'].value_counts(normalize=True))

# Özellikleri ve hedefi hazırlama
y = df['DELAY_CLASS']
X = df.drop(['DELAY_CLASS', 'DEP_DELAY', "DEP_TIME"], axis=1)

# Verileri bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Veri Dengesizliğini Giderme (SMOTE)
print("Veri SMOTE ile Dengesizlik Gideriliyor...")
smote = SMOTE(random_state=42, k_neighbors=5)
X_train, y_train = smote.fit_resample(X_train, y_train)

df["DELAY_CLASS"].value_counts()

# SMOTE sonrası sınıf dağılımını kontrol etme
print("\nSınıf dağılımı:")
print(y_train.value_counts(normalize=True))

# Pipeline oluşturma
pipeline = ImbPipeline([
    ('classifier', XGBClassifier(
        n_estimators=100,
        max_depth=10,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=1,
        random_state=42,
        eval_metric='logloss'
    ))
])

# Modeli eğitme
print("\nModel eğitimi başlıyor...")
pipeline.fit(X_train, y_train)
print("Model eğitimi tamamlandı!")

# Model performansını değerlendirme
y_pred = pipeline.predict(X_test)

print("\nModel Performansı:")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print(f"\nAccuracy Score: {accuracy_score(y_test, y_pred):.4f}")

# Modeli ve gerekli bileşenleri kaydet
print("\nModel ve bileşenler kaydediliyor...")
joblib.dump(pipeline, 'model_delay.joblib')
joblib.dump(imputer, 'imputer_delay.joblib')
joblib.dump(scaler, 'scaler_delay.joblib')
joblib.dump(label_enc, 'label_enc_delay.joblib')

print("Kaydedilen dosyalar:")
print("✅ model_delay.joblib")
print("✅ imputer_delay.joblib")
print("✅ scaler_delay.joblib")
print("✅ label_enc_delay.joblib")

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

# Confusion matrix oluştur
cm = confusion_matrix(y_test, y_pred)

# Görselleştir
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=[0, 1,2,3], yticklabels=[0, 1,2,3])
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix")
plt.show()

# Eğitim ve test doğruluğunu karşılaştırma
pipeline.fit(X_train, y_train)

y_train_pred_delay = pipeline.predict(X_train)
train_accuracy_delay = accuracy_score(y_train, y_train_pred_delay)

y_test_pred_delay = pipeline.predict(X_test)
test_accuracy_delay = accuracy_score(y_test, y_test_pred_delay)

print(f"Gecikme Sınıfı - Eğitim Doğruluğu: {train_accuracy_delay:.2f}")
print(f"Gecikme Sınıfı - Test Doğruluğu: {test_accuracy_delay:.2f}")
print(f"Fark: {abs(train_accuracy_delay - test_accuracy_delay):.2f}")

# Özellik önemlerini görselleştirme
importances = pipeline.named_steps['classifier'].feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(12, 6))
plt.title("Gecikme Sınıflandırması - Özellik Önem Dereceleri", fontsize=14, pad=20)
plt.bar(range(X_train.shape[1]), importances[indices])
plt.xticks(range(X_train.shape[1]), [X_train.columns[i] for i in indices], rotation=45, ha='right')
plt.xlabel('Özellikler')
plt.ylabel('Önem Derecesi')
plt.tight_layout()
plt.show()

# Örnek tahmin için yeni veri
new_data = pd.DataFrame({
    'YEAR': [2024],
    'MONTH': [5],
    'DAY': [15],
    'AIR': [14],
    'ORG': [289],
    'DST': [202],
    'CRS_DEP_TIME': [2155],
    'DISTANCE': [612],
    'tmin': [18.9],
    'tmax': [25],
    'prcp': [0],
    'snow': [0],
    'wdir': [312],
    'wspd': [11.5],
    'wpgt': [0],
    'pres': [1018.6],
    'tsun': [0]
}, index=[0])

# Eksik sütunları kontrol etme ve ekleme
missing_columns = set(X_train.columns) - set(new_data.columns)
for col in missing_columns:
    new_data[col] = 0

# Sütun sırasını train verisi ile aynı yapma
new_data = new_data[X_train.columns]

# Tahmin yapma
prediction = pipeline.predict(new_data)
prediction_proba = pipeline.predict_proba(new_data)

# Gecikme sınıfları sözlüğü
delay_classes = {
    0: "Zamanında veya erken",
    1: "Hafif gecikme (1-15 dakika)",
    2: "Orta gecikme (16-30 dakika)",
    3: "Ciddi gecikme (30+ dakika)"
}

# Tahmin sonuçlarını yazdırma
print("\nTahmin Sonucu:")
print(f"Tahmin edilen sınıf: {delay_classes[prediction[0]]}")
print("\nSınıf olasılıkları:")
for i, prob in enumerate(prediction_proba[0]):
    print(f"{delay_classes[i]}: {prob:.2%}")