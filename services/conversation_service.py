from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from datetime import datetime
from config import chat

class ConversationService:
    def __init__(self, chat_model=chat):
        """
        Initialize the ConversationService with a chat model.
        """
        self.chat = chat_model
        self.chat_history = []

    def clear_data(self):
        """
        Clear the chat history.
        """
        self.chat_history = {}

    def get_current_date(self):
        """
        Get the current date.
        """
        return datetime.now().strftime("%Y-%m-%d (%A)")

    def generate_weather_response(self, customer_request, extracted_location, weather_forecast, history):
        """
        Generate a weather response based on the user's request, location, weather forecast, and chat history.
        """
        try:
            # Define the schema for extracting information from the user query
            response_schema = ResponseSchema(
                name="response",
                description="The detailed response to the user's weather query based on the extracted location and obtained weather forecast."
            )

            response_schemas = [response_schema]

            # Initialize the output parser with the response schemas
            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

            # Get the format instructions for the parser
            format_instructions = output_parser.get_format_instructions()

            # Get the current date
            current_date = self.get_current_date()

            # Define the template for the chat prompt
            request_template = """
            You are a weather chatbot assistant. Your primary goal is to provide accurate and helpful weather information while maintaining a friendly and professional tone.

            This is the conversation history: {history}
            Today's date is: {current_date}
            And the new user message is: {customer_request}

            Detected locations from the exchange: {extracted_location}. For them, the weather forecast is as follows:
            Available weather forecasts: {weather_forecast}

            Your task is to follow these guidelines to craft a response to the user's new message:

            1. Understand the User's Needs:
            - Carefully review the conversation history to understand the context and previous queries.
            - Analyze the new customer query to determine the primary weather information sought (current conditions, forecast, specific parameters like temperature or precipitation).
            - Identify the timeframe (current, today, tomorrow, upcoming week, etc.) for which the forecast is requested.
            - Use the extracted location for the response. If the location is unclear, politely ask the user to specify it.

            2. Gather the Information Needed to Craft the Answer:
            - Reference the weather forecast to provide accurate information focused on the user's requested timeframe and weather parameters.
            - Search the forecast for the relevant city first, and then for the relevant date. You will find specific dates as well as relative dates (e.g., forecast for tomorrow).
            - If the user is traveling, and asks you for the weather, you should provide the forecast for the city where the user is traveling to. 
            - If the user asks for a forecast beyond the next five days, politely explain that you don't have the data.
            - Since you don't have forecasts by the hour, if the user requests information for a specific time of day, provide a general forecast and apologize for the lack of detail.
            - The information in the forecast data for the detected location includes: temperatures (min, max, average, and feels like), chance of precipitation, humidity, wind speed, visibility, and weather descriptions, among others.

            3. Write a Clear and Concise Response:
            - When the user asks a specific question, you answer the question directly.
            - Your answer should be short and to the point. Avoid long, complex sentences.
            - Ensure the response is concise and easy to understand. Avoid including unnecessary information that does not add value to the user's query.
            - Use units of measurement (e.g., degrees Celsius, millimeters of rain).
            - If certain information is not available, acknowledge it politely.
            - Request clarification on vague queries about specific weather aspects.
            - Reference specific dates when discussing relative times like today and tomorrow to avoid ambiguity.

            4. Maintain Conversation Flow:
            - For follow-up questions, refer to previously mentioned locations unless a new one is specified.
            - Offer practical advice based on the forecast, such as suggestions for weather-related activities or clothing choices.

            5. Handle Off-Topic Queries:
            - Politely redirect the conversation to weather-related topics if the user asks about unrelated subjects.
            - Suggest rephrasing their question to relate to weather conditions, if possible.

            Now, please provide a response to the user's request, following the guidelines above and structure the reply as follows:
            {format_instructions}
            """
            # Format the prompt with the user input and format instructions
            prompt = ChatPromptTemplate.from_template(template=request_template)
            messages = prompt.format_messages(
                customer_request=customer_request,
                extracted_location=extracted_location,
                weather_forecast=weather_forecast,
                current_date=current_date,
                history=history,
                format_instructions=format_instructions
            )

            # Get the response from the model 
            response = self.chat.invoke(messages)
            
            # Parse the response from the model
            output_dict = output_parser.parse(response.content)
            
            return output_dict['response']
        
        except Exception as e:
            return {"error": str(e)}