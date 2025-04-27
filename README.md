**Project Overview – Jatayu Web Scraper Tool (JWSBT)**

The Jatayu Web Scraper Tool (JWSBT) is a Streamlit-based Python application that provides an intuitive interface to extract real-time travel data—both buses and trains—from AbhiBus. It scrapes relevant information like names, timings, prices, and frequency, and presents it in a structured format with CSV export functionality.
 **Key Features
🚌 Bus Scraper**
Scrapes both Private and Government buses.

Automatically expands hidden Government Bus sections.

**Extracts:**

Bus name and type

Departure and arrival times

Travel duration

Price

Allows users to download the scraped data as CSV.

🚆 Train Scraper
Extracts multiple pieces of information from AbhiBus train search results.

Specifically retrieves:

  Train name

  Departure and arrival times

  Source and destination stations

  Total travel duration

  Available ticket classes with prices (e.g., SL, 2A, 3A)

  Frequency of operation (Runs Daily / Days of week)

Allows the data to be exported as CSV for further analysis or record-keeping.

🛠️ **Technology Stack**
**Python:** Core programming language.

**Streamlit:** Used to build the front-end of the application.

**Selenium:** Used for dynamic web scraping.

**Pandas:** For tabular data manipulation and CSV export.

**ChromeDriver:** Acts as a bridge between Selenium and Chrome browser.

🖥️ **Application Structure**
The application is contained in a single file: scrap.py. It includes:

Streamlit UI logic

Scraping functions for buses and trains

CSV export logic

The core scraping logic for trains is structured to:

Handle dynamic content loading using WebDriverWait.

Parse nested HTML elements like <span> for times and stations.

Correctly extract fare classes from horizontally scrolling price sections.

Normalize and validate data to ensure consistency across all records.


 **How to Use the Tool**
**For Buses**
Visit AbhiBus and search a route (e.g., Hyderabad to Vijayawada).

Copy the complete search URL from the browser.

Paste it into the Bus URL input field in the app.

Click on Scrape Buses.

View the extracted details and download the CSV.

**For Trains**
Search a train route on AbhiBus (e.g., Hyderabad to Vijayawada).

Paste the train search URL into the Train URL input.

Click on Scrape Trains.

View the extracted data which includes train name, timings, source/destination, prices, and frequency.

Download the CSV if needed.

**Performance Tips**
To ensure faster scraping (ideally under 30 seconds):

Use high-speed internet.

Keep browser cache cleared and avoid extra tabs during scraping.

Optimize headless Chrome settings and reduce WebDriverWait timeouts where possible.

Streamlit’s auto-reloading feature can cause delays — minimize reruns and use @st.cache_data() when applicable.


