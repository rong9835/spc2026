# 툴들 추가
# 1. 네이버 뉴스를 가져온다. 배웠음 (API-key)
# 2. 구글 검색으로 기업 개요/최근 정보를 조회한다. 배웠음 (API-key)
# 3. 환율을 조회한다.
# 4. 주가를 조회한다.

from dotenv import load_dotenv


from langchain_core.tools import tool

# pip install yfinance
import yfinance as yf
import os
import requests
from langchain_tavily import TavilySearch


load_dotenv()

client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')


@tool
def get_news(query: str) -> str:
    """네이버 뉴스 API로 뉴스를 검색한다. 예) '삼성전자', '엔비디아'"""
    url = 'https://openapi.naver.com/v1/search/news.json'

    headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}

    params = {'query': query}

    response = requests.get(url, headers=headers, params=params)
    # print(response)
    data = response.json()

    return data


@tool
def get_company_info(query: str) -> str:
    """구글 검색으로 기업 개요와 최근 정보를 조회한다. 예) '삼성전자', '엔비디아'"""
    web_search = TavilySearch(max_results=3)
    result = web_search.invoke(query)
    return result


@tool
def get_exchange_rate(currency: str) -> str:
    """환율을 조회한다. 예) 'USD' 달러, 'JPY' 엔화, 'EUR' 유로"""
    url = f'https://open.er-api.com/v6/latest/{currency}'
    response = requests.get(url)
    data = response.json()
    return data


@tool
def get_stock_price(ticker: str) -> str:
    """yfinance 로 다양한 기업의 주가를 가져온다.
    예) 애플('AAPL') 과 삼성전자('005930.KS')"""
    # pip install yfinance

    data = yf.Ticker(ticker).history(period='1d')

    return data.to_string()


TOOLS = [get_news, get_company_info, get_exchange_rate, get_stock_price]

if __name__ == '__main__':
    result = get_news.invoke({'query': '삼성전자'})
    print(result)
    print('=' * 60)
    result2 = get_company_info.invoke({'query': '삼성전자'})
    print(result2)
    print('=' * 60)
    result3 = get_exchange_rate.invoke({'currency': 'KRW'})
    print(result3)
    print('=' * 60)
    result4 = get_stock_price.invoke({'ticker': 'AAPL'})
    print(result4)
