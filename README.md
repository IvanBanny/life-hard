# Life-Hard: Travel Budget Automation

A smart travel planning application that integrates with Bunq's banking API to help you plan trips within your budget. The app monitors your savings account balance and automatically generates travel itineraries using AI when your savings reach the minimum threshold.

## Features

- **Automated Budget Monitoring**: Tracks your Bunq savings pot balance in real-time
- **AI-Powered Itinerary Generation**: Uses local LLM (Gemma3) to create personalized travel plans
- **Web Interface**: Simple form to input travel preferences
- **Smart Savings Top-up**: Automatically transfers funds to maintain minimum travel budget

## Architecture

- Flask web application with session management
- Bunq SDK integration for banking operations
- Local LLM integration (Ollama with Gemma3 model)
- Real-time polling system for balance monitoring

## Prerequisites

- Python 3.x
- Bunq Sandbox account
- Ollama with Gemma3 model installed locally
- Environment variables configured

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Bunq API key:
   ```
   BUNQ_API_KEY=your_sandbox_api_key
   DEVICE_DESCRIPTION=your_device_name
   CONTEXT_FILE=bunq_context.conf
   ```
4. Initialize Bunq context:
   ```bash
   python init_context.py
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Navigate to the web form at `http://localhost:5000/form`
2. Enter your travel destination and dates
3. The app monitors your savings and generates an itinerary when funds are sufficient
4. View your personalized travel plan on the results page

## Project Structure

- `src/`: Main application code
  - `bunq_utils.py`: Bunq API integration
  - `llm_utils.py`: LLM integration
  - `chat.py`: Itinerary generation endpoint
  - `form.py`: Travel form handling
- `static/`: Frontend assets
- `app.py`: Main application loop with balance monitoring

## Team

Bora Saygaç, 
Daisy Ossel, 
Debdutta Guha Roy, 
Ivan Banny, 
Rushikesh Somane

Developed for the Bunq Hackathon 2025
