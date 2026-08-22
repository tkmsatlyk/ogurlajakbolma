import HappProcessor from 'node-happ-decryptor';
import net from 'net';
import https from 'https';
import http from 'http';
import fs from 'fs';

const customNames = [
    "🔥 Pro-VPN-01",
    "⚡ Pro-VPN-02",
    "🚀 Pro-VPN-03",
    "💎 Pro-VPN-04",
    "🌐 Pro-VPN-05",
    "⚡ Pro-VPN-06",
    "🔥 Pro-VPN-07",
    "🚀 Pro-VPN-08",
    "💎 Pro-VPN-09",
    "🌐 Pro-VPN-10"
];

function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        client.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', err => reject(err));
    });
}

async function pingNode(link) {
    try {
        const url = new URL(link);
        const host = url.hostname;
        const port = url.port || (url.protocol === 'https:' ? 443 : 80);
        
        const start = Date.now();
        return new Promise((resolve) => {
            const socket = new net.Socket();
            socket.setTimeout(1500);
            socket.connect(port, host, () => {
                const latency = Date.now() - start;
                socket.destroy();
                resolve(latency);
            });
            socket.on('error', () => { socket.destroy(); resolve(9999); });
            socket.on('timeout', () => { socket.destroy(); resolve(9999); });
        });
    } catch (e) {
        return 9999;
    }
}

async function main() {
    console.log("--- Telegram Kanalı Taranıyor ---");
    let tgHtml;
    try {
        tgHtml = await fetchUrl("https://t.me/s/happvpn");
    } catch (e) {
        console.log("Telegram bağlantı hatası:", e);
        return;
    }

    const happMatches = tgHtml.match(/happ:\/\/[^\s<>"\']+/g);
    if (!happMatches || happMatches.length === 0) {
        console.log("Hiç happ linki bulunamadı.");
        return;
    }

    const latestHapp = happMatches[happMatches.length - 1].replace(/&amp;/g, '&').trim();
    console.log("Bulunan son happ link:", latestHapp);

    let decryptedText = "";
    try {
        const processor = new HappProcessor();
        const result = processor.decrypt(latestHapp);
        decryptedText = result.decryptedData;
        console.log("Yerel Decrypt Başarılı!");
    } catch (e) {
        console.log("Decrypt hatası:", e.message);
        return;
    }

    const httpsMatches = decryptedText.match(/https?:\/\/[^\s<>"\']+/g);
    if (!httpsMatches || httpsMatches.length === 0) {
        console.log("Decrypted veri içinde https linki bulunamadı.");
        return;
    }

    const targetUrl = httpsMatches[0];
    console.log("Bulunan abonelik URL'si:", targetUrl);

    let subContent = "";
    try {
        subContent = await fetchUrl(targetUrl);
    } catch (e) {
        console.log("Abonelik URL'si çekilemedi:", e);
        return;
    }

    let rawConfigs = [];
    try {
        const buff = Buffer.from(subContent.trim(), 'base64');
        const decodedSub = buff.toString('utf-8');
        rawConfigs = decodedSub.match(/(?:vless|vmess|ss|trojan):\/\/[^\s<>"\']+/g) || [];
    } catch (e) {}

    if (rawConfigs.length === 0) {
        rawConfigs = subContent.match(/(?:vless|vmess|ss|trojan):\/\/[^\s<>"\']+/g) || [];
    }

    console.log(`Ham node sayısı: ${rawConfigs.length}`);
    if (rawConfigs.length === 0) return;

    console.log("Ping testleri başlatılıyor (< 1500ms filtreleniyor)...");
    const testedNodes = [];
    for (const config of rawConfigs) {
        const ping = await pingNode(config);
        if (ping < 1500) {
            testedNodes.push({ config, ping });
            console.log(`[PASS] Ping: ${ping}ms`);
        }
    }

    testedNodes.sort((a, b) => a.ping - b.ping);

    const finalLinks = [];
    const topNodes = testedNodes.slice(0, 10);
    
    topNodes.forEach((item, index) => {
        let cleanConfig = item.config.split('#')[0];
        const assignedName = customNames[index] || `Pro-Node-${index + 1}`;
        const renamedConfig = `${cleanConfig}#${encodeURIComponent(assignedName)}`;
        finalLinks.push(renamedConfig);
    });

    if (finalLinks.length > 0) {
        fs.writeFileSync("Toplanan_linkler.txt", finalLinks.join('\n'), 'utf-8');
        console.log(`BAŞARILI: Toplam ${finalLinks.length} adet optimize edilmiş node dosyaya yazıldı.`);
    } else {
        console.log("1500ms altında uygun node bulunamadı.");
    }
}

main();
