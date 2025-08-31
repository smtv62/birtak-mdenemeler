import requests
import re

# Birleştirilecek M3U afiþ listelerinin URL'leri
# Buraya istediğiniz kadar M3U URL'si ekleyebilirsiniz.
playlist_urls = [
    "https://cine10giris.org.tr/ulusaltv.m3u",
    "https://raw.githubusercontent.com/ahmet21ahmet/F-n/main/scripts%2Fcanli-tv.m3u",
    "https://raw.githubusercontent.com/ahmet21ahmet/Trgoalsvsdengetv/main/Birlesik.m3u",
    "https://andro.kopernik6411.workers.dev/DeaTHLesS-iptv.m3u",
    "https://salamin.kopernik6411.workers.dev/DeaTHLesS-BOTV30.m3u"
]

# Kanallarýn benzersizliðini kontrol etmek için kullanýlacak set
# (Kanal Adý, URL) tuple'larýný saklayacak
unique_channels = set()

# Birleþtirilmiþ M3U içeriðini tutacak liste
merged_content_lines = ["#EXTM3U"]

def get_channel_name(extinf_line):
    """#EXTINF satýrýndan kanal adýný çeker."""
    try:
        # Virgül sonrasýndaki kýsmý al
        return extinf_line.split(',')[-1].strip()
    except:
        return None

print("M3U listeleri indiriliyor ve birleþtiriliyor...")

# Her bir URL için iþlem yap
for url in playlist_urls:
    try:
        print(f"Ýþleniyor: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP hatasý varsa except bloðuna geçer
        
        # Kodlama sorunlarýný önlemek için içeriði doðru þekilde çöz
        response.encoding = response.apparent_encoding or 'utf-8'
        playlist_content = response.text

        lines = playlist_content.split('\n')
        
        # Satýrlarý gezerek kanal bilgilerini ve URL'lerini ayýkla
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                channel_name = get_channel_name(line)
                
                # Bir sonraki satýrýn URL olduðunu kontrol et
                if i + 1 < len(lines) and lines[i+1].strip().startswith("http"):
                    stream_url = lines[i+1].strip()
                    
                    # Eðer kanal daha önce eklenmediyse ekle
                    if (channel_name, stream_url) not in unique_channels:
                        unique_channels.add((channel_name, stream_url))
                        merged_content_lines.append(line)
                        merged_content_lines.append(stream_url)

    except requests.exceptions.RequestException as e:
        print(f"Hata: {url} adresi indirilemedi. Hata: {e}")
    except Exception as e:
        print(f"Bilinmeyen bir hata oluþtu: {e}")

# Birleþtirilmiþ içeriði bir dosyaya yaz
output_filename = "birlesik_liste.m3u"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("\n".join(merged_content_lines))

print(f"\nÝþlem tamamlandý!")
print(f"Toplam {len(unique_channels)} benzersiz kanal bulundu.")
print(f"Birleþtirilmiþ liste '{output_filename}' dosyasýna kaydedildi.")