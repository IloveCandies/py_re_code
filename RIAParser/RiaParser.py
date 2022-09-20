import sys
import asyncio
#bs4 для скрапинга
from bs4 import BeautifulSoup
import time as tm
from datetime import datetime, timedelta
# так как данные генерируюся автоматически и подгружаются через js - requests не подходит 
# приходится имитировать действия в браузере
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# чтобы вручную к хрому не писать путь
from webdriver_manager.chrome import ChromeDriverManager



#через реквесты  не захотели страницы отружаться поэтому вэбдрайвер
options = webdriver.ChromeOptions()
# отключаем неныжные логи в консоли
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--log-level=3')
# чтобы гуи не показывалась
options.add_argument('headless')
options.add_argument("disable-gpu")
driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)

#дататайм возращет числа в формате: n  а не nn (1 а не 01), поэтому поправлем их
def check_len(item):
    if len(item) < 2:
          return "0"+item
    return item

#парсим одну страницу
async def parse_page(url):
    driver.get(url)
    print('\033[92m'+"Парсится:"+url+'\033[0m')
    
    #изначально подгружается только 20 записей чтобы обойти использыем нажатие на кнопку загрузки 
    element = driver.find_element(By.CLASS_NAME,"list-more")
    driver.execute_script("arguments[0].click();", element) 
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    item = driver.find_elements(By.CLASS_NAME,"list-item__date")
    
    # для прогресс бара в консоли, можно убрать
    from progress.bar import IncrementalBar
    bar = IncrementalBar('Прогресс', max = 300)
    
    #скролим до предпоследней записи, чтобы данные подгрузились
    for i in range(300):
        driver.execute_script("arguments[0].scrollIntoView();", item[-2])
        item = driver.find_elements(By.CLASS_NAME,"list-item__date")
        # для прогресс бара в консоли, можно убрать
        bar.next()
    bar.finish()    
    
    #собираем данные 
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = soup.find_all("a", {"class": "list-item__title color-font-hover-only"})
    #  очищенный список заголовков новостей
    #  проверяем что новость точно относится к дате запроса
    list_headers = [head.text for head in data if url in head['href']]
    return list_headers

async def writer(list_headers,name ):
    with open(name, 'w') as f:
        for header in list_headers :
            f.write(f"{header}\n")
    print('\033[92m'+"Заголовки нововстей сохранены в " + name+'\033[0m' +'\n')

#ввод даты в формате "год месяц день" без пробелов и точек  Пример: 20221201
async def parse_news_headers(s_date = "", e_date = ""):
    print('\033[91m'+"Не прерывайте парсер, он сам остановится"+'\033[0m')
    print('\033[33m' +"P.S. [0914/231601.097:ERROR:ssl_client_socket_impl.cc(983)] handshake failed; returned -1, SSL error code 1, net_error -101 НИ НА ЧТО НЕ ВЛИЯЕТ" +'\033[0m')
    #срез 
    start_date = datetime(year=int(s_date[0:4]), month=int(s_date[4:6]), day=int(s_date[6:8]))
    end_date = datetime(year=int(e_date[0:4]), month=int(e_date[4:6]), day=int(e_date[6:8]))
    
    while start_date <= end_date:
        #получаем ссылку
        year, month, day = str(start_date.year),str(start_date.month),str(start_date.day)
        day,month = check_len(day),check_len(month) 
        url = "https://ria.ru/"+year+month+day+"/"
        list_headers = await parse_page(url)
        await writer(list_headers=list_headers,name=year+month+day+'.txt')
        start_date += timedelta(days=1)

#пример работы        
asyncio.run(parse_news_headers("20220913","20220914"))
