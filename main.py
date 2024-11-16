from services.ui_service import ChatInterface


def main():
    """
    Initialize and run the chatbot interface.
    """
    chatbot = ChatInterface()   # Create an instance of ChatInterface
    chatbot.main()              # Run the main method of ChatInterface


if __name__ == "__main__":
    main()  