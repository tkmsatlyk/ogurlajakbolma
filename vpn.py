import json, os, subprocess, urllib.request, zipfile
xray_dir = os.path.expanduser("~/.xray")
os.makedirs(xray_dir, exist_ok=True)
if not os.path.exists(f"{xray_dir}/xray"):
    urllib.request.urlretrieve("https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip", f"{xray_dir}/xray.zip")
    with zipfile.ZipFile(f"{xray_dir}/xray.zip", 'r') as z: z.extractall(xray_dir)
    os.chmod(f"{xray_dir}/xray", 0o755)

uid, port = "12345678-1234-5678-1234-567812345678", 10000

cfg = {"log":{"loglevel":"warning"},"inbounds":[{"port":port,"protocol":"vless","settings":{"clients":[{"id":uid,"flow":""}],"decryption":"none"},"streamSettings":{"network":"ws","wsSettings":{"path":"/ray"}}}],"outbounds":[{"protocol":"freedom"}]}
json.dump(cfg, open(f"{xray_dir}/config.json", "w"), indent=4)
subprocess.Popen(f"{xray_dir}/xray run -c {xray_dir}/config.json &", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
cname = os.environ.get("CODESPACE_NAME")
url = f"{cname}-{port}.app.github.dev" if cname else "URL_YOK"
print("\n" + "="*50)
print("🎉 HATASIZ VLESS LİNKİN:")
print("="*50)
print(f"vless://{uid}@{url}:443?encryption=none&security=tls&type=ws&host={url}&path=/ray#TURKMEN_VPN")
print("="*50)
