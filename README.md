# Riemann Zeta Sıfır Avcısı & Hipotez Test İstasyonu

Bu proje, Riemann Zeta fonksiyonunun sıfırlarını yüksek hassasiyetle (20 basamak) hesaplayan, görselleştiren ve aynı zamanda **Riemann Hipotezi'ni çürütme potansiyelini** arka planda test eden açık kaynaklı bir Python uygulamasıdır.

## Özellikler

- **Yüksek Hassasiyetli Hesaplama:** `mpmath` kütüphanesi kullanılarak, karmaşık düzlemde virgülden sonra 20 basamak hassasiyetle işlem yapılır.
- **Çift Görevli Motor (Multithreading):** 
  1. Ön planda görülebilen asıl görev: `Re=0.5` (Kritik Doğru) üzerindeki sıfırları bulur.
  2. Arka plan gizli görevi: `Re=0.3, 0.4, 0.6, 0.7` gibi kritik doğru dışındaki ihtimalleri test eder. Eğer buralarda bir sıfır bulursa **Kırmızı Alarm** verir.
- **Görselleştirme:** Bulunan sıfırlar `matplotlib` kullanılarak anlık olarak grafiğe dökülür. Sıfır yoğunluğu ve karmaşık düzlemdeki dağılım canlı olarak izlenebilir.
- **İnteraktif Arayüz:** Sol tık ile zoom yapma, sağ tık ile uzaklaşma ve tablodaki bir değere çift tıklayarak o sıfıra odaklanma özellikleri mevcuttur.
- **Hata Payı (Epsilon) Kontrolü:** Bulunan her sıfır, `1e-10` hata payı eşiği ile test edilir. Sadece bu eşiği geçenler listelenir.

## Kurulum

Projenin çalışması için Python 3.8+ sürümüne ve aşağıdaki kütüphanelere ihtiyacınız vardır. Terminalinizde şu komutu çalıştırın:

```bash
pip install mpmath matplotlib numpy
