import time
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Streamlit Page Config
st.set_page_config(page_title="Web Scraper", page_icon="🛠", layout="wide")

# Main Navigation
st.sidebar.title("Navigation 🔍")
page = st.sidebar.radio("Go to", ["Home", "Bus Scraper 🚌", "Train Scraper 🚆"])

# ---- Setup Selenium Web Driver ----
def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-images")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0")
    options.page_load_strategy = 'eager'
    return webdriver.Chrome(service=service, options=options)

def extract_text(elements):
    return [elem.text.strip() for elem in elements if elem.text.strip()]

# ---- Expand Government Bus Dropdowns ----
def expand_government_buses(driver):
    try:
        wait = WebDriverWait(driver, 2)
    
        dropdown_buttons = wait.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            'a.btn.dark.filled.primary.sm.rounded-sm.inactive.button'
        )))

        if not dropdown_buttons:
            print("⚠ No government bus dropdown buttons found.")
        else:
            print(f"Found {len(dropdown_buttons)} government dropdown button(s).")

        for i, button in enumerate(dropdown_buttons):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", button)
                print(f" Clicked dropdown #{i + 1}")
            except Exception as click_error:
                print(f" Failed to click dropdown #{i + 1}: {click_error}")

    except Exception as e:
        print(" Error locating dropdown buttons:", e)


# ---- Bus Scraper ----
def scrape_buses(driver):
    all_buses = []
    try:
        wait = WebDriverWait(driver, 0.1)
        # wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "title")))
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.fare")))

        titles = extract_text(driver.find_elements(By.CLASS_NAME, "title"))
        subtitles = extract_text(driver.find_elements(By.CLASS_NAME, "sub-title"))
        departures = extract_text(driver.find_elements(By.CLASS_NAME, "departure-time"))
        arrivals = extract_text(driver.find_elements(By.CLASS_NAME, "arrival-time"))
        sources = extract_text(driver.find_elements(By.CLASS_NAME, "source-name"))
        durations = extract_text(driver.find_elements(By.CLASS_NAME, "travel-time"))
        destinations = extract_text(driver.find_elements(By.CLASS_NAME, "destination-name"))
        fares = extract_text(driver.find_elements(By.CSS_SELECTOR, "span.fare"))

        print(f"Titles: {len(titles)}")
        print(f"Subtitles: {len(subtitles)}")
        print(f"Departures: {len(departures)}")
        print(f"Arrivals: {len(arrivals)}")
        print(f"Sources: {len(sources)}")
        print(f"Durations: {len(durations)}")
        print(f"Destinations: {len(destinations)}")
        print(f"Fares: {len(fares)}")

        all_buses = list(zip(titles, subtitles, departures, arrivals, sources, durations, destinations, fares))

    except Exception as e:
        st.warning(f"Error fetching bus details: {e}")
    return all_buses

# ---- Train Scraper ----
def scrape_trains(driver):
    all_trains = []
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "name")))

        train_names = extract_text(driver.find_elements(By.CLASS_NAME, "name"))
        durations = extract_text(driver.find_elements(By.CLASS_NAME, "duration"))

        # Extract departure & arrival times correctly
        train_time_elements = driver.find_elements(By.CLASS_NAME, "trainTime")
        departures, arrivals, sources, destinations = [], [], [], []

        for element in train_time_elements:
            spans = element.find_elements(By.TAG_NAME, "span")
            if spans:
                # Modify departures and arrivals extraction to remove the last 4 characters
                raw_departure = spans[0].text.strip() if len(spans) > 0 else "N/A"
                raw_arrival = spans[-2].text.strip() if len(spans) > 1 else "N/A"

                departures.append(raw_departure[0:5:1] if len(raw_departure) > 0 else "N/A")
                arrivals.append(raw_arrival[0:5:1] if len(raw_arrival) > 1 else "N/A")

                # Modify source and destination extraction to remove first 6 characters
                raw_source = spans[0].text.strip() if len(spans) > 2 else "N/A"
                raw_destination = spans[-2].text.strip() if len(spans) > 3 else "N/A"

                sources.append(raw_source[6:] if len(raw_source) > 6 else "N/A")
                destinations.append(raw_destination[6:] if len(raw_destination) > 6 else "N/A")
            else:
                departures.append("N/A")
                arrivals.append("N/A")
                sources.append("N/A")
                destinations.append("N/A")

        # Extract multiple price details
        prices_list = []
        price_containers = driver.find_elements(By.CLASS_NAME, "react-horizontal-scrolling-menu--scroll-container")

        for container in price_containers:
            prices = extract_text(container.find_elements(By.CLASS_NAME, "avail-cls"))

            # ✅ Ensure full price extraction
            full_prices = [price.strip() for price in prices if price.strip()]
            prices_list.append("; ".join(full_prices) if full_prices else "N/A")  # Use '; ' instead of ', ' to avoid CSV conflicts


        frequencies_list = []
        frequency_containers = driver.find_elements(By.CLASS_NAME, "days-of-run")
        
        for container in frequency_containers:
            running_days = extract_text(container.find_elements(By.CLASS_NAME, "running"))
            
            # New logic-check for exactly two "T"s and two "S"s
            if running_days.count("T") == 2 and running_days.count("S") == 2:
                frequencies_list.append("Runs Daily")
            else:
                frequencies_list.append(", ".join(running_days) if running_days else "N/A")

        # Adjust list sizes in case of mismatches
        max_length = max(len(train_names), len(departures), len(arrivals), len(sources), 
                          len(durations), len(destinations), len(prices_list), len(frequencies_list))
        
        train_names += ["N/A"] * (max_length - len(train_names))
        departures += ["N/A"] * (max_length - len(departures))
        arrivals += ["N/A"] * (max_length - len(arrivals))
        sources += ["N/A"] * (max_length - len(sources))
        durations += ["N/A"] * (max_length - len(durations))
        destinations += ["N/A"] * (max_length - len(destinations))
        prices_list += ["N/A"] * (max_length - len(prices_list))
        frequencies_list += ["N/A"] * (max_length - len(frequencies_list))

        # Combine all extracted data
        all_trains = list(zip(train_names, departures, arrivals, sources, durations, destinations, prices_list, frequencies_list))

    except Exception as e:
        st.warning(f"Error fetching train details: {e}")
    
    return all_trains


# ---- Download CSV ----
def download_csv(dataframe, filename):
    # ✅ Convert all columns to string type to prevent truncation issues
    dataframe = dataframe.astype(str)

    # ✅ Ensure proper encoding
    csv_data = dataframe.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(label="📥 Download CSV", data=csv_data, file_name=filename, mime="text/csv")

# ---- Page Routing ----
if page == "Home":
    st.title("🚀 Web Scraper: Bus & Train Data Extraction")
    st.write("""
    This tool allows you to scrape bus and train details from *AbhiBus* and *Train Websites*.
    
    *Steps to Use:*
    1. Select *Bus Scraper 🚌* or *Train Scraper 🚆* from the left menu.
    2. Enter the URL where you want to scrape data from.
    3. Click *Scrape* to extract the details.
    4. Download the extracted data as a *CSV* file.
    """)

elif page == "Bus Scraper 🚌":
    st.title("🚌 Bus Scraper")
    url = st.text_input("Enter AbhiBus Bus Search URL:")

    if st.button("Scrape Buses"):
        if url:
            try:
                start = time.time()
                driver = setup_driver()
                driver.get(url)
                expand_government_buses(driver)
                all_bus_data = scrape_buses(driver)
                driver.quit()
                end = time.time()
                st.success(f"Scraping completed in {round(end - start, 2)} seconds ⏱️")

                if all_bus_data:
                    df = pd.DataFrame(all_bus_data, columns=["Bus Name", "Bus Type", "Departure", "Arrival", "Starting Place", "Duration", "Ending Place", "Price"])

                    df["Departure"] = (df["Departure"].tolist())  
                    df["Arrival"] = (df["Arrival"].tolist())
                    df["Starting Place"] = (df["Starting Place"].tolist())  
                    df["Duration"] = (df["Duration"].tolist())   
                    df["Ending Place"] = (df["Ending Place"].tolist())   
                    df["Price"] = (df["Price"].tolist())        

                   

                    # ✅ Separate Government & Private buses based on "Service Number"
                    df_gov = df[df["Bus Name"].str.contains("Service Number", case=False, na=False)]
                    df_private = df[~df["Bus Name"].str.contains("Service Number", case=False, na=False)]


                    # 🏛 Government Buses Table
                    if not df_gov.empty:
                        st.write("### Government Buses 🏛 (APSRTC & TSRTC) ")
                        st.dataframe(df_gov)
                        download_csv(df_gov, "government_buses_sorted.csv")

                    # 🚍 Private Buses Table
                    if not df_private.empty:
                        st.write("### Private Buses 🚍 ")
                        st.dataframe(df_private)
                        download_csv(df_private, "private_buses_sorted.csv")

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("⚠ Please enter a valid Bus URL.")

elif page == "Train Scraper 🚆":
    st.title("🚆 Train Scraper")
    url = st.text_input("Enter AbhiBus Train Search URL:")

    if st.button("Scrape Trains"):
        if url:
            try:
                driver = setup_driver()
                driver.get(url)
                all_train_data = scrape_trains(driver)
                driver.quit()

                if all_train_data:
                    df = pd.DataFrame(all_train_data, columns=["Train Name", "Departure", "Arrival", "Starting Station", "Duration", "Destination Station", "Prices", "Frequency"])
                    df["Prices"] = df["Prices"].apply(lambda x: x if isinstance(x, str) else str(x))
                    st.dataframe(df)
                    download_csv(df, "train_details.csv")
                else:
                    st.warning("No data found. Please check the URL.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("⚠ Please enter a valid Train URL.")