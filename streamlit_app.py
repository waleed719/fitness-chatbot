import streamlit as st
import httpx
import os
import re
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file (especially for local development)
load_dotenv()

# --- Configuration and Constants ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# You can switch to gemini-1.5-pro-latest for potentially more detailed responses,
# but it may have different pricing and availability.
# API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


# Predefined FAQ responses for the fitness domain
FITNESS_FAQS = {
    "what is your name": "I am a Fitness Chatbot, designed to help you with your fitness queries!",
    "how to lose weight": "Losing weight typically involves a combination of a balanced diet and regular exercise. Consider consulting a nutritionist or a fitness expert for a personalized plan.",
    "best exercises for beginners": "For beginners, bodyweight exercises like squats, push-ups (modified if needed), planks, and lunges are great. Walking or light jogging are also excellent starting points.",
    "how much water should I drink daily": "Generally, it's recommended to drink around 8 glasses (about 2 liters) of water daily, but this can vary based on activity level, climate, and individual needs.",
    "what is protein good for": "Protein is essential for muscle repair and growth, hormone production, and overall body function. It's crucial for anyone engaging in physical activity.",
    "how to build muscle": "Building muscle requires progressive overload in strength training, adequate protein intake, and sufficient rest. Consistency is key!",
    # ... (keep all other FAQs as they were)
    "what is cardio": "Cardio (cardiovascular exercise) strengthens your heart and lungs. Examples include running, swimming, cycling, and brisk walking.",
    "how often should I work out": "For general health, aim for at least 150 minutes of moderate-intensity aerobic activity or 75 minutes of vigorous-intensity aerobic activity per week, plus strength training 2-3 times a week.",
    "what is a balanced diet": "A balanced diet includes a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats. It provides all the necessary nutrients for your body.",
    "can you help me with a workout plan": "While I can offer general advice, I'm not a certified personal trainer. For a personalized workout plan, I recommend consulting a professional fitness coach.",
    "what are macronutrients": "Macronutrients are nutrients that the body needs in large amounts: carbohydrates, proteins, and fats. They provide energy and are essential for bodily functions.",
    "what are micronutrients": "Micronutrients are vitamins and minerals that the body needs in smaller amounts. They are crucial for various bodily functions and overall health.",
    "how to stay motivated": "Set realistic goals, track your progress, find an exercise buddy, try different activities to keep things interesting, and celebrate small victories!",
    "is stretching important": "Yes, stretching improves flexibility, reduces muscle soreness, and can help prevent injuries. Incorporate dynamic stretches before workouts and static stretches after.",
    "what is HIIT": "HIIT stands for High-Intensity Interval Training. It involves short bursts of intense exercise followed by brief recovery periods. It's effective for burning calories and improving cardiovascular fitness.",
    "what are electrolytes": "Electrolytes are minerals like sodium, potassium, and calcium that help regulate fluid balance, muscle contractions, and nerve signals. They are important during intense exercise.",
    "how to recover after workout": "Post-workout recovery includes proper nutrition (protein and carbs), hydration, stretching, and adequate sleep. Foam rolling can also help with muscle soreness.",
    "what is a calorie deficit": "A calorie deficit occurs when you consume fewer calories than your body burns. It's a fundamental principle for weight loss.",
    "what is meal prepping": "Meal prepping involves preparing meals or components of meals in advance. It helps with portion control, healthy eating, and saving time.",
    "how to track progress": "Track your progress by monitoring your weight, measurements, strength gains, endurance improvements, and how your clothes fit. Take progress photos too!",
}

# UPDATED SYSTEM_INSTRUCTION
SYSTEM_INSTRUCTION = (
    "You are an expert fitness chatbot. Your goal is to provide comprehensive, detailed, and well-structured information "
    "related to fitness, exercise, nutrition, and general well-being. "
    "You can use markdown formatting such as lists (using hyphens or asterisks for bullet points), "
    "bolding (using double asterisks **like this**), and paragraphs to make your answers clear and easy to read. "
    "If a user asks a question that is not related to fitness, politely inform them that your expertise is in fitness "
    "and you cannot answer non-fitness related questions. "
    "Strive to be thorough in your explanations. Ensure your advice is safe and generally applicable. "
    "For specific medical or dietary conditions, always advise the user to consult a professional."
)

# --- Helper Functions ---

# UPDATED strip_markdown function (effectively disabled to allow markdown)
def strip_markdown(text):
    """
    Passes text through, allowing markdown.
    Original function preserved in comments if selective stripping is needed later.
    """
    return text
    # Original stripping logic:
    # text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    # text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    # text = re.sub(r'\_([^\_]+)\_', r'\1', text)
    # text = re.sub(r'#+\s*', '', text)
    # text = re.sub(r'^- ', '', text, flags=re.MULTILINE)
    # text = text.replace('`', '')
    # return text.strip()

async def get_chatbot_response(user_message: str, conversation_api_history: list) -> str:
    """
    Gets a response from the chatbot, either from FAQs or Gemini API.
    """
    normalized_message = user_message.lower().strip()

    # 1. Check FAQs
    if normalized_message in FITNESS_FAQS:
        return FITNESS_FAQS[normalized_message]

    # 2. Call Gemini API
    if not GEMINI_API_KEY:
        return "API Key for Gemini is not configured. Please set the GEMINI_API_KEY environment variable."

    # Prepare conversation history for Gemini API
    api_payload_contents = [{"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION}]}] + conversation_api_history[-10:]

    # ADDED generationConfig
    payload = {
        "contents": api_payload_contents,
        "generationConfig": {
            "temperature": 0.75,  # Adjust for creativity/factuality balance
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1500 # Increased for more detailed responses
        },
        "safetySettings": [ # Optional: Adjust safety settings if needed
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client: # Increased timeout
            response = await client.post(API_URL, json=payload)
            response.raise_for_status() # Raises an exception for 4XX/5XX responses
            result = response.json()

        # Process successful response
        if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
            bot_response_text = result['candidates'][0]['content']['parts'][0]['text']
            return strip_markdown(bot_response_text) # Will pass through markdown

        # Handle cases where response might be blocked or empty
        elif result.get('candidates') and result['candidates'][0].get('finishReason') == 'SAFETY':
            st.warning("The response was adjusted due to safety guidelines. Some information might be missing.")
            # Try to get any partial content if available, otherwise provide a generic message
            if result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
                 return strip_markdown(result['candidates'][0]['content']['parts'][0]['text']) + \
                        "\n\n*[Note: This response may have been modified due to safety settings.]*"
            return "I'm unable to provide a complete response to that specific query due to safety guidelines. Please try rephrasing."
        elif not result.get('candidates') and result.get('promptFeedback', {}).get('blockReason'):
             block_reason = result['promptFeedback']['blockReason']
             st.warning(f"Your request could not be processed because it was blocked: {block_reason}. Please rephrase your message.")
             return f"Your request was blocked by content filters ({block_reason}). Please avoid such topics or rephrase your query."
        else:
            st.error(f"Unexpected API response structure or empty candidates: {result}")
            return "I'm sorry, I couldn't generate a response at this time. (API structure issue or no content)"

    except httpx.RequestError as e:
        st.error(f"RequestError connecting to Gemini API: {e}")
        return "I'm having trouble connecting to my knowledge base. Please check your internet or try again later."
    except httpx.HTTPStatusError as e:
        st.error(f"HTTPStatusError from Gemini API: {e.response.status_code} - {e.response.text}")
        error_details = e.response.json()
        error_message = error_details.get("error", {}).get("message", "No specific error message provided by API.")
        return f"There was an issue with the API (Status {e.response.status_code}): {error_message}. Please try again later."
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return "I'm having a bit of trouble understanding right now. Could you try rephrasing?"

# --- Streamlit App UI and Logic ---

st.set_page_config(page_title="Fitness Chatbot Pro", page_icon="🏋️‍♂️", layout="centered")

st.title("🏋️‍♂️ Fitness Chatbot Pro")
st.caption("Your AI assistant for detailed fitness, exercise, and nutrition advice.")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your Fitness Chatbot Pro. Ask me anything about fitness for a detailed response!"}]
if "conversation_api_history" not in st.session_state:
    st.session_state.conversation_api_history = []


# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) # Use st.markdown to render formatted text

# Chat input
if prompt := st.chat_input("Ask for detailed fitness advice..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_api_history.append({"role": "user", "parts": [{"text": prompt}]})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Fitness bot is thinking...")
        
        # --- MODIFIED SECTION TO CORRECTLY CALL ASYNC FUNCTION ---
        bot_response = "" # Initialize bot_response
        try:
            # This is the standard way to run an async function from sync code in Python 3.7+
            bot_response = asyncio.run(get_chatbot_response(prompt, st.session_state.conversation_api_history))
        except RuntimeError as e:
            # This fallback is for specific cases where asyncio.run() might not be suitable
            # (e.g., if an event loop is already running in a way that conflicts, common in some frameworks/notebooks)
            if "cannot run current event loop" in str(e).lower() or "event loop is closed" in str(e).lower():
                # Try to get the existing loop or create a new one
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError: # No current event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                bot_response = loop.run_until_complete(get_chatbot_response(prompt, st.session_state.conversation_api_history))
            else:
                # Re-raise other RuntimeErrors or handle them
                st.error(f"An unexpected runtime error occurred while running async code: {e}")
                bot_response = "Sorry, I encountered a technical glitch. Please try again."
        except Exception as e:
            # Catch any other unexpected errors during the async call
            st.error(f"An error occurred while getting the bot response: {e}")
            bot_response = "I had trouble processing that. Could you try rephrasing?"
        # --- END OF MODIFIED SECTION ---
        
        message_placeholder.markdown(bot_response) # Display the actual response

    hide_streamlit_style = """
    <style>
    /* Hide the "Hosted with Streamlit" badge */
    .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK {
        display: none;
    }
    
    /* Also hide the main menu and footer for a cleaner look if desired */
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.session_state.conversation_api_history.append({"role": "model", "parts": [{"text": bot_response}]})

    if len(st.session_state.conversation_api_history) > 12: # Keep last 6 turns (user+model) + system prompt
        st.session_state.conversation_api_history = st.session_state.conversation_api_history[-12:]

if not GEMINI_API_KEY:
    st.error("FATAL: GEMINI_API_KEY is not set. The chatbot will not be able to connect to the Gemini API.")
    st.info("Please set the GEMINI_API_KEY environment variable. If deploying on Heroku, set it as a Config Var.")
