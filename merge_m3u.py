import requests
import re
from collections import defaultdict

# Birleştirilecek M3U afiş listelerinin URL'leri
playlist_urls = [
    "https://cine10giris.org.tr/ulusaltv.m3u",
    "https://raw.githubusercontent.com/ahmet21ahmet/F-n/main/scripts%2Fcanli-tv.m3u",
    "https://raw.githubusercontent.com/ahmet21ahmet/Trgoalsvsdengetv/main/Birlesik.m3u",
    "https://andro.kopernik6411.workers.dev/DeaTHLesS-iptv.m3u",
    "https://salamin.kopernik6411.workers.dev/DeaTHLesS-BOTV30.m3u"
]

# Kanalları kategorize etmek için kullanılacak anahtar kelimeler
# Sıralama önemlidir; ilk eşleşme kullanılır.
CATEGORIES = {
    "Spor": ["spor", "sport", "bein", "ssport", "tivibu", "d-smart", "fb tv", "gs tv", "bjk tv"],
    "Haber": ["haber", "news", "cnn", "ntv", "habertürk", "halk tv", "sözcü", "tele1", "ulusal kanal", "üLKE TV"],
    "Belgesel": ["belgesel", "documentary", "nat geo", "national geographic", "discovery", "animal planet"],
    "Sinema": ["sinema", "film", "movie", "cinema", "tv+", "filmbox"],
    "Çocuk": ["çocuk", "kids", "minika", "disney", "cartoon", "nick", "trt çocuk"],
    "Müzik": ["müzik", "music", "kral", "power", "dream", "mtv", "number 1"],
    "Dini": ["diyanet", "semerkand", "lalegül"],
    "Ulusal": ["trt 1", "show", "star", "atv", "kanal d", "fox", "tv8", "kanal 7", "beyaz tv", "360"],
}
DEFAULT_CATEGORY = "Diğer Kanallar"

# Kanalların benzersizliğini kontrol etmek için kullanılacak set
# (Kanal Adı, URL) tuple'larını saklayacak
unique_channels_set = set()

# Kategorize edilmiş kanalları tutacak dictionary
# defaultdict, anahtar yoksa otomatik olarak boş bir liste oluşturur.
categorized_channels = defaultdict(list)

def get_channel_info(extinf_line):
    """#EXTINF satırından kanal adını ve diğer bilgileri çeker."""
    try:
        parts = extinf_line.split(',', 1)
        # tvg-id, tvg-logo gibi bilgileri içeren kısım
        attributes = parts[0] 
        # Kanalın asıl adı
        name = parts[1].strip()
        return name, attributes
    except IndexError:
        return None, None

def categorize_channel(channel_name):
    """Verilen kanal adına göre bir kategori döndürür."""
    channel_name_lower = channel_name.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in channel_name_lower for keyword in keywords):
            return category
    return DEFAULT_CATEGORY

print("M3U listeleri indiriliyor ve birleştiriliyor...")

# Her bir URL için işlem yap
for url in playlist_urls:
    try:
        print(f"İşleniyor: {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        playlist_content = response.text
        lines = playlist_content.split('\n')
        
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                channel_name, attributes = get_channel_info(line)
                
                if channel_name and i + 1 < len(lines) and lines[i+1].strip().startswith("http"):
                    stream_url = lines[i+1].strip()
                    
                    if (channel_name, stream_url) not in unique_channels_set:
                        unique_channels_set.add((channel_name, stream_url))
                        
                        # Kanalı kategorize et
                        category = categorize_channel(channel_name)
                        
                        # Kanal bilgilerini sözlüğe ekle
                        channel_data = {
                            "name": channel_name,
                            "attributes": attributes,
                            "url": stream_url
                        }
                        categorized_channels[category].append(channel_data)

    except requests.exceptions.RequestException as e:
        print(f"Hata: {url} adresi indirilemedi. Hata: {e}")
    except Exception as e:
        print(f"Bilinmeyen bir hata oluştu: {url} işlenirken hata: {e}")

print("\nKategorizasyon tamamlandı. Çıktı dosyası oluşturuluyor...")

# Birleştirilmiş ve kategorize edilmiş içeriği bir dosyaya yaz
output_filename = "birlesik_liste.m3u"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    
    # Kategorileri (ve kanalları) alfabetik olarak sırala
    for category in sorted(categorized_channels.keys()):
        print(f"- {category}: {len(categorized_channels[category])} kanal bulundu.")
        # Her kategorideki kanalları isme göre sırala
        sorted_channels = sorted(categorized_channels[category], key=lambda x: x['name'])
        
        for channel in sorted_channels:
            # group-title özelliğini #EXTINF satırına ekle
            extinf_line = f'{channel["attributes"]} group-title="{category}",{channel["name"]}'
            f.write(extinf_line + "\n")
            f.write(channel["url"] + "\n")

print(f"\nİşlem tamamlandı!")
print(f"Toplam {len(unique_channels_set)} benzersiz kanal bulundu.")
print(f"Birleştirilmiş ve kategorize edilmiş liste '{output_filename}' dosyasına kaydedildi.")