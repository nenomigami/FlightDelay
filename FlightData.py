# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 00:53:31 2018

@author: nenom
"""

from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import date
import datetime
import csv
import numpy as np
import pandas as pd
import time

#크롬 드라이버
DRIVER_PATH = r'C:/Users/nenom/webdriver/chromedriver.exe' 

#URL
URL = "http://www.airportal.go.kr/life/airinfo/RbHanFrm.jsp"

#변수
COL = ["Airline","Name","Departure","Plan","Expectation","Arrival","Kind","Situation"]




def sourceEachPage(date,browser): #date 날 페이지의 소스를 불러오는 함수
    date_block = browser.find_element_by_css_selector('input[type = "text"]') #날짜 칸 선택
    browser.implicitly_wait(5)#5초 대기
    
    date_block.clear() #지우기
    browser.implicitly_wait(5)#5초 대기
    
    date_block.send_keys(date) # 날짜칸에 쓰기
    browser.implicitly_wait(5)#5초 대기
    
    browser.find_element_by_css_selector('a[href = "javascript:go_search()"]').click()# 날짜변경 클릭
    browser.implicitly_wait(5)#5초 대기
    
    frame = browser.find_element_by_css_selector('IFRAME[name="sframe"]')
    browser.switch_to.frame(frame)
    
    outerFrame = browser.find_element_by_css_selector('table[width="100%"][border="0"]')
    source = outerFrame.get_attribute('innerHTML')
    return(source)

def clearRow(lines):# 표의 행을 구성하는 소스 중 실제 표에 나타난 부분만 넣음
    table_line = []
    for line in lines:
        if len(line.findChildren()) > 10 :#안에 내용이 많으면 넣고 아니면 빼고
            table_line.append(line)
    return(table_line)
    

def clearCol(Row):# 한 행의 열을 구성하는 소스 중 실제 표에 나타난 부분만 넣음
    cells = Row.findChildren()
    newRow = []
    for cell in cells:
        content = cell.text.strip()
        content = content.replace('\xa0',"")
        if len(content) != 0:
            newRow.append(content)
    return(newRow)

def makeTable(table_line): #정리된 열들을 데이터프레임으로 만듬
    result = [] 
    for i in range(len(table_line)):
       newRow = clearCol(table_line[i])
       result.append(pd.DataFrame(newRow).T)
    return(pd.concat(result))
    

yesterday = date.today() - datetime.timedelta(days = 1)
def getFlightDelayTable(years = 5, startDate = yesterday):
    #years : 몇 개년 어치 데이터를 수집할 것인지 (default = 5년)
    #startDate : 며칠부터 데이터를 수집할 것인지(default = 어제)

    date = startDate
    endDate = startDate - datetime.timedelta(days = 365 * years)
    
    
    browser = webdriver.Chrome(executable_path=DRIVER_PATH)
    browser.get(URL)
    browser.implicitly_wait(10)#15초 대기
            
    with open("C:/Users/nenom/Desktop/FlightDelay.csv",'w',newline = '') as csvfile:
        wr = csv.writer(csvfile)
        wr.writerow(COL)
        while date != endDate:
            day = date.strftime('%Y%m%d')
            source = sourceEachPage(day,browser)
            soup = BeautifulSoup(source)
            lines = soup.findAll("tr") #tr 다 골라냄
            table_line = clearRow(lines)
            table = makeTable(table_line)
            trim_table = table.iloc[:,1:9]
            trim_table.columns = COL    
            trim_table["Date"] = date.strftime('%Y-%m-%d')
            
            for row in trim_table.values.tolist():
                wr.writerow(row)
            time.sleep(10)
            browser.implicitly_wait(10)
            browser.switch_to.default_content()
            date = date - datetime.timedelta(days = 1)
        
getFlightDelayTable(1)


#샘플코드
"""
def makeDf(df):
    result = []
    for i in range(10):
        result.append(df[i])
    return pd.concat(result)
"""   
