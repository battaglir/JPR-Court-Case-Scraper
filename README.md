**Overview**

This program is designed to scrape court case information from the Oregon state courts website. It extracts all the civil cases from every county in Oregon on the current day. The program is particularly focused on identifying tort cases and filtering them based on specific counties of interest. Since this is a program built for Jefferson Public Radio, we're looking for counties in southwest Oregon. If any cases are found, the program compiles them into a nice looking list, and posts it in a specific slack channel.

**Usage**

1. Setup: Ensure you have the necessary dependencies installed, including requests, bs4, and slack_sdk. Everything else should be built-in to python
2. Run the Script: Execute the court_scraper.py script to start the scraping process.
3. View Results: The extracted and formatted case information will be sent to the specified Slack channel.

**Dependencies**

- requests (basic web scraping script)
- bs4 (BeautifulSoup4)
- slack_sdk (to access the slack API)

**Configuration**

To configure the program for your needs, you may need to update the following:

- Slack Token: Ensure you have a valid Slack token and update the SLACK_TOKEN variable in the script. In this repository, SLACK_TOKEN is pulled from a secret variable stored in github for privacy
- Courts login: You'll need your own login for the Oregon Courts website. Update LOGIN_PASSWORD to reflect this.
- Counties of Interest: Modify the list of counties in the extraction portion of the script to match your requirements.
- Slack channel: The channel in this program is specific to a Slack channel I am using, you'll have to change the channel to match.
