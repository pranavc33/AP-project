import streamlit as st
import requests
import pandas as pd
import os

# Set up the API endpoint and headers
url = "https://api.api-ninjas.com/v1/nutrition?query="
headers = {
    "X-API-Key": "cSNXvt31N7FSRia1HJfJlg==j3XuZh8S3Cw6Aqwg"
}

# Create a background image
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://img.freepik.com/premium-photo/healthy-food-variation-with-copy-space-empty-background_944892-519.jpg');
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create a title and header
st.title("Nutrition Information")

# Check if the search history CSV file exists, and create it if not
search_history_file = "search_history.csv"
if not os.path.exists(search_history_file):
    pd.DataFrame(columns=["Food", "Calories"]).to_csv(search_history_file, index=False)

# Create the input field and submit button
food_item = st.text_input("Enter a food item")
if st.button("Submit"):
    # Make the API request
    params = {"query": food_item}
    response = requests.get(url, headers=headers, params=params)

    # Parse the response and display the calorie information
    if response.status_code == 200:
        result = response.json()
        if len(result) > 0:
            # Assuming you want to display the first result's calories
            calories = result[0]["calories"]
            st.success(f"{food_item} has {calories} calories")

            # Update the search history by appending to the CSV file
            search_history = pd.read_csv(search_history_file)
            search_history = search_history.append({"Food": food_item, "Calories": calories}, ignore_index=True)
            search_history.to_csv(search_history_file, index=False)

        else:
            st.warning("No results found for this food item")
    else:
        st.error("Error: Unable to get calorie information")

# Create a section for history
st.header("Search History")

# Load and display the search history from the CSV file when the "Show History" button is pressed
if st.button("Show History"):
    search_history = pd.read_csv(search_history_file)
    st.table(search_history)

# Add a "Clear History" button to clear the search history
if st.button("Clear History"):
    # Clear the history by overwriting the CSV file with an empty DataFrame
    pd.DataFrame(columns=["Food", "Calories"]).to_csv(search_history_file, index=False)
    st.success("Search history cleared!")
