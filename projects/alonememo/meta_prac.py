import requests
from bs4 import BeautifulSoup

url = 'https://platum.kr/archives/120958'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(url, headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

# 여기에 코딩을 해서 meta tag를 먼저 가져와보겠습니다.

og_title = soup.select_one('meta[property="og:title"]')
og_image = soup.select_one('meta[property="og:image"]')
og_description = soup.select_one('meta[property="og:description"]')

print(og_title['content'])
print(og_image['content'])
print(og_description['content'])