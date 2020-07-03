# German-Top100

Python application which web scrapes the [German Top 100 Single Charts](https://www.offiziellecharts.de) for every week in 2019 using BeautifulSoup.

The web scraped song information is then stored to a .csv file named 2019_top_100.csv.

```
filename = '2019_top_100.csv'
```

### .csv Headers:

- Artist name
- Song title
- Label name
- Chart position
- Start date of the week
- End date of the week
- Calender week
