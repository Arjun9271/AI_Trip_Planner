# AI Trip Planner 🌴

**AI Trip Planner** is an innovative Streamlit application that generates personalized trip itineraries based on user preferences. This app uses the Groq AI model for crafting detailed travel plans and integrates the Google Places API and OpenWeatherMap API for enhanced functionality.

## Features

- **Travel Days**: Specify the number of days for your trip.
- **Destination**: Enter the name of your destination city.
- **Travel Style**: Choose your preferred style of travel.
- **Personalized Itinerary**: Get a detailed itinerary tailored to your preferences.
- **Destination Images**: View photos of your destination.


## Use of Google Places API

We use the Google Places API to fetch images of your destination. This enhances the user experience by providing visual context for the trip. When you input a destination, the app makes a request to the Google Places API to retrieve a photo reference. This reference is then used to generate a URL for displaying a relevant image of the destination.

## How It Works

1. **Setup**: Ensure you have the required API keys in your `.env` file:
   - `GROQ_API_KEY`: For Groq AI model.
   - `GOOGLE_API_KEY`: For Google Places API.
 

2. **Generate Itinerary**:
   - Input travel details and click "Plan My Trip".
   - The app generates a detailed itinerary using the Groq AI model.

3. **View and Download**:
   - A photo of the destination is fetched using the Google Places API.
   - The itinerary is displayed and can be downloaded as a PDF.
