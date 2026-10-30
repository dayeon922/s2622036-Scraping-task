from bs4 import BeautifulSoup
import csv
import time
import requests
from urllib.parse import urljoin, urlparse

base_url = 'https://www.musashino-u.ac.jp'
domain = urlparse(base_url).netloc

MAX_PAGES = 1100       # 1000건 이상 모이도록 약간 여유
SAVE_EVERY = 100
SKIP_EXT = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip',
            '.xlsx', '.xls', '.docx', '.doc', '.pptx', '.mp4', '.svg')

csv_filename = 'musashino_u_sitemap.csv'

visited = set()
queued = {base_url}
queue = [base_url]
url_title_dict = {}


def save_csv():
  with open(csv_filename, mode='w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['URL', 'Title'])
    for u, t in url_title_dict.items():
      writer.writerow([u, t])


print("--- 무사시노 대학 웹사이트 스크래핑 시작 ---")

try:
  while queue and len(url_title_dict) < MAX_PAGES:
    current_url = queue.pop(0)

    if current_url in visited:
      continue

    try:
      res = requests.get(current_url, timeout=(5, 15))
      if res.status_code != 200:
        print(f"상태 코드 {res.status_code}: {current_url}")
        continue

      # HTML이 아닌 응답(PDF 등)은 건너뜀
      if 'text/html' not in res.headers.get('Content-Type', ''):
        continue

      res.encoding = 'utf-8'
      visited.add(current_url)   # 성공했을 때만 방문 처리
      html_soup = BeautifulSoup(res.text, 'html.parser')

      title_tag = html_soup.find('title')
      if title_tag and title_tag.string:
        title_text = title_tag.string.strip()
      else:
        title_text = 'No Title'

      url_title_dict[current_url] = title_text
      print(f"수집 완료 [{len(url_title_dict)}]: {current_url} -> {title_text}")

      for a in html_soup.find_all('a', href=True):
        full_url = urljoin(current_url, a['href'])
        parsed_full = urlparse(full_url)
        clean_url = (
            f'{parsed_full.scheme}://{parsed_full.netloc}{parsed_full.path}'
        )

        if parsed_full.netloc != domain:
          continue
        if clean_url.lower().endswith(SKIP_EXT):
          continue
        if clean_url in visited or clean_url in queued:
          continue

        queue.append(clean_url)
        queued.add(clean_url)

      if len(url_title_dict) % SAVE_EVERY == 0:
        save_csv()

      time.sleep(1)

    except Exception as e:
      print(f"에러 발생 URL ({current_url}): {e}")

except KeyboardInterrupt:
  print("\n사용자가 중단했습니다. 지금까지 수집한 결과를 저장합니다.")

save_csv()
print(f"\n스크래핑 완료! {len(url_title_dict)}개가 '{csv_filename}'에 저장되었습니다.")