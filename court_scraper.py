# %% [markdown]
# Oregon Case records Scraper
# 
# Scrapes case records from Oregon eCourt to find the latest interesting cases (torts)
# 
# 
# The counties I want: 
# 116100,115100,115200,101100,114100,113100,126100
# 

# %%
# request the required databases
import requests, time, datetime, csv, os

#Setup a session so we can keep the cookies for the next request
s = requests.Session()

#Get the login information from the environment variables
login_password = os.environ.get('LOGIN_PASSWORD')

#define custom headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
}

#Setup the POST request including the login information
payload = {'UserName': login_password, 'Password': login_password, 'ValidateUser': '1', 'dbKeyAuth': 'JusticePA', 'SignOn': 'Sign+On'}

#Send the POST request
r = s.post('https://publicaccess.courts.oregon.gov/PublicAccessLogin/Login.aspx?ReturnUrl=%2fPublicAccessLogin%2fdefault.aspx', data=payload, headers=headers)

r.raise_for_status()

# %%
import random


#This section does one search for Jackson County, but all it's doing is getting us a __VIEWSTATE and __EVENTVALIDATION code that we can use to send the next request

#Define the URL for the search
county_url = 'https://publicaccess.courts.oregon.gov/PublicAccessLogin/Search.aspx?ID=200'

#Define the POST request for the search
county_data = {
	'NodeID': '101100',
	'NodeDesc': 'Jackson'
}

#Send the POST request
results = s.post(county_url, data=county_data, headers=headers, cookies=s.cookies)

# Wait for a random amount of time between 1 and 2 seconds
time.sleep(random.uniform(1, 2))

results.raise_for_status()

# %%
from bs4 import BeautifulSoup

# Parse the HTML content of results
soup = BeautifulSoup(results.text, 'html.parser')

# Find the input element with the name '__VIEWSTATE'
viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']

# Find the input elements with the names '__VIEWSTATEGENERATOR' and '__EVENTVALIDATION'
viewgen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
eventval = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

# %%
#Set the current date in the format MM/DD/YYYY
current_date = datetime.datetime.now().strftime("%m/%d/%Y")

#Set the POST request to search for all cases filed today in all counties.
search_data = {
	"__EVENTTARGET": "",
	"__EVENTARGUMENT": "",
	"__VIEWSTATE": viewstate,
	"__VIEWSTATEGENERATOR": viewgen,
	"__EVENTVALIDATION": eventval,
	"NodeID": "101100,102100,103100,104100,104210,104215,104220,104225,104310,104320,104330,104410,104420,104430,104440,105100,106100,106200,106210,107100,107200,107300,107400,107500,108100,109100,110100,110200,111100,112100,113100,114100,115100,115200,116100,117100,118100,119100,120100,121100,122100,122200,123100,124100,124200,125100,126100,127100,150000,150100,150200",
	"NodeDesc": "All+Locations",
	"SearchBy": "6",
	"ExactName": "on",
	"CaseSearchMode": "CaseNumber",
	"CaseSearchValue": "",
	"CitationSearchValue": "",
	"CourtCaseSearchValue": "",
	"PartySearchMode": "Name",
	"AttorneySearchMode": "Name",
	"LastName": "",
	"FirstName": "",
	"cboState": "AA",
	"MiddleName": "",
	"DateOfBirth": "",
	"DriverLicNum": "",
	"CaseStatusType": "0",
	"DateFiledOnAfter": current_date,
	"DateFiledOnBefore": current_date,
	"chkCriminal": "on",
	"chkFamily": "on",
	"chkCivil": "on",
	"chkProbate": "on",
	"chkDtRangeCriminal": "on",
	"chkDtRangeFamily": "on",
	"chkDtRangeCivil": "on",
	"chkDtRangeProbate": "on",
	"chkCriminalMagist": "on",
	"chkFamilyMagist": "on",
	"chkCivilMagist": "on",
	"chkProbateMagist": "on",
	"DateSettingOnAfter": "",
	"DateSettingOnBefore": "",
	"SortBy": "fileddate",
	"SearchSubmit": "Search",
	"SearchType": "CASE",
	"SearchMode": "FILED",
	"NameTypeKy": "",
	"BaseConnKy": "",
	"StatusType": "true",
	"ShowInactive": "",
	"AllStatusTypes": "true",
	"CaseCategories": "",
	"RequireFirstName": "",
	"CaseTypeIDs": "",
	"HearingTypeIDs": "",
    }

# Wait for a random amount of time between 1 and 2 seconds
time.sleep(random.uniform(1, 2))

#Send the POST request to search for all cases filed today in all counties.
results = s.post(county_url, data=search_data, headers=headers, cookies=s.cookies)

results.raise_for_status()

# %%

soup = BeautifulSoup(results.text, 'html.parser')

#Create and clear the master dictionary
master_cases = {}

#Find the table of court cases in the HTML and pull it out
main_table = soup.find(cellpadding="2")

#Look for the word "Tort" in the each case
for row in main_table.find_all('tr'):
    if any("Tort" in cell.get_text() for cell in row.find_all('td')):
        #If the word "Tort" is found, check if the case is in the counties we are interested in
        if any(county in row.find_all('td')[2].get_text() for county in ["Jackson", "Josephine", "Douglas", "Klamath", "Lake", "Coos", "Curry"]):  #If the case is in one of the counties we are interested in, pull out the case number, case name, county, and case type
            cells = row.find_all('td')
            case_number = cells[0].get_text(strip=True) if len(cells) > 0 else ''
            case_name = cells[1].get_text(strip=True) if len(cells) > 1 else ''
            case_county = cells[2].get_text(strip=True) if len(cells) > 2 else ''
            case_type = cells[3].get_text(strip=True) if len(cells) > 3 else ''
            #Clean up the case name and county
            case_name = case_name.replace('\n', ' ')
            case_county = case_county.replace(current_date, '')
            #Write the info to a temporary dictionary
            case_dict = {
                'Case Number': case_number,
                'Case Name': case_name,
                'County': case_county,
                'Case Type': case_type
            }
            #Append the temp dictionary to the master dictionary
            case_id = f"Case {len(master_cases) + 1}"
            master_cases[case_id] = case_dict

#Print if new cases were found
if master_cases:
    print("New cases found!")
else:
    print("No new cases found.")

#Write the results to a CSV file
with open(f"State_of_Oregon_Court_Cases_{current_date.replace('/', '-')}.csv", mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['Case Number', 'Case Name', 'County', 'Case Type'])
    writer.writeheader()
    for case in master_cases.values():
        writer.writerow(case)

# %%
#Write an email with the results
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

#Set the Slack token from the enviromental variables
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

if master_cases:
    formatted_cases = []
    #Format the cases for the Slack message
    for case_number, case_info in master_cases.items():
        formatted_case = (
            f"Case Number: {case_info['Case Number']}\n"
            f"Case Name: {case_info['Case Name']}\n"
            f"County: {case_info['County']}\n"
            f"Case Type: {case_info['Case Type']}\n"
            "-------------------------"
        )
        formatted_cases.append(formatted_case)
    
    client = WebClient(token=SLACK_TOKEN)
    #Post the message to the Slack channel
    client.chat_postMessage(
        channel="C07QGTYJJ9Z",
        text="New cases found in Oregon!\n" + "\n".join(formatted_cases)
    )


