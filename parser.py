import csv
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd


ITEMS = 20
URL = f'https://hh.ru/search/vacancy?items_on_page={ITEMS}&area=113&st=searchVacancy&text=python'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}


def extract_last_page():
    request = requests.get(URL, headers=headers)
    soup = bs(request.text, 'html.parser')
    pages = []
    paginator = soup.find_all("span", {'class': 'pager-item-not-in-short-range'})
    for page in paginator:
        pages.append(int(page.find('a').text))
    return pages[-1]


def extract_job(html):
    title = html.find('a', {'class': 'bloko-link'}).text.strip()
    link = html.find('a', {'class': 'bloko-link'})['href'].replace('?query=python&hhtmFrom=vacancy_search_list', '')
    # link_c = f'=ГИПЕРССЫЛКА("{link}")'
    company = html.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).text.strip().replace('\xa0', ' ')
    location = html.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text.partition(',')[0]
    return {'title': title, 'company': company, 'location': location, 'link': link}


def extract_hh_jobs(last_page):
    jobs = []
    for page in range(last_page):
        print(f'Parse page {page}')
        result = requests.get(f'{URL}&page={page}', headers=headers)
        # print(result.status_code)
        soup = bs(result.text,'html.parser')
        results = soup.find_all('div', {'class':'serp-item serp-item_link'})
        # print(results)
        for result in results:
          jobs.append(extract_job(result))
    return jobs


def save_to_csv(jobs):
   with open('hh.csv', 'w', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow(['Вакансия', 'Компания', 'Месторасположение', 'Ссылка на вакансию'])
      for job in jobs:
          writer.writerow(list(job.values()))
   return


def csv_to_excel():
    df = pd.read_csv("hh.csv", encoding='utf-8')
    df.to_excel("hh_vacan.xlsx", index=False)


save_to_csv(extract_hh_jobs(extract_last_page()))
csv_to_excel()



