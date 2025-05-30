import streamlit as st
import httpx
import os
import re
import asyncio
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

FITNESS_FAQS = {
    "what is your name": "I am a Fitness Chatbot, designed to help you with your fitness queries!",
    "how to lose weight": "Losing weight typically involves a combination of a balanced diet and regular exercise. Consider consulting a nutritionist or a fitness expert for a personalized plan.",
    "best exercises for beginners": "For beginners, bodyweight exercises like squats, push-ups (modified if needed), planks, and lunges are great. Walking or light jogging are also excellent starting points.",
    "how much water should I drink daily": "Generally, it's recommended to drink around 8 glasses (about 2 liters) of water daily, but this can vary based on activity level, climate, and individual needs.",
    "what is protein good for": "Protein is essential for muscle repair and growth, hormone production, and overall body function. It's crucial for anyone engaging in physical activity.",
    "how to build muscle": "Building muscle requires progressive overload in strength training, adequate protein intake, and sufficient rest. Consistency is key!",
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


def strip_markdown(text):
    return text

async def get_chatbot_response(user_message: str, conversation_api_history: list) -> str:
    normalized_message = user_message.lower().strip()

    if normalized_message in FITNESS_FAQS:
        return FITNESS_FAQS[normalized_message]

    if not GEMINI_API_KEY:
        return "API Key for Gemini is not configured. Please set the GEMINI_API_KEY environment variable."

    api_payload_contents = [{"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION}]}] + conversation_api_history[-10:]

    payload = {
        "contents": api_payload_contents,
        "generationConfig": {
            "temperature": 0.75,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1500
        "safetySettings": [ 
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        }
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()
            result = response.json()

        if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
            bot_response_text = result['candidates'][0]['content']['parts'][0]['text']
            return strip_markdown(bot_response_text)

        elif result.get('candidates') and result['candidates'][0].get('finishReason') == 'SAFETY':
            st.warning("The response was adjusted due to safety guidelines. Some information might be missing.")
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


st.set_page_config(page_title="Fitness Chatbot Pro", page_icon="🏋️‍♂️", layout="centered")

custom_theme_css = """
<style>
/* Define CSS variables for easier color management */
:root {
    --primary-color: #E63946; /* Strong red for accents */
    --background-color: #1A1A1A; /* Very dark main background */
    --secondary-background-color: #262730; /* Slightly lighter dark for sidebar, inputs */
    --text-color: #FAFAFA; /* Off-white for general text */
    --chat-bubble-user-color: #31333F; /* Darker grey for user chat bubbles */
    --chat-bubble-assistant-color: var(--secondary-background-color); /* Assistant uses secondary background */
    --border-color: #444444; /* Darker border for elements */
}

/* Overall app background */
.stApp {
    background-color: var(--background-color) !important;
}

/* Main content area background */
body {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important; /* Default text color */
}

/* All text elements for consistency */
h1, h2, h3, h4, h5, h6, p, li, span, div, .stMarkdown, .stText {
    color: var(--text-color) !important;
}

/* Streamlit Header (title, caption) */
/* Targeting by generic class that covers titles/captions */
.st-emotion-cache-nahz7x { /* Adjust this class if needed, it often refers to header/title container */
    color: var(--text-color) !important;
}
.st-emotion-cache-1r6c0d6 { /* Another common class for Streamlit titles */
    color: var(--text-color) !important;
}

/* Sidebar styling */
.stSidebar {
    background-color: var(--secondary-background-color) !important;
    color: var(--text-color) !important;
}

/* Sidebar header/title color */
.stSidebar .st-emotion-cache-1cpx6h, .stSidebar .st-emotion-cache-109040r { 
    color: var(--text-color) !important;
}

/* Sidebar links */
.stSidebar a {
    color: var(--primary-color) !important; /* Make links stand out */
    text-decoration: none; /* Remove underline */
}
.stSidebar a:hover {
    color: lightgray !important; /* Lighter hover color */
    text-decoration: underline; /* Add underline on hover */
}

/* Buttons */
.stButton button {
    background-color: var(--primary-color) !important;
    color: var(--text-color) !important;
    border: 1px solid var(--primary-color) !important;
    border-radius: 5px !important;
    transition: background-color 0.3s ease;
}
.stButton button:hover {
    background-color: #BB2D3A !important; /* Slightly darker red on hover */
    color: white !important;
    border-color: #BB2D3A !important;
}

/* Input fields (text input, number input, text area, selectbox) */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div > input { /* For selectbox input area */
    background-color: var(--secondary-background-color) !important;
    color: var(--text-color) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 5px !important;
}
/* For the dropdown arrow of selectbox */
.stSelectbox > div > div > div > div {
    color: var(--text-color) !important;
}

/* Chat message bubbles */
.stChatMessage {
    padding: 10px !important;
    border-radius: 10px !important;
    margin-bottom: 10px !important;
}

/* User chat bubble */
.stChatMessage.st-emotion-cache-user .stMarkdown { /* Specific class for user message container */
    background-color: var(--chat-bubble-user-color) !important;
    color: var(--text-color) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

/* Assistant chat bubble */
.stChatMessage.st-emotion-cache-assistant .stMarkdown { /* Specific class for assistant message container */
    background-color: var(--chat-bubble-assistant-color) !important;
    color: var(--text-color) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

/* Chat input box (outer container) */
/* These classes can change with Streamlit updates. Use browser dev tools if issues persist. */
.st-emotion-cache-1oe5f0g, .st-emotion-cache-f1x29i, .st-emotion-cache-1d37b6c { 
    background-color: var(--secondary-background-color) !important;
    border-top: 1px solid var(--border-color) !important;
    padding: 10px 0 !important;
}
/* The actual text input field within chat input */
.st-emotion-cache-1ae4qfn { 
    background-color: var(--secondary-background-color) !important;
    color: var(--text-color) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 5px !important;
}

/* Hide Streamlit branding and GitHub icon - existing (with !important for robustness) */
.viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK {
    display: none !important;
    visibility: hidden !important;
}

#MainMenu {
    display: none !important;
    visibility: hidden !important;
}
footer {
    display: none !important;
    visibility: hidden !important;
}
#GithubIcon {
    display: none !important;
    visibility: hidden !important;
}
</style>
"""
st.markdown(custom_theme_css, unsafe_allow_html=True)


st.title("🏋️‍♂️ Fitness Chatbot Pro")
st.caption("Your AI assistant for detailed fitness, exercise, and nutrition advice.")

st.sidebar.title("Our Team")
st.sidebar.markdown("---")

group_members = [
    {"name": "Waleed Qamar", "github_url": "https://github.com/waleed719"},
    {"name": "Muhammad Mubeen Butt", "github_url": "https://github.com/MuhammadMubeenButt"},
    {"name": "Muhammad Musa", "github_url": "https://github.com/man-exe"},
]

for member in group_members:
    st.sidebar.markdown(f"**[{member['name']}]({member['github_url']})**")
    st.sidebar.markdown("")
st.sidebar.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your Fitness Chatbot Pro. Ask me anything about fitness for a detailed response!"}]
if "conversation_api_history" not in st.session_state:
    st.session_state.conversation_api_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("Ask for detailed fitness advice..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_api_history.append({"role": "user", "parts": [{"text": prompt}]})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Fitness bot is thinking...")
        
        bot_response = ""
        try:
            bot_response = asyncio.run(get_chatbot_response(prompt, st.session_state.conversation_api_history))
        except RuntimeError as e:
            if "cannot run current event loop" in str(e).lower() or "event loop is closed" in str(e).lower():
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                bot_response = loop.run_until_complete(get_chatbot_response(prompt, st.session_state.conversation_api_history))
            else:
                st.error(f"An unexpected runtime error occurred while running async code: {e}")
                bot_response = "Sorry, I encountered a technical glitch. Please try again."
        except Exception as e:
            st.error(f"An error occurred while getting the bot response: {e}")
            bot_response = "I had trouble processing that. Could you try rephrasing?"
        
        message_placeholder.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.session_state.conversation_api_history.append({"role": "model", "parts": [{"text": bot_response}]})

    if len(st.session_state.conversation_api_history) > 12:
        st.session_state.conversation_api_history = st.session_state.conversation_api_history[-12:]

if not GEMINI_API_KEY:
    st.error("FATAL: GEMINI_API_KEY is not set. The chatbot will not be able to connect to the Gemini API.")
    st.info("Please set the GEMINI_API_KEY environment variable. If deploying on Heroku, set it as a Config Var.")
