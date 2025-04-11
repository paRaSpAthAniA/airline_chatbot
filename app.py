import streamlit as st
import requests
import re

API_TOKEN = '439349d701b6c09a3b1e3f42d28c8b36'

# Map of cities to their respective airport codes
city_to_code = {
    "delhi": "DEL", "mumbai": "BOM", "bangalore": "BLR", "hyderabad": "HYD",
    "chennai": "MAA", "kolkata": "CCU", "goa": "GOI", "ahmedabad": "AMD",
    "pune": "PNQ", "jaipur": "JAI"
}

# Airline code mapping
airline_codes = {
    "6E": "IndiGo",
    "AI": "Air India",
    "SG": "SpiceJet",
    "UK": "Vistara",
    "IX": "Air India Express",
    "QP": "Akasa Air",
    "G8": "Go First",
}

# Function to determine greeting based on user input
def get_greeting(user_message):
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "howdy", "greetings"]
    user_message = user_message.lower()

    for greeting in greetings:
        if user_message.startswith(greeting):
            return f"Hello! How can I assist you today?"
    return None

# Chatbot interface
st.title("✈️ Flight Price Checker")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Get user input
user_input = st.chat_input("Enter your travel details...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Check if the user input starts with a greeting
    greeting_response = get_greeting(user_input)
    if greeting_response:
        st.session_state.messages.append({"role": "assistant", "content": greeting_response})
        with st.chat_message("assistant"):
            st.write(greeting_response)
    
    # Extract cities from user input
    match = re.findall(r"\b([a-zA-Z]+)\b", user_input.lower())
    valid_cities = [word for word in match if word in city_to_code]

    if len(valid_cities) >= 2:
        from_city, to_city = valid_cities[0], valid_cities[1]

        # Check if the extracted cities are valid
        if from_city in city_to_code and to_city in city_to_code:
            from_code = city_to_code[from_city]
            to_code = city_to_code[to_city]

            url = f"https://api.travelpayouts.com/v2/prices/latest"
            headers = {"X-Access-Token": API_TOKEN}
            params = {"origin": from_code, "destination": to_code, "currency": "inr"}

            try:
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                if data.get("success") and data.get("data"):
                    flights = data["data"][:5]  # Get the first 5 flights
                    flight_lines = [f"🛫 Flights from {from_city.title()} to {to_city.title()}:"]
                    for flight in flights:
                        airline_code = flight.get("airline", "Unknown")
                        airline = airline_codes.get(airline_code, airline_code)
                        price = flight.get("value", "N/A")
                        flight_lines.append(f"• ₹{price} via {airline}")
                    flight_info = "\n\n".join(flight_lines)
                    st.session_state.messages.append({"role": "assistant", "content": flight_info})
                    with st.chat_message("assistant"):
                        st.markdown(flight_info)
                else:
                    no_flights_msg = "I'm sorry, but I couldn't find any flights for this route. Please ensure you've entered valid city names."
                    st.session_state.messages.append({"role": "assistant", "content": no_flights_msg})
                    with st.chat_message("assistant"):
                        st.write(no_flights_msg)
            except Exception as e:
                error_msg = f"An error occurred while fetching flight data: {e}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.write(error_msg)
        else:
            invalid_city_msg = "Please enter valid city names."
            st.session_state.messages.append({"role": "assistant", "content": invalid_city_msg})
            with st.chat_message("assistant"):
                st.write(invalid_city_msg)
    else:
        insufficient_info_msg = "Please enter at least two valid city names."
        st.session_state.messages.append({"role": "assistant", "content": insufficient_info_msg})
        with st.chat_message("assistant"):
            st.write(insufficient_info_msg)
