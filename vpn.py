import json, os, subprocess, urllib.request, uuid, zipfile
print("[*] Xray indiriliyor...")
xray_dir = os.path.expanduser("~/.xray")
os.makedirs(xray_dir, exist_ok=True)
urllib.request.urlretrieve("https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip", f"{xray_dir}/xray.zip")
with zipfile.ZipFile(f"{xray_dir}/xray.zip", 'r') as z: z.extractall(xray_dir)
uid, port = str(uuid.uuid4()), 10000
cfg = {"log":{"loglevel":"warning"},"inbounds":[{"port":port,"protocol":"vless","settings":{"clients":[{"id":uid,"flow":""}],"decryption":"none"},"streamSettings":{"network":"ws","wsSettings":{"path":"/ray"}}}],"outbounds":[{"protocol":"freedom"}]}
json.dump(cfg, open(f"{xray_dir}/config.json", "w"), indent=4)
os.chmod(f"{xray_dir}/xray", 0o755)
subprocess.Popen(f"{xray_dir}/xray run -c {xray_dir}/config.json &", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
cname = os.environ.get("CODESPACE_NAME")
url = f"{cname}-{port}.app.github.dev" if cname else "URL_YOK"
print("\n" + "="*50)
print("🎉 VLESS LINKİN AŞAĞIDA:")
print("="*50)
print(f"vless://{uid}@{url}:443?encryption=none&security=tls&type=ws&host={url}&path=/ray#TURKMEN_VPN")
print("="*50)

