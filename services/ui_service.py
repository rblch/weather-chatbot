import streamlit as st
from .weather_service import WeatherService
from .location_service import LocationService
from .conversation_service import ConversationService

class ChatInterface:
    """
    A class to represent the chat interface for a weather forecast chatbot.
    """

    def __init__(self):
        """
        Initializes the ChatInterface by setting up the services and session state variables.
        """
        self.initialize_services()
        self.initialize_session_state()

    def initialize_services(self):
        """
        Initializes the required services (WeatherService, LocationService, ConversationService)
        and stores them in the session state.
        """
        if 'weather_service' not in st.session_state:
            st.session_state.weather_service = WeatherService()
        if 'location_service' not in st.session_state:
            st.session_state.location_service = LocationService()
        if 'conversation_service' not in st.session_state:
            st.session_state.conversation_service = ConversationService()

        self.weather_service = st.session_state.weather_service
        self.location_service = st.session_state.location_service
        self.conversation_service = st.session_state.conversation_service

    def initialize_session_state(self):
        """
        Initializes the session state variables needed for the chat functionality.
        """
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'pending_user_input' not in st.session_state:
            st.session_state.pending_user_input = None
        if 'locations' not in st.session_state:
            st.session_state.locations = set()
        if 'weather_forecasts' not in st.session_state:
            st.session_state.weather_forecasts = {}

    def reset_chat(self):
        """
        Resets the chat and related session state variables when the "Reset Chat" button is pressed.
        """
        if st.sidebar.button("Reset Chat"):
            st.session_state.chat_history = []
            st.session_state.pending_user_input = None
            st.session_state.locations = set()
            st.session_state.weather_forecasts = {}
            st.session_state.weather_cache = {}
            st.session_state.weather_service.clear_data()
            st.session_state.location_service.clear_data()
            st.session_state.conversation_service.clear_data()
            st.rerun()

    def display_chat_history(self):
        """
        Displays the chat history in the chat interface.
        """
        with st.container():
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["text"])

    def focus_chat_input(self):
        """
        Sets focus on the chat input box to avoid needing to manually selecting each time.
        """
        focus_script = """
        <script>
        document.getElementById("chat-input").focus();
        </script>
        """
        st.markdown(focus_script, unsafe_allow_html=True)

    def handle_user_input(self):
        """
        Handles user input, updates the chat history, and sets the pending user input.
        """
        prompt = st.chat_input("Type a message", key="chat-input")
        if prompt:
            st.session_state.pending_user_input = prompt
            st.session_state.chat_history.append({"role": "user", "text": prompt})
            st.rerun()

    def process_input_and_generate_response(self):
        """
        Processes user input, detects locations, retrieves weather forecasts, and generates a bot response.
        """
        if st.session_state.pending_user_input:
            prompt = st.session_state.pending_user_input

            # Extract conversation history as string for context
            history = "\n".join([f"{msg['role']}: {msg['text']}" for msg in st.session_state.chat_history])

            # Detect location from user query
            location_result = self.location_service.detect_location(prompt)
            cities = location_result.get("cities", []) if location_result else []

            # Update weather forecasts if new cities are found
            if cities:
                self.weather_service.get_weather_forecasts(cities)

            # Retrieve accumulated data
            locations, weather_forecasts = self.weather_service.get_accumulated_data()

            # Generate response based on detected cities
            bot_response = self.conversation_service.generate_weather_response(
                prompt, locations, weather_forecasts, history
            )

            # Add bot response to chat history
            st.session_state.chat_history.append({"role": "assistant", "text": bot_response})
            st.session_state.pending_user_input = None
            st.rerun()

    def main(self):
        """
        The main function to run the chat interface, setting up the sidebar, and handling the chat interaction.
        """
        st.sidebar.title('The Weather Channel Chatbot')
        st.sidebar.header('About')
        st.sidebar.info("""
        Welcome to the TWC Chatbot! This chatbot provides daily weather forecasts for cities worldwide, including predictions for the next five days. Ask about the city you're interested in, and receive up-to-date weather information.
        """)
        self.reset_chat()
        self.display_chat_history()
        self.handle_user_input()
        self.process_input_and_generate_response()
        self.focus_chat_input()
