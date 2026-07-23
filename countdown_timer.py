#!/usr/bin/env python3
"""
26 GÜNLÜK SAYAÇ - SADECE #announce SAÜRINDaki SAYIYI GÜNCELLE
- #announce: ❌ VPN İŞLEMESE📱BIR AZ GARAŞYP📲OBNAVİT EDIP GORUŇ🦾 【²⁶ ᵍᵘⁿ ᵍᵃˡᵈʸ】
  Bu satırda SADECE SAYIYI DEĞİŞTİR: 26 → 25 → 24 ... → 0
- GÜN 0'A ULAŞIRSA:
  * Sub2'deki TÜM VLESS linklerini sil
  * 1 tane yeni rastgele VLESS oluştur (#sag bolun ile)
  * Sayacı yeniden 26 başlat
"""

import json
import re
import os
from datetime import datetime
import uuid
import random

LIMIT_DATE_FILE = "limit_date.json"
SUB2_FILE = "Sub2"

def load_limit_date():
    """Önceki başlama tarihini yükle"""
    if os.path.exists(LIMIT_DATE_FILE):
        with open(LIMIT_DATE_FILE, 'r') as f:
            data = json.load(f)
            return datetime.strptime(data.get("date", datetime.now().isoformat()), "%Y-%m-%d").date()
    return datetime.now().date()

def save_limit_date(date):
    """Başlama tarihini kaydet"""
    with open(LIMIT_DATE_FILE, 'w') as f:
        json.dump({"date": date.isoformat()}, f)

def calculate_remaining_days(start_date):
    """Kalan gün sayısını hesapla (0-26)"""
    today = datetime.now().date()
    delta = today - start_date
    remaining = 26 - delta.days
    return max(0, remaining)

def generate_random_vless():
    """Rastgele 1 VLESS protokolü oluştur"""
    uuid_val = str(uuid.uuid4())
    ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    port = random.randint(400, 65000)
    vless_url = f"vless://{uuid_val}@{ip}:{port}?encryption=none&security=none&type=tcp&headerType=none"
    return vless_url

def format_days_with_superscript(days):
    """Gün sayısını üst simgelerle formatla (2⁶ gibi)"""
    superscript_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', 
        '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    result = ""
    for char in str(days):
        result += superscript_map.get(char, char)
    return result

def delete_all_vless_links(content):
    """Tüm VLESS linklerini sil"""
    lines = content.split('\n')
    filtered_lines = []
    
    for line in lines:
        if line.strip().startswith('vless://'):
            continue
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def update_countdown():
    """Sayacı güncelle - SADECE #announce satırındaki sayı değişir"""
    start_date = load_limit_date()
    remaining_days = calculate_remaining_days(start_date)
    
    print(f"📅 Başlama Tarihi: {start_date}")
    print(f"⏳ Kalan Gün: {remaining_days}")
    
    # Sub2 dosyasını oku
    with open(SUB2_FILE, 'r', encoding='utf-8') as f:
        sub2_content = f.read()
    
    # **GÜN 0'A ULAŞTI - TÜM VLESS SİL VE 1 YENİ OLUŞTUR**
    if remaining_days == 0:
        print("🔴 ⚠️  GÜN 0'A ULAŞTI!")
        print("🗑️  Tüm VLESS linklerini siliyorum...")
        
        # Tüm VLESS linklerini sil
        sub2_content = delete_all_vless_links(sub2_content)
        
        # 1 yeni VLESS oluştur
        print("✨ Yeni 1 VLESS oluşturuluyor...")
        new_vless = generate_random_vless()
        new_vless_line = f"{new_vless}#sag bolun\n"
        
        # Boş satırlardan sonra yeni linki ekle
        sub2_content += "\n" + new_vless_line
        
        # 26 günü yeniden başlat
        start_date = datetime.now().date()
        save_limit_date(start_date)
        remaining_days = 26
        
        print(f"✅ 1 yeni VLESS oluşturuldu!")
        print(f"✅ Sayaç RESETLENDI: 26 gün başladı!")
    
    # #announce satırındaki SADECE SAYIYI GÜNCELLE
    formatted_days = format_days_with_superscript(remaining_days)
    
    # Regex: 【[üst simgeler] ᵍᵘⁿ ᵍᵃˡᵈʸ】 formunu bul ve SADECE sayıyı değiştir
    updated_content = re.sub(
        r'【[⁰¹²³⁴⁵⁶⁷⁸⁹]+ ᵍᵘⁿ ᵍᵃˡᵈʸ】',
        f'【{formatted_days} ᵍᵘⁿ ᵍᵃˡᵈʸ】',
        sub2_content
    )
    
    # Sub2 dosyasına yaz
    with open(SUB2_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    if remaining_days == 0:
        print(f"🎉 Sub2 güncellendi! SIFIR gün - 1 yeni VLESS oluşturuldu!")
    else:
        print(f"✅ #announce satırında sayı güncellendi: {remaining_days} gün")

if __name__ == "__main__":
    update_countdown()
