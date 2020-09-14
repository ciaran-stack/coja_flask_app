import requests
from bs4 import BeautifulSoup
import pandas as pd

annual_10k = []  # list for only 10k document directory links
document = []  # list will contain dated tuples with links
analysis_links = []  # this list will be tuples of year stamps and 10k links
analysis_data = []  # this list will contain all sentences that contain a keyword
inx_lst = []  # get year stamp and keyword that was found for multi index


def find_10k(search_firm, file):

    data = file
    for (tick, cik) in zip(data["Ticker"], data["CIK"]):
        if tick == search_firm:
            usable_cik = cik
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={usable_cik}&type=10-K&dateb=&owner=exclude&count=100"
            print(url)

            # get url for a specific company
            response = requests.get(url)
            response_text = response.text

            # convert to lxml format to make parsing easier
            html_soup = BeautifulSoup(response_text, 'lxml')
            raw_table = html_soup.find('table', {'class': 'tableFile2'})

            # variable used to find documents button
            documents = raw_table.find_all('a', {'id': 'documentsbutton'})
            for links in documents:
                doc_link = links['href']
                annual_10k.append(doc_link)


def assign_date():

    twenty_fist = ['-00-', '-01-', '-02-', '-03-', '-04-', '-05-', '-06-', '-07-', '-08-', '-09-', '-10-', '-11-',
                   '-12-', '-13-', '-14-', '-15-', '-16-', '-17-', '-18-', '-19-', '-20-']

    twentieth = ['-93-', '-94-', '-95-', '-96-', '-97-', '-98-', '-99-']

    for link in annual_10k:  # loop through the annual_10l list

        for value in twenty_fist:  # loop through values in 21st list
            print(link)
            if value in link:
                year_digits = value[1:3]  # grab the two digits that represent the year
                year = f"20{year_digits}"
                items = (year, link)  # create tuple with link and date
                document.append(items)

        for value in twentieth:  # loop through values in 20th list
            if value in link:
                year_digits = value[1:3]  # grab the two digits that represent the year
                year = f"19{year_digits}"
                items = (year, link)  # create tuple with link and date
                document.append(items)


def analyze_urls(start, end):
    for item in document:  # get url for 10k html per year
        if int(item[0]) in range(start, (end+1)):
            url = f'https://www.sec.gov/{item[1]}'  # item = (year, url)
            response = requests.get(url)
            response_text = response.text

            # convert to lxml format to make parsing easier
            html_soup = BeautifulSoup(response_text, 'lxml')
            data_table = html_soup.find('table', {'class': 'tableFile'})  # grab the table with all files

            # grab all of the standard data tags within the table
            standard_table_data = data_table.find_all('td')
            get_link = standard_table_data[2]  # 10-k link is always the in the second td tag
            link = get_link.find('a')['href']  # get the a tag for the second piece of standard table data

            if '/ix?doc=' in link:  # cleans up link so it is not using the iXBRL format
                html_convert = link.split("=")
                analysis = (item[0], html_convert[1])
                # append all year stamps and links into a global list
                analysis_links.append(analysis)

            else:
                analysis_source = (item[0], link)
                # append all year stamps and links into a global list
                analysis_links.append(analysis_source)


def searchable_10k(kw, excel_name):
    print(analysis_links)
    for link in analysis_links:  # for loop through all the key 10k links
        url = f'https://www.sec.gov{link[1]}'
        response = requests.get(url)
        response_text = response.text

        html_soup = BeautifulSoup(response_text, 'lxml')
        full_text = html_soup.text  # print out all text
        search_text = full_text.lower().split(".")  # split text based on periods
        for sentence in search_text:  # iterate through each sentence
            for k in kw:  # iterate through the each keyword
                if k in sentence:  # is the keyword in each sentence that is being analyzed
                    inx = (link[0], k)  # need data in a tuple for a multi index data frame
                    inx_lst.append(inx)  # append tuples to list to determine outer and inner index
                    analysis_data.append(sentence)

    index = pd.MultiIndex.from_tuples(inx_lst, names=['Year', 'Keyword Found'])  # set outer and inner index
    df = pd.DataFrame(analysis_data, columns=['Sentence with Keyword'], index=index)  # create data frame
    df.to_excel(f"{excel_name}.xlsx")  # write data frame to an excel sheet


if __name__ == '__main__':

    search = 'AAPL'.lower()  # What firm are we analyzing
    csv_file = pd.read_csv("ticker.csv")  # read the CSV file to find the correct CIK number
    find_10k(search, csv_file)

    assign_date()  # pull all links for

    print("Please input the start and end range of 10ks you would like to search!")
    start_year_input = int(input("Start: "))  # start parameter
    end_year_input = int(input("End: "))  # end parameter
    analyze_urls(start=start_year_input, end=end_year_input)

    # list of keywords that are going to be used for the analysis of the 10Ks
    keyword = ['transformation', 'cloud', 'revenue streams', 'new product', 'it initiative']

    searchable_10k(keyword, excel_name=search)
