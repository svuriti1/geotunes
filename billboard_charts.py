import billboard
import pandas as pd

if __name__ == '__main__':
    chartList = ["hot-100", "the-arabic-hot-100", "billboard-argentina-hot-100", "billboard-brasil-hot-100", 
                "canadian-hot-100", "billboard-italy-hot-100", "japan-hot-100", "billboard-thailand-top-thai-songs",
                "official-uk-songs", "australia-songs-hotw", "austria-songs-hotw", "belgium-songs-hotw",
                "bolivia-songs-hotw", "chile-songs-hotw", "china-tme-uni-songs", "colombia-songs-hotw", "croatia-songs-hotw",
                "czech-republic-songs-hotw", "denmark-songs-hotw", "ecuador-songs-hotw", "finland-songs-hotw",
                "france-songs-hotw", "germany-songs-hotw", "greece-songs-hotw", "hong-kong-songs-hotw", "hungary-songs-hotw",
                "iceland-songs-hotw", "india-songs-hotw", "indonesia-songs-hotw", "ireland-songs-hotw", "luxembourg-songs-hotw",
                "malaysia-songs-hotw", "mexico-songs-hotw", "netherlands-songs-hotw", "new-zealand-songs-hotw",
                "norway-songs-hotw", "peru-songs-hotw", "philippines-songs-hotw", "poland-songs-hotw", "portugal-songs-hotw",
                "romania-songs-hotw", "singapore-songs-hotw", "slovakia-songs-hotw", "south-africa-songs-hotw",
                "south-korea-songs-hotw", "spain-songs-hotw", "sweden-songs-hotw", "switzerland-songs-hotw", 
                "taiwan-songs-hotw", "turkey-songs-hotw", "u-k-songs-hotw"]

    for i in chartList:
        print("chart ", i)
        chart = billboard.ChartData(i, date=None, year=None, fetch=True, timeout=25)

        titleList = []
        artistList = []
        rankList = []
        for j in chart:
            titleList.append(j.title)
            artistList.append(j.artist)
            rankList.append(j.rank)


        dict = {'Rank': rankList, 'Title': titleList, 'Artist': artistList}
        df = pd.DataFrame(dict)
        outputFile = "billboard/" + i + ".csv"
        df.to_csv(outputFile)