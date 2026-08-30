import HappProcessor from "node-happ-decryptor";

console.log("Paket başarıyla yüklendi.");
console.log("Constructor:", typeof HappProcessor);
console.log(
  "Prototype metodları:",
  Object.getOwnPropertyNames(HappProcessor.prototype)
);
