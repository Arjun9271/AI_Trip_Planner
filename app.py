import streamlit as st
import requests
import os
from dotenv import load_dotenv
from groq import Groq
import re
import base64
from fpdf import FPDF
import io

# Set page config
st.set_page_config(page_title="AI Trip Planner 🌴", layout="wide")

# Load environment variables
load_dotenv()

# Initialize Groq client with API key from .env
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

def get_llama_response(prompt):
    response = groq_client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are an AI travel planner. Always respond in the exact format specified by the user."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=4000
    )
    return response.choices[0].message.content

def get_place_photo(place_name, api_key):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": place_name,
        "inputtype": "textquery",
        "fields": "photos",
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json().get('candidates')
        if result and 'photos' in result[0]:
            photo_reference = result[0]['photos'][0]['photo_reference']
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1200&photoreference={photo_reference}&key={api_key}"
            return photo_url
    return None

def format_itinerary(raw_itinerary):
    lines = raw_itinerary.split('\n')
    formatted_lines = []

    for line in lines:
        if line.startswith('# '):
            formatted_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith('## '):
            formatted_lines.append(f"<h2>{line[3:]}</h2>")
        elif re.match(r'^\d{1,2}:\d{2}:', line):
            time, activity = line.split(':', 1)
            formatted_lines.append(f"<strong>{time}:</strong>{activity}")
        elif line.startswith('Evening:'):
            formatted_lines.append(f"<strong>{line}</strong>")
        elif line.strip().startswith('- '):
            formatted_lines.append(f"<li>{line.strip()[2:]}</li>")
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)

def get_weather_forecast(city, days):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecast = []
        for i in range(0, min(days * 8, len(data['list'])), 8):  # One forecast per day
            day_data = data['list'][i]
            forecast.append({
                'date': day_data['dt_txt'].split()[0],
                'temp': day_data['main']['temp'],
                'description': day_data['weather'][0]['description']
            })
        return forecast
    return None

def create_pdf(itinerary, destination):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Itinerary for {destination}", ln=1, align='C')
    pdf.multi_cell(0, 10, txt=itinerary)
    return pdf.output(dest='S').encode('latin-1')

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .stButton>button {
        width: 150px;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stSelectbox>div>div {
        background-color: white;
        border-radius: 20px;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
    }
    .stNumberInput>div>div>input {
        border-radius: 20px;
    }
    .itinerary-box {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .itinerary-box h1 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    .itinerary-box h2 {
        color: #16a085;
        margin-top: 20px;
    }
    .itinerary-box strong {
        color: #e74c3c;
    }
    .itinerary-box ul {
        list-style-type: none;
        padding-left: 0;
    }
    .itinerary-box li {
        margin-bottom: 5px;
    }
    .share-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        border-radius: 5px;
        color: white;
        text-decoration: none;
        font-weight: bold;
    }
    .whatsapp { background-color: #25D366; }
    .facebook { background-color: #3b5998; }
    .twitter { background-color: #1DA1F2; }
    .email { background-color: #D44638; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("About This Project")
st.sidebar.info(
    """
    **AI Trip Planner** is an innovative application that generates personalized trip itineraries based on your preferences.
    
    - **Travel days**: Select the number of days for your trip.
    - **Destination**: Enter the name of your destination city.
    - **Travel style**: Choose your preferred style of travel.
    
    Once you provide the necessary information, click 'Plan My Trip' to receive a detailed itinerary for your dream vacation!
    """
)

# Header
st.title("🌴 AI Trip Planner")
st.markdown("### Create your personalized dream itinerary in seconds!")

# Input fields
col1, col2, col3 = st.columns(3)

with col1:
    travel_days = st.number_input("Travel days", min_value=1, max_value=30, value=3)

with col2:
    destination = st.text_input("Destination", placeholder="Enter a city name...")

with col3:
    travel_style = st.selectbox("Travel style", 
                                ["Cultural and Historical", "Adventure", "Relaxation", 
                                 "Foodie", "Budget", "Luxury"])

# Generate button
if st.button("Plan My Trip"):
    if destination and travel_style:
        with st.spinner("Crafting your perfect itinerary..."):
            prompt = f"""Create a detailed {travel_days}-day itinerary for a {travel_style} trip to {destination}.
            
            Strictly adhere to the following format for each day:
            
            # {travel_days} Day {travel_style} Trip in {destination}
            
            ## Day [Number] - [Day Theme]
            
            [Time]: [Activity 1]
            [Description of Activity 1]
            [Booking information if applicable]
            
            [Time]: [Activity 2]
            [Description of Activity 2]
            [Booking information if applicable]
            
            ... (continue for 4-6 activities)
            
            Evening: [Evening activity or summary]
            
            Repeat this structure for each day of the trip.
            
            After the itinerary, include these sections:
            
            ## Local Tips
            - [Tip 1]
            - [Tip 2]
            - [Tip 3]
            
            ## Packing Suggestions
            - [Item 1]
            - [Item 2]
            - [Item 3]
            ... (continue for 10-15 items)
            
            Use Markdown formatting for headers and emphasis. Ensure all days follow the same structure and format.
            Do not deviate from this format or add any additional text or sections.
            """
            
            itinerary = get_llama_response(prompt)
            formatted_itinerary = format_itinerary(itinerary)
            
            # Display results
            st.success("Your itinerary is ready!")
            
            # Get and display place photo
            photo_url = get_place_photo(destination, GOOGLE_API_KEY)
            if photo_url:
                st.image(photo_url, caption=f"Welcome to {destination}!", use_column_width=True)
            else:
                st.image("https://via.placeholder.com/1200x400?text=Imagine+Your+Dream+Destination", 
                         caption=f"Imagine your trip to {destination}!", use_column_width=True)
            
            # Display itinerary in a boxed interface
            with st.container():
                st.markdown('<div class="itinerary-box">', unsafe_allow_html=True)
                st.markdown(formatted_itinerary, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            

            
            # Download button
            pdf = create_pdf(itinerary, destination)
            st.download_button(
                label="📥 Download Itinerary (PDF)",
                data=pdf,
                file_name=f"{destination}_itinerary.pdf",
                mime="application/pdf"
            )
            


# Footer
st.markdown("---")
st.markdown("Made with ❤️ by AI Trip Planner | © 2024")