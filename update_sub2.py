#!/usr/bin/env python3
"""
Sub2 Gün Sayacı Güncelleyici
Her çalıştırıldığında (cron job ile 24 saatte bir):
1. limit_date.json'dan başlama tarihini kontrol et
2. Kalan gün sayısını hesapla
3. #announce satırını güncelle
4. Gün 0'a ulaşırsa tüm linkler silinip yeni VLESS oluşturulur
"""

import sys
import os

# countdown_timer.py'i import et
from countdown_timer import update_countdown

if __name__ == "__main__":
    try:
        update_countdown()
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)
