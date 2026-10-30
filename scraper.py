from bs4 import BeautifulSoup
import csv
import time
import requests
from urllib.parse import urljoin, urlparse

base_url = 'https://www.musashino-u.ac.jp'
domain = urlparse(base_url).netloc

MAX_PAGES = 300  # 최대 수집 개수 (필요에 따라 조절)

visited = set()
queue = [base_url]
url_title_dict = {}

print("--- 무사시노 대학 웹사이트 스크래핑 시작 ---")

try:
  while queue and len(visited) < MAX_PAGES:
    current_url = queue.pop(0)

    if current_url in visited:
      continue

    try:
      res = requests.get(current_url, timeout=10)
      if res.status_code != 200:
        continue

      res.encoding = 'utf-8'
      visited.add(current_url)

      html_soup = BeautifulSoup(res.text, 'html.parser')

      title_tag = html_soup.find('title')
      if title_tag and title_tag.string:
        title_text = title_tag.string.strip()
      else:
        title_text = 'No Title'

      url_title_dict[current_url] = title_text
      print(f"수집 완료 [{len(visited)}]: {current_url} -> {title_text}")

      a_list = html_soup.find_all('a', href=True)

      for a in a_list:
        href = a['href']
        full_url = urljoin(current_url, href)

        parsed_full = urlparse(full_url)
        clean_url = (
            f'{parsed_full.scheme}://{parsed_full.netloc}{parsed_full.path}'
        )

        if parsed_full.netloc == domain and clean_url not in visited:
          if clean_url not in queue:
            queue.append(clean_url)

      # 과제 요구사항: 서버 부하 경감
      time.sleep(1)

    except requests.RequestException as e:
      print(f"에러 발생 URL ({current_url}): {e}")

except KeyboardInterrupt:
  print("\n사용자가 중단했습니다. 지금까지 수집한 결과를 저장합니다.")

# CSV 저장
csv_filename = 'musashino_u_sitemap.csv'
with open(csv_filename, mode='w', encoding='utf-8-sig', newline='') as f:
  writer = csv.writer(f)
  writer.writerow(['URL', 'Title'])
  for url, title in url_title_dict.items():
    writer.writerow([url, title])

print(f"\n스크래핑 완료! {len(url_title_dict)}개가 '{csv_filename}'에 저장되었습니다.")