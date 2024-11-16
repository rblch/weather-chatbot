from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from config import chat

class LocationService:
    def __init__(self, chat_model=chat):
        """
        Initializes the LocationService with the given chat model.
        """
        self.chat = chat_model
        self.detected_locations = set()

    def clear_data(self):
        """
        Clears the detected locations.
        """
        self.detected_locations.clear()

    def detect_location(self, customer_request):
        """
        Extracts and identifies unique cities mentioned in the customer request.

        Args:
            customer_request (str): The customer request containing city names or descriptions.

        Returns:
            dict: A dictionary containing a list of unique cities.
                  If no cities are identified, returns an empty list.
        """
        try:
            # Define the schema for extracting information from the user query
            cities_schema = ResponseSchema(
                name="cities",
                description="List of unique cities for which the forecast is being requested. Use obvious inferences for city names. If no city can be identified, return an empty list."
            )

            response_schemas = [cities_schema]

            # Initialize the output parser with the response schemas
            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

            # Get the format instructions for the parser
            format_instructions = output_parser.get_format_instructions()

            # Template for the prompt to be sent to the model
            request_template = """\
            Extract a list of unique cities from the following text. 
            Use obvious inferences for city names and handle common misspellings. 
            If no city can be identified, return an empty list.

            Text: {text}

            {format_instructions}
            """
            
            # Format the prompt with the user input and format instructions
            prompt = ChatPromptTemplate.from_template(template=request_template)
            messages = prompt.format_messages(text=customer_request, format_instructions=format_instructions)

            # Get the response from the model
            response = self.chat.invoke(messages)
            
            # Parse the response from the model
            output_dict = output_parser.parse(response.content)
            
            # Deduplicate and filter the list of cities
            unique_cities = list(set(output_dict['cities']))
            unique_cities = [city for city in unique_cities if len(city) > 1]  # Filter out single characters
            return {"cities": unique_cities}
        
        except Exception as e:
            print(f"Error in detect_location: {e}")
            return {"cities": []}