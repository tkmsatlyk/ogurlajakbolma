const fs = require('fs');
const path = './subscription.json';

// 5 dakikada eklenecek miktar
const ADD_AMOUNT_MB = 6.37;

function updateSubscription() {
  let data = {
    subscription: {
      total_mb: 0,
      last_updated: null
    }
  };

  // Eğer dosya mevcutsa var olan veriyi oku
  if (fs.existsSync(path)) {
    try {
      const fileContent = fs.readFileSync(path, 'utf8');
      data = JSON.parse(fileContent);
    } catch (error) {
      console.error("JSON dosyası okunurken hata oluştu, yeni oluşturuluyor.", error);
    }
  }

  // Mevcut MB değerine 6.37 MB ekle
  const currentMb = data.subscription.total_mb || 0;
  const newTotal = parseFloat((currentMb + ADD_AMOUNT_MB).toFixed(2));

  // Veriyi güncelle
  data.subscription.total_mb = newTotal;
  data.subscription.last_updated = new Date().toISOString();

  // Dosyaya yaz
  fs.writeFileSync(path, JSON.stringify(data, null, 2));

  console.log(`[BAŞARILI] Aboneliğe ${ADD_AMOUNT_MB} MB eklendi.`);
  console.log(`Güncel Toplam: ${newTotal} MB`);
}

updateSubscription();
