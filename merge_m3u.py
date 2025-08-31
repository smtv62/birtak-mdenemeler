import requests
import re
from collections import defaultdict

# Birleştirilecek M3U afiş listelerinin URL'leri
playlist_urls = [
    "https://cine10giris.org.tr/ulusaltv.m3u",
    "https://raw.githubusercontent.com/ahmet21ahmet/F-n/main/scripts%2Fcanli-tv.m3u",
    "https://raw.githubusercontent.com/ahmet21ahmet/Trgoalsvsdengetv/main/Birlesik.m3u"
]

# Kaynakta kategorisi bulunmayan kanallar için varsayılan grup adı
DEFAULT_CATEGORY = "Diğer Kanallar"

# Kanalların benzersizliğini kontrol etmek için kullanılacak set
unique_channels_set = set()

# Kategorize edilmiş kanalları tutacak dictionary
categorized_channels = defaultdict(list)

def parse_extinf_line(line):
    """
    #EXTINF satırını analiz eder. Mevcut group-title'ı, kanal adını ve 
    diğer özellikleri (temizlenmiş halde) ayıklar.
    """
    info = {
        "name": None,
        "category": None,
        "attributes": line
    }
    
    match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
    if match:
        info["category"] = match.group(1).strip()
        info["attributes"] = (line[:match.start()] + line[match.end():]).strip()

    try:
        parts = info["attributes"].rsplit(',', 1)
        info["attributes"] = parts[0]
        info["name"] = parts[1].strip()
    except IndexError:
        info["name"] = info["attributes"].split(' ', 1)[-1]

    return info

print("M3U listeleri indiriliyor ve birleştiriliyor...")

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
                channel_info = parse_extinf_line(line)
                channel_name = channel_info["name"]
                
                if channel_name and i + 1 < len(lines) and lines[i+1].strip().startswith("http"):
                    stream_url = lines[i+1].strip()
                    
                    if (channel_name, stream_url) not in unique_channels_set:
                        unique_channels_set.add((channel_name, stream_url))
                        
                        # ANA MANTIK: Mevcut kategori varsa onu kullan, yoksa varsayılanı ata.
                        category = channel_info["category"]
                        if not category or category.isspace():
                            category = DEFAULT_CATEGORY
                        
                        channel_data = {
                            "name": channel_name,
                            "attributes": channel_info["attributes"],
                            "url": stream_url
                        }
                        categorized_channels[category].append(channel_data)

    except requests.exceptions.RequestException as e:
        print(f"Hata: {url} adresi indirilemedi. Hata: {e}")
    except Exception as e:
        print(f"Bilinmeyen bir hata oluştu: {url} işlenirken hata: {e}")

print("\nKategorizasyon tamamlandı. Çıktı dosyası oluşturuluyor...")

output_filename = "birlesik_liste.m3u"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    
    for category in sorted(categorized_channels.keys()):
        print(f"- {category}: {len(categorized_channels[category])} kanal bulundu.")
        sorted_channels = sorted(categorized_channels[category], key=lambda x: x['name'])
        
        for channel in sorted_channels:
            extinf_line = f'{channel["attributes"]} group-title="{category}",{channel["name"]}'
            f.write(extinf_line + "\n")
            f.write(channel["url"] + "\n")

print(f"\nİşlem tamamlandı!")
print(f"Toplam {len(unique_channels_set)} benzersiz kanal bulundu.")
print(f"Birleştirilmiş ve düzenlenmiş liste '{output_filename}' dosyasına kaydedildi.")