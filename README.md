# 🎵 Antigravity AI Music Studio

AI destekli müzik üretim sistemi — Docker mikro servis mimarisi + Flutter mobil uygulama.

## 🏗️ Mimari

```
mobile-app (Flutter)
    │
    └──► Gateway :8000  (FastAPI — orkestrasyon)
              ├──► lyrics-service :8001   (Qwen2-1.5B — söz yazımı)
              ├──► music-service  :8002   (MusicGen-Small — müzik üretimi)
              ├──► voice-service  :8003   (gTTS — ses sentezi)
              ├──► clone-service  :8004   (Ses profili — stub)
              └──► remix-service  :8005   (Demucs — stem ayrımı)
```

## 🚀 Başlatma

### 1. Gereksinimler
- Docker Desktop (v4+) — çalışıyor olmalı
- Flutter SDK (3.0+)
- Android emülatör veya fiziksel cihaz

### 2. Backend'i başlat (ilk seferde build ~10-20 dk sürer)
```powershell
cd C:\Users\YUNUS\Desktop\AIMUSICSTUDIO
docker-compose up --build -d
```

### 3. Servislerin hazır olduğunu doğrula
```powershell
docker-compose ps
# Veya her servisin docs sayfasını kontrol et:
# http://localhost:8000/docs  ← Gateway
# http://localhost:8001/docs  ← Lyrics
# http://localhost:8002/docs  ← Music
# http://localhost:8003/docs  ← Voice
```

### 4. Flutter uygulamasını başlat
```powershell
cd mobile-app
flutter pub get
flutter run   # Emülatör veya bağlı cihazda
```

> **Not:** Android emülatörde `10.0.2.2` = PC'nin localhost'u.  
> Fiziksel cihazda `10.0.2.2` yerine PC'nin yerel IP adresini kullan (örn. `192.168.1.5`).

## 🛑 Durdurma
```powershell
docker-compose down
```

## 📋 Servis Durumlarını İzleme
```powershell
docker-compose logs -f            # Tüm servisler
docker-compose logs -f gateway    # Sadece gateway
docker-compose logs -f music-service
```

## 🔧 Geliştirme Notları

| Servis | Model | GPU | Notlar |
|--------|-------|-----|--------|
| lyrics-service | Qwen2-1.5B-Instruct | Opsiyonel | İlk çalıştırmada ~3GB indirir |
| music-service | facebook/musicgen-small | Opsiyonel | ~800MB, 10 sn müzik |
| voice-service | gTTS | ❌ | Cloud TTS, internet gerekli |
| clone-service | Stub | ❌ | Demo mod — gerçek klonlama için OpenVoice gerekli |
| remix-service | Demucs htdemucs | Opsiyonel | Stem ayrımı |

## 🎮 Kullanım

1. Uygulamayı aç
2. Şarkın hakkında bir prompt yaz (ör. "a lo-fi beat about rainy nights")
3. Müzik stilini seç
4. **Generate Song** butonuna bas ve bekle (~30-60 sn)
5. Oynatıcı ekranında dinle + şarkı sözlerini gör
