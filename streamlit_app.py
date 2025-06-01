import streamlit as st
import httpx
import os
import asyncio
from dotenv import load_dotenv
import uuid

st.set_page_config(layout="wide")

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

FITNESS_FAQS = {
    "How can I lose weight?": "Losing weight effectively usually involves a combination of regular physical activity and a balanced, calorie-controlled diet. Focusing on whole foods, lean protein, and plenty of vegetables can be very helpful. What kind of physical activities do you enjoy, or are there any dietary approaches you're curious about? This will help me give more tailored suggestions for exercise or healthy eating habits.",
    "Suggest a good workout for beginners!": "Absolutely! For beginners, it's often best to start with full-body workouts 2-3 times a week to build a solid foundation. This could include bodyweight exercises like **Bodyweight Squats**, **Push-ups** (on knees if needed), **Lunges**, and **Planks**. Do you prefer to work out at home, or do you have access to gym equipment? And roughly how much time are you looking to dedicate per session?",
    "What are some good ABS exercises?": "For targeting your abdominal muscles and strengthening your core, exercises like **Crunches**, **Leg Raises**, **Plank variations** (like forearm plank or side plank), and **Russian Twists** are effective. Remember, a strong core contributes to overall stability and posture! Are you looking to add these to an existing routine, or would you like ideas for a dedicated core workout?",
    "How can I eat healthier?": "That's a great goal! Eating healthier generally means focusing on whole, unprocessed foods, increasing your intake of fruits and vegetables, choosing lean protein sources (like chicken, fish, beans, or tofu), incorporating healthy fats (like avocados or nuts), and ensuring you're well-hydrated. Are you interested in tips for meal planning, understanding macronutrients (proteins, carbs, fats), or perhaps some healthy snack ideas to get you started?",
    "I have no motivation to exercise!": "It's completely normal to feel a lack of motivation sometimes! Setting small, achievable goals can make a big difference – even a 10-minute walk is a win. Finding an activity you genuinely enjoy is also key, as it makes exercise feel less like a chore. What kind of activities have you considered or enjoyed in the past, or what usually makes you feel unmotivated?",
    "What should I eat before a workout?": "Fueling your body before a workout can help with energy and performance. Generally, having some easily digestible carbohydrates about 1-2 hours beforehand is a good idea. This could be something like a banana, a small bowl of oatmeal, or a piece of fruit. What kind of workout are you planning, and how long will it be? That can help refine the suggestion.",
    "What should I eat after a workout?": "After a workout, it's beneficial to consume a combination of protein and carbohydrates within an hour or two to aid muscle recovery and replenish energy stores. Good options include Greek yogurt with berries, a protein shake with a banana, chicken breast with quinoa, or a tuna sandwich on whole-wheat bread. What are your main fitness goals, such as muscle building or endurance improvement?",
    "Can you suggest some cardio exercises!": "Certainly! Cardiovascular exercises, or 'cardio,' are great for heart health, endurance, and burning calories. Popular options include **Running** or **Jogging**, **Cycling** (indoors or outdoors), **Swimming**, **Brisk Walking**, using an **Elliptical Trainer**, or even **Dancing**. Are you looking for low-impact options, something you can do at home, or are you training for a specific endurance goal?"
}

SYSTEM_INSTRUCTION = (
    "\n**Core Principle: User Safety First.** Always preface advice with a disclaimer, especially on first interaction or when suggesting new routines/significant changes. Example: 'Remember to consult with your doctor or a qualified fitness professional before starting any new exercise program or making significant changes to your diet. My suggestions are for informational purposes only and are not a substitute for professional medical advice.'"
    "\n\nWhen a user interacts with you:"
    "\n1. If the user's query is clearly a request for fitness guidance (e.g., 'suggest a workout for abs,' 'how can I eat healthier?', 'I need motivation to exercise'):"
    "   a. Try to understand their specific goals, current fitness level, preferences, and any limitations they mention. If the request is vague (e.g., 'help me get fit'), ask clarifying questions "
    "      like 'What are your main fitness goals (e.g., weight loss, muscle gain, endurance, flexibility)?', 'What's your current experience with exercise?', 'Do you have access to a gym or prefer home workouts?', 'How much time can you dedicate?', or 'Are there any types of activities you particularly enjoy or dislike?'. "
    "   b. Aim to provide 2-4 distinct and actionable suggestions if possible (e.g., specific exercises, a sample workout structure, meal ideas). For each suggestion, briefly explain its benefits, how to perform it correctly (if an exercise, with emphasis on form and safety), or why it aligns with their goals. "
    "   c. Use markdown formatting to make your answers clear and engaging: "
    "      - Use bolding for exercise names, routine titles, or key concepts (e.g., '**Push-ups**', '**Beginner Full Body Routine**', '**Calorie Deficit**'). "
    "      - Use bullet points (hyphens or asterisks) for lists of exercises, tips, or meal components. "
    "      - Use paragraphs for explanations and instructions. "
    "   d. Utilize the provided conversation history from the current session effectively. "
    "      - Avoid re-suggesting exercises or plans already discussed and dismissed in this ongoing conversation unless the user asks for them again or for more details/modifications."
    "      - If the user has mentioned goals, preferences, limitations, or progress earlier in the current conversation, acknowledge this and incorporate that context into your current suggestions to make them more personalized and coherent. For example, 'Since you mentioned you want to focus on upper body strength and have access to dumbbells, here are a couple of routines...'"
    "   e. Always prioritize safety. If a user mentions a potential injury or medical condition, gently remind them to consult a healthcare professional and offer to provide general fitness information that doesn't exacerbate their condition, if appropriate and safe. (e.g., 'I can't give advice for specific injuries, but if you're cleared for gentle activity, perhaps some light stretching or mobility work could be discussed?')"
    "\n2. If the user's query is not a request for fitness guidance (e.g., asking 'What is the capital of Spain?', 'Who are you beyond a fitness bot?', 'Tell me a story?', 'What's the weather like?', 'Calculate my mortgage'):"
    "   a. You must politely decline to answer the question directly. "
    "   b. Clearly state your specialized role as a Fitness Chatbot. "
    "   c. Immediately attempt to redirect the conversation back to fitness, exercise, nutrition, or motivation. "
    "   d. Example refusals: "
    "      - User: 'What's the latest news?' You: 'My focus is on helping you with your fitness journey! I can't provide news updates, but I can definitely help you plan your next workout or offer some healthy eating tips. What are you working on today?'"
    "      - User: 'Can you explain quantum physics?' You: 'I'm designed to be your go-to for fitness and nutrition information. While I can't explain quantum physics, perhaps you'd like some tips on improving your workout intensity or understanding macronutrients?'"
    "      - User: 'Tell me about your creators.' You: 'I'm a Fitness Chatbot AI, here to assist you with your exercise routines, nutrition questions, and keeping you motivated! Do you have any fitness goals you'd like to discuss?'"
    "\n3. If a user asks for something you cannot ethically or safely provide (e.g., advice on illegal substances, promotion of eating disorders, extremely dangerous exercises, or specific medical advice/diagnosis): "
    "   a. Politely and firmly state that you cannot help with that specific request due to safety, ethical, or scope limitations. "
    "   b. Do not be preachy, but be clear. "
    "   c. Offer to help with safe and appropriate fitness-related topics. Example: 'Icannot provide guidance on [harmful request]. My purpose is to promote health and safety. However, I can help you with creating a balanced workout plan or offer tips for healthy eating if you're interested.'"
    "\n4. Do not invent exercises, nutritional information, or unsubstantiated fitness claims. If you are unsure about a very specific or obscure request, or if it borders on medical advice: "
    "   a. State that you don't have specific information on that item or that it's outside your scope. "
    "   b. Offer to provide information on more general, established, and safe alternatives or related concepts. "
    "   c. Reiterate the importance of consulting with qualified professionals for specific or complex needs. Example: 'I don't have information on that specific unconventional training method. It's always best to stick to well-researched exercises or consult a certified trainer for such specialized requests. Would you like help with some foundational strength exercises instead?'"
    "\n5. Your tone should be helpful, friendly, encouraging, motivating, and empathetic, but also firm on matters of safety and scope. "
    "\n6. Exception for factual fitness-related questions: If a user asks a factual question directly related to fitness, exercise, or general nutrition that could lead to or support guidance (e.g., 'What muscles do lunges work?', 'How many calories in a banana?', 'What is HIIT?'):"
    "   a. You can provide a brief, concise, and accurate answer. "
    "   b. Then, try to pivot to personalized advice or a recommendation. Do not go into overly lengthy explanations. "
    "   c. Example: 'Lunges primarily work your quadriceps, glutes, and hamstrings, and also engage your core for stability. They are a great compound exercise! Would you like to incorporate them into a leg workout routine, or learn some variations?'"
    "\n\nStick to your role as a Fitness Chatbot AI diligently. Your goal is to guide and support users in their fitness journey safely and effectively, not to be a general conversationalist or a substitute for professional medical or certified expert advice. Be mindful of the ongoing conversation to provide a seamless, intelligent, and motivating fitness support experience."
)

def strip_markdown(text):
    st.subheader("Our Team")
    group_members = [
        {"name": "Waleed Qamar", "github_url": "https://github.com/waleed719"},
        {"name": "Muhammad Mubeen Butt", "github_url": "https://github.com/MuhammadMubeenButt"},
        {"name": "Muhammad Musa", "github_url": "https://github.com/man-exe"},
    ]
    for member in group_members:
        st.markdown(f"* [{member['name']}]({member['github_url']})")
    st.markdown("") 

    st.markdown("---") 
    st.subheader("Project Link")
    st.link_button("View Source Code", "https://github.com/waleed719/fitness-chatbot", use_container_width=True, type="secondary")
    st.caption("Built with Streamlit & Gemini")
    return text 


async def get_chatbot_response_from_api(user_message: str, conversation_api_history: list) -> str:
    if not GEMINI_API_KEY:
        return "API Key for Gemini is not configured. Please set the GEMINI_API_KEY environment variable."

    api_payload_contents = [{"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION}]}] + \
                           conversation_api_history[-10:] 

    payload = {
        "contents": api_payload_contents,
        "generationConfig": {
            "temperature": 0.75,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1500
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
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
            safety_message = "I'm unable to provide a complete response to that specific query due to safety guidelines."
            if result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
                safety_message = strip_markdown(result['candidates'][0]['content']['parts'][0]['text']) + \
                                 "\n\n*[Note: This response may have been modified due to safety settings.]*"
            return f"SAFETY_WARNING::{safety_message}"
        elif not result.get('candidates') and result.get('promptFeedback', {}).get('blockReason'):
            block_reason = result['promptFeedback']['blockReason']
            return f"BLOCKED_PROMPT::Your request could not be processed because it was blocked: {block_reason}. Please rephrase your message."
        else:
            print(f"Unexpected API response structure or empty candidates: {result}")
            return "ERROR::I'm sorry, I couldn't generate a response at this time. (API structure issue or no content)"

    except httpx.RequestError as e:
        print(f"RequestError connecting to Gemini API: {e}")
        return f"ERROR::I'm having trouble connecting to my knowledge base. Please check your internet or try again later."
    except httpx.HTTPStatusError as e:
        print(f"HTTPStatusError from Gemini API: {e.response.status_code} - {e.response.text}")
        error_details = {}
        try:
            error_details = e.response.json() 
        except Exception:
            pass 
        error_message_from_api = error_details.get("error", {}).get("message", "No specific error message provided by API.")
        return f"ERROR::There was an issue with the API (Status {e.response.status_code}): {error_message_from_api}. Please try again later."
    except Exception as e: 
        print(f"An unexpected error occurred in API call: {e}")
        return "ERROR::I'm having a bit of trouble understanding right now. Could you try rephrasing?"

st.title("💬 Fitness Chatbot Pro")
st.caption("Your AI assistant for detailed fitness, exercise, and nutrition advice.")

if "fitness_chatbot_messages" not in st.session_state:
    st.session_state.fitness_chatbot_messages = [{"id": str(uuid.uuid4()), "role": "assistant", "content": "Hello! I'm your Fitness Chatbot Pro. Ask me anything about fitness, or select a common question below!"}]
if "fitness_chatbot_api_history" not in st.session_state:
    st.session_state.fitness_chatbot_api_history = [] 
if "user_started_conversation" not in st.session_state:
    st.session_state.user_started_conversation = False


if not st.session_state.user_started_conversation:
    st.subheader("💡 Quick Questions (FAQs)")
    num_faq_columns = 2
    faq_cols = st.columns(num_faq_columns)
    faq_items_list = list(FITNESS_FAQS.items())

    for i, (question, answer) in enumerate(faq_items_list):
        col_index = i % num_faq_columns
        if faq_cols[col_index].button(question, key=f"faq_btn_{i}", use_container_width=True):
            st.session_state.user_started_conversation = True
            user_faq_msg_id = str(uuid.uuid4())
            st.session_state.fitness_chatbot_messages.append({"id": user_faq_msg_id, "role": "user", "content": question})
            st.session_state.fitness_chatbot_api_history.append({"role": "user", "parts": [{"text": question}]})
            
            bot_faq_msg_id = str(uuid.uuid4())
            st.session_state.fitness_chatbot_messages.append({"id": bot_faq_msg_id, "role": "assistant", "content": answer})
            st.session_state.fitness_chatbot_api_history.append({"role": "model", "parts": [{"text": answer}]})
            st.rerun() 
    st.markdown("---")

for message in st.session_state.fitness_chatbot_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

input_label = "Ask for detailed fitness advice..."
if prompt := st.chat_input(input_label, key="fitness_chat_main_input", disabled=not GEMINI_API_KEY):
    st.session_state.user_started_conversation = True 

    user_msg_id = str(uuid.uuid4())
    st.session_state.fitness_chatbot_messages.append({"id": user_msg_id, "role": "user", "content": prompt})
    st.session_state.fitness_chatbot_api_history.append({"role": "user", "parts": [{"text": prompt}]})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Fitness bot is thinking... 🧠")

        bot_response_content = ""
        normalized_prompt = prompt.lower().strip()
        matched_faq_answer = None

        for faq_q, faq_a in FITNESS_FAQS.items():
            if faq_q.lower() == normalized_prompt:
                matched_faq_answer = faq_a
                break
        
        if matched_faq_answer:
            bot_response_content = matched_faq_answer
        else:
            try:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed(): 
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError: 
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                api_response = loop.run_until_complete(
                    get_chatbot_response_from_api(prompt, st.session_state.fitness_chatbot_api_history)
                )

                if api_response.startswith("ERROR::"):
                    st.error(api_response.replace("ERROR::", "")) 
                    bot_response_content = "Sorry, I encountered a technical problem. Please try again."
                elif api_response.startswith("SAFETY_WARNING::"):
                    st.warning("The response was adjusted due to safety guidelines. Some information might be missing.")
                    bot_response_content = api_response.replace("SAFETY_WARNING::", "")
                elif api_response.startswith("BLOCKED_PROMPT::"):
                    st.warning(api_response.replace("BLOCKED_PROMPT::", ""))
                    bot_response_content = "I cannot respond to that query. Please rephrase or ask something else."
                else:
                    bot_response_content = api_response
            
            except RuntimeError as e: 
                if "cannot run current event loop" in str(e).lower() or "event loop is closed" in str(e).lower():
                    st.warning("Retrying API call due to event loop issue...")
                    try:
                        loop = asyncio.new_event_loop() 
                        asyncio.set_event_loop(loop)
                        api_response = loop.run_until_complete(
                            get_chatbot_response_from_api(prompt, st.session_state.fitness_chatbot_api_history)
                        )
                        if api_response.startswith("ERROR::"): bot_response_content = "Sorry, an error occurred on retry."
                        elif api_response.startswith("SAFETY_WARNING::"): bot_response_content = api_response.replace("SAFETY_WARNING::", "")
                        elif api_response.startswith("BLOCKED_PROMPT::"): bot_response_content = "Request blocked on retry."
                        else: bot_response_content = api_response
                    except Exception as inner_e:
                        st.error(f"Critical error in event loop management during retry: {inner_e}")
                        bot_response_content = "A critical error occurred. Please refresh."
                else: 
                    st.error(f"An unexpected runtime error occurred: {e}")
                    bot_response_content = "Sorry, I encountered a technical glitch."
            except Exception as e: 
                st.error(f"An error occurred while getting the bot response: {e}")
                bot_response_content = "I had trouble processing that. Could you try rephrasing?"

        message_placeholder.markdown(bot_response_content) 

    bot_msg_id = str(uuid.uuid4())
    st.session_state.fitness_chatbot_messages.append({"id": bot_msg_id, "role": "assistant", "content": bot_response_content})
    st.session_state.fitness_chatbot_api_history.append({"role": "model", "parts": [{"text": bot_response_content}]})

    if len(st.session_state.fitness_chatbot_api_history) > 12: 
        st.session_state.fitness_chatbot_api_history = st.session_state.fitness_chatbot_api_history[-12:]
    
    st.rerun() 

if not GEMINI_API_KEY:
    st.error("🔴 FATAL: GEMINI_API_KEY is not set in your .env file or environment variables.")
    st.info("Please create a `.env` file in the project root directory and add `GEMINI_API_KEY='YOUR_API_KEY'`.")
    st.info("If deploying, set this as an environment variable or secret on your hosting platform.")
    st.stop()
