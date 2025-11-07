from dotenv import load_dotenv
load_dotenv()

from chatbot.llm_client import generate_summary

print(generate_summary("Summarize why Django REST framework is useful."))
