const fs = require('fs');
// Dosya adını senin oluşturduğun "sub" olarak değiştirdik
const path = './sub';

// 5 dakikada eklenecek miktar
const ADD_AMOUNT_MB = 6.37;

function updateSubscription() {
  let data = {
    subscription: {
      total_mb: 0,
      last_updated: null
    }
  };

  // Eğer sub dosyası mevcutsa oku
  if (fs.existsSync(path)) {
    try {
      const fileContent = fs.readFileSync(path, 'utf8');
      // Dosya boş değilse JSON olarak oku
      if (fileContent.trim() !== "") {
        data = JSON.parse(fileContent);
      }
    } catch (error) {
      console.error("sub dosyası okunurken hata oluştu, varsayılan yapı kullanılıyor.", error);
    }
  }

  // Mevcut MB değerine 6.37 MB ekle
  const currentMb = (data.subscription && data.subscription.total_mb) || 0;
  const newTotal = parseFloat((currentMb + ADD_AMOUNT_MB).toFixed(2));

  // Veriyi güncelle
  data.subscription = {
    total_mb: newTotal,
    last_updated: new Date().toISOString()
  };

  // sub dosyasına yaz
  fs.writeFileSync(path, JSON.stringify(data, null, 2));

  console.log(`[BAŞARILI] 'sub' dosyasına ${ADD_AMOUNT_MB} MB eklendi.`);
  console.log(`Güncel Toplam: ${newTotal} MB`);
}

updateSubscription();
