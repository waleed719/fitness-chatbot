# AI Fitness Chatbot

## Overview

Welcome to the AI Fitness Chatbot Project! This application is designed to be your personalized AI fitness companion, helping you on your journey to a healthier lifestyle. Whether you're a beginner just starting out or a seasoned athlete looking to optimize your routine, this chatbot aims to provide valuable guidance and support.

It leverages the power of Google's Gemini Large Language Model (LLM) and a curated set of frequently asked questions to offer tailored advice, exercise instructions, and answer your fitness-related questions.

## Features

This AI Fitness Chatbot includes features such as:

* **Personalized Workout Recommendations:** Get workout plans and advice tailored to your specific goals (e.g., weight loss, muscle building, endurance), current experience level, and preferences, powered by the Gemini LLM.
* **Detailed Exercise Descriptions & Fitness Q&A:** Access clear instructions, form tips, and answers to a wide range of fitness, nutrition, and motivation questions through interaction with the AI.
* **Quick Questions (FAQs):** A predefined list of common fitness questions with readily available answers for quick guidance.
* **Interactive Interface:** Engage with the chatbot through an easy-to-use web interface built with Streamlit.
* **Safety-Focused Advice:** The chatbot is programmed with system instructions that prioritize user safety, including disclaimers to consult professionals.

## Technology Stack

The project is built using a combination of modern technologies:

* **Core Programming Language:** Python
* **AI / Machine Learning:**
    * **Google Gemini API (gemini-2.0-flash):** Used for natural language understanding, generating personalized fitness advice, and answering user queries.
* **User Interface (UI):**
    * **Streamlit:** A Python framework for rapidly building interactive web applications.
* **API Interaction:**
    * **httpx:** An asynchronous HTTP client for making API requests to the Gemini service.
* **Environment Management:**
    * **python-dotenv:** For managing API keys and other environment variables.
* **Data/Knowledge Source:**
    * The primary knowledge comes from the **Google Gemini LLM**.
    * A built-in Python dictionary (`FITNESS_FAQS`) provides answers to a predefined set of common questions.

## Setup and Installation

To get this project up and running on your local machine, follow these general steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/waleed719/fitness-chatbot
    cd fitness-chatbot
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    The project should have a `requirements.txt` file listing all necessary Python packages (e.g., `streamlit`, `httpx`, `python-dotenv`).
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up API Keys:**
    This project requires an API key for the Google Gemini service.
    * Create a `.env` file in the root directory of the project.
    * Add your API key to this file:
        ```env
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
        ```
    * The application uses `python-dotenv` to load this environment variable.

## Usage

Once the setup is complete, you can run the application using Streamlit:

1.  **Run the Streamlit application:**
    ```bash
    streamlit run streamlit_app.py
    ```

2.  **Access the chatbot:**
    Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

## Deployment

Deploying this application can be done in several ways, depending on your needs:

* **Streamlit Community Cloud:**
    * Streamlit offers a free platform to deploy public Streamlit apps directly from GitHub repositories. This is often the easiest way to share your project. Ensure your `GEMINI_API_KEY` is set as a secret in the Streamlit Cloud settings.
* **Cloud Platforms (e.g., AWS, Google Cloud, Azure):**
    * For more control, scalability, or private deployments, you can host the application on a cloud virtual server.
    * This typically involves:
        * Setting up the server environment (installing Python, Git, etc.).
        * Cloning your repository.
        * Installing dependencies.
        * Configuring the `GEMINI_API_KEY` as an environment variable on the server.
        * Running the Streamlit application using a process manager (like `tmux`, `screen`, or `systemd`) to keep it alive.
        * Configuring a web server (like Nginx or Apache) as a reverse proxy (optional but recommended for production).
        * Setting up firewall rules to allow traffic on the appropriate ports.

## Contributing

If you'd like to contribute to this project, please reach out to repository owners (`waleed719` | `man-exe` | `MuhammadMubeenButt`). Typical contributions might involve:
* Adding new features or FAQs
* Improving existing functionality or the system prompt for the LLM
* Reporting or fixing bugs
* Enhancing the user interface
* Improving documentation
