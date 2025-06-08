# SmartTicket (FCDP-SFTS AI Model Web Uygulaması)

## Proje Tanımı
SmartTicket, uçuş iptal ve gecikme tahminleri sunan, modern ve kullanıcı dostu bir web uygulamasıdır. Kullanıcılar, uçuş araması yaparak seçtikleri biletin iptal ve gecikme risklerini, yapay zeka destekli modelden anlık olarak görebilirler. Model, uçuşun iptal olma ve gecikme olasılıklarını, güven oranı ile birlikte detaylı şekilde sunar.

## Ana Klasör ve Dosya Yapısı
```
SmartTicket/
│
├── bitirme-frontend/      # React tabanlı web arayüzü
│   └── src/
│       └── components/    # Ana React bileşenleri (Ticket, Travel, Navbar, vs.)
│       └── api/           # API istekleri
│       └── ...
│
├── bitirme-backend/       # Node.js/Express tabanlı API sunucusu
│   └── controllers/       # Uçuş, lokasyon, kullanıcı controller dosyaları
│   └── routes/            # API endpoint tanımları
│   └── models/            # Kullanıcı modeli
│   └── constant/          # Şehir/havalimanı sabit verileri
│   └── ...
│
├── model-api/             # Python tabanlı AI model ve API
│   ├── cancel_delay_api.py  # Ana API dosyası (Flask/FastAPI)
│   ├── delay_model.py       # Gecikme tahmin modeli kodu
│   ├── cancel_model.py      # İptal tahmin modeli kodu
│   ├── requirements.txt     # Python bağımlılıkları
│   └── models/              # Eğitilmiş model dosyaları (.joblib)
│
└── README.md              # Proje dökümantasyonu
```

## Kullanılan Teknolojiler
- **Frontend:** React.js, Tailwind CSS, Ant Design, Framer Motion, React Icons
- **Backend:** Node.js, Express.js
- **Model API:** Python (Flask veya FastAPI), scikit-learn, joblib
- **Diğer:** Axios (API istekleri için)

## Kurulum
### 1. Model API (model-api)
```bash
cd model-api
pip install -r requirements.txt
python cancel_delay_api.py
```

### 2. Backend (bitirme-backend)
```bash
cd bitirme-backend
npm install
```

#### Ortam Değişkenleri
Aşağıdaki değişkenleri içeren `bitirme-backend` dizininde bir `.env` dosyası oluşturun:
```env
# Database
MONGODB_URI=your_mongodb_connection_string

# JWT Authentication
JWT_SECRET_KEY=your_jwt_secret_key
JWT_REFRESH_SECRET_KEY=your_jwt_refresh_secret_key
JWT_EXPIRES_TIME=24h

# Email Configuration
NODE_USER=your_email_address
NODE_PASS=your_email_password
```

Ardından sunucuyu başlatın:
```bash
node server.js
```

### 3. Frontend (bitirme-frontend)
```bash
cd bitirme-frontend
npm install
npm install framer-motion antd react-icons axios
npm start
```

## Kullanım
1. Model API'yi başlatın (model-api klasöründe):
   ```bash
   python cancel_delay_api.py
   ```
2. Backend'i başlatın (bitirme-backend klasöründe):
   ```bash
   node server.js
   ```
3. Frontend'i başlatın (bitirme-frontend klasöründe):
   ```bash
   npm start
   ```
4. Tarayıcıda `http://localhost:5173` adresine gidin.

## Ana Özellikler
- **Uçuş Arama:** Kalkış/varış şehirleri ve tarih seçimiyle uçuş arama
- **Bilet Kartı:** Havayolu, saatler, fiyat ve model tahminleri
- **AI Model Tahmin Detayları:**
  - Sadece "FCDP-SFTS AI Model Tahmin Detayları" etiketine tıklanınca açılır
  - Açılış/kapanış animasyonludur (framer-motion)
  - İptal olasılığı kırmızı, olmama olasılığı yeşil Progress bar ile gösterilir
  - Gecikme tahminlerinde "Zamanında veya erken" yeşil, diğerleri kırmızı Progress bar ile gösterilir
  - Modelin uyguladığı düzeltmeler ve güven oranı detaylı şekilde sunulur
- **Modern UI:** Ant Design, Tailwind ve animasyonlarla zenginleştirilmiş kullanıcı deneyimi

## model-api Hakkında
- **cancel_delay_api.py:** Ana API dosyası, uçuş iptal ve gecikme tahminlerini sunar
- **delay_model.py & cancel_model.py:** Model tahmin fonksiyonları
- **models/**: Eğitilmiş scikit-learn modelleri (.joblib)
- **requirements.txt:** Gerekli Python paketleri

## Ekran Görüntüsü
> Buraya bir ekran görüntüsü ekleyebilirsiniz:
> ![Ekran Görüntüsü](./screenshot.png)

## Geliştirme ve Özelleştirme Notları
- Şehir ve havalimanı verileri backend API'den dinamik olarak çekilmektedir
- Uçuşlar arası mesafe hesaplaması, havalimanı koordinatları API'den alınarak yapılır
- Tüm tahminler ve oranlar, Python tabanlı model API'den alınır
- Detay kutusu sadece ilgili etikete tıklanınca açılır ve animasyonludur
- Kodda modern React ve fonksiyonel component yapısı kullanılmıştır

## Katkı ve Lisans
Katkıda bulunmak isterseniz lütfen bir pull request açın. Lisans bilgisi için projenin sahibine danışınız.

---

**Hazırlayanlar:** Nuri Can Birdemir - Eda Nur Mutlu