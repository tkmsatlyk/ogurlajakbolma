#!/usr/bin/env python3
"""
26 GÜNLÜK SAYAÇ
- Her gün otomatik olarak 1 azalır
- GÜN 0'A ULAŞTIĞINDA:
  * Sub2'deki TÜM VPN linklerini sil
  * Yeni rastgele VLESS protokolü oluştur (26 adet)
  * 26 günü yeniden başlat
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
    """Rastgele VLESS protokolü oluştur"""
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

def delete_all_vpn_links(content):
    """Tüm VPN linklerini sil (vless://, ss://, vmess://, trojan://)"""
    lines = content.split('\n')
    filtered_lines = []
    
    for line in lines:
        if (line.strip().startswith('vless://') or 
            line.strip().startswith('ss://') or 
            line.strip().startswith('vmess://') or
            line.strip().startswith('trojan://')):
            continue
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def update_countdown():
    """Sayacı güncelle - GÜN 0'A ULAŞIRSA YENİ VLESS OLUŞTUR"""
    start_date = load_limit_date()
    remaining_days = calculate_remaining_days(start_date)
    
    print(f"📅 Başlama Tarihi: {start_date}")
    print(f"⏳ Kalan Gün: {remaining_days}")
    
    # Sub2 dosyasını oku
    with open(SUB2_FILE, 'r', encoding='utf-8') as f:
        sub2_content = f.read()
    
    # **GÜN 0'A ULAŞTI - TÜM LİNKLERİ SİL VE YENİ OLUŞTUR**
    if remaining_days == 0:
        print("🔴 ⚠️  GÜN 0'A ULAŞTI!")
        print("🗑️  Tüm VPN linklerini siliyorum...")
        
        # Tüm VPN linklerini sil
        sub2_content = delete_all_vpn_links(sub2_content)
        
        # Yeni 26 VLESS protokolü oluştur
        print("✨ Yeni 26 VLESS oluşturuluyor...")
        new_vless_links = []
        flags = ["🇷🇺", "🇹🇲", "🇸🇪", "🇹🇷", "🇩🇪", "🇳🇱", "🇺🇸", "🇬🇧", "🇫🇷", "🇮🇹", "🇪🇸", "🇵🇱"]
        countries = ["RUSSIA", "TURKMENISTAN", "SWEDEN", "TURKEY", "GERMANY", 
                    "NETHERLANDS", "UNITED STATES", "UNITED KINGDOM", "FRANCE", "ITALY", "SPAIN", "POLAND"]
        
        for i in range(26):
            vless = generate_random_vless()
            flag = flags[i % len(flags)]
            country = countries[i % len(countries)]
            new_vless_links.append(f"{vless}#{flag} {country}")
        
        # Yeni linkler ekle
        sub2_content += "\n" + "\n".join(new_vless_links) + "\n"
        
        # 26 günü yeniden başlat
        start_date = datetime.now().date()
        save_limit_date(start_date)
        remaining_days = 26
        
        print(f"✅ 26 yeni VLESS oluşturuldu!")
        print(f"✅ Sayaç RESETLENDI: 26 gün başladı!")
    
    # Announce satırını güncelle
    formatted_days = format_days_with_superscript(remaining_days)
    announce_text = f"❌ VPN İŞLEMESE📱BIR AZ GARAŞYP📲OBNAVİT EDIP GORUŇ🦾 【{formatted_days} ᵍᵘⁿ ᵍᵃˡᵈʸ】"
    
    # #announce satırını güncelle
    updated_content = re.sub(
        r'#announce:.*',
        f'#announce: {announce_text}',
        sub2_content
    )
    
    # Sub2 dosyasına yaz
    with open(SUB2_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    if remaining_days == 0:
        print(f"🎉 Sub2 TAMAMEN güncellendi! Yeni 26 gün döngüsü başladı!")
    else:
        print(f"✅ Sub2 güncellendi: {remaining_days} gün kaldı!")

if __name__ == "__main__":
    update_countdown()
