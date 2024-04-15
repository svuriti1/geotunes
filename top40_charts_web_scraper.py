import requests
from bs4 import BeautifulSoup
import sys
import pandas as pd
from csv import writer

def main():
    if(len(sys.argv) != 3):
        print("How to use: This web scraper works specifically for https://top40-charts.com/\n")
        print("This program requires two arguments: the link to a chart (make sure the link includes the date of the chart) and the name of the country")
        exit()
    URL = str(sys.argv[1])
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    if page.status_code == 200:
        results = soup.find_all("select")
        date_list = []
        for i in results[1]:
            date = i.text
            split_date = date.split('-')
            date_list.append(str(split_date[2] + '-' + split_date[1] + '-'+ split_date[0]))
        #split the url
        split_URL = URL.split("&date=")[0]
        c = 1
        for date in date_list:
            
            check_url = split_URL + str("&date=") + str(date)
            #now do the process
            nURL = str(check_url)
            page = requests.get(nURL)
            soup = BeautifulSoup(page.content, "html.parser")
            if page.status_code == 200:
                results = soup.find_all("tr", class_="latc_song")
                count = 1
                for song in results:
                    stuff = song.find_all("a")
                    song_name = ""
                    artist_name = ""
                    if len(stuff) > 3:
                        artist_name = stuff[3].text.strip()
                        song_name = stuff[2].text.strip()
                    else:
                        artist_name = stuff[2].text.strip()
                        song_name = ""
                    with open('top40-charts-data.csv','a') as df:
                        List = [count, song_name, artist_name, sys.argv[2], date]
                        writer_object = writer(df)
                        writer_object.writerow(List)
                    count = count + 1
            else:
                print("Failure at: " + check_url)
            print(str(c) + "/" +str(len(date_list)))
            c = c+1
    print(sys.argv[2])

if __name__ == "__main__":
    main()
    