import os
import streamlit as st
from helper_functions.router import router
from faq_route import ingest_faq_data, faq_chain
from sql_route import sql_chain
from small_talk_route import small_talk_chain
import re
from datetime import datetime

# Resolve faqs_path relative to this file
base_dir = os.path.dirname(os.path.abspath(__file__))
faqs_path = os.path.join(base_dir, "resources", "Myntra_FAQ.csv")

img_path = os.path.join(base_dir, "assets", "thumbnail_image.jpeg")

# Display the image in the Streamlit app
st.image(img_path)

# Use session state to ingest FAQ data only once per session
if 'faqs_ingested' not in st.session_state:
    ingest_faq_data(faqs_path)
    st.session_state['faqs_ingested'] = True

def format_sql_response(response):
    lines = response.strip().split('\n')
    if not lines:
        return response

    table_header = "| Product | Price | Discount | Rating | Scraped Date |\n"
    table_separator = "|---------|-------|----------|--------|-------------|\n"
    table_rows = ""
    links_list = []

    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue

        parts = line.split(': Rs. ')
        if len(parts) < 2:
            continue

        product_name = parts[0].strip()
        product_name_clean = re.sub(r'\s*\((Men|Women|Unisex|Kids)\)', '', product_name).strip()

        remaining = parts[1]

        price_match = re.match(r'(\d+)', remaining)
        price = f"Rs. {price_match.group(1)}" if price_match else "NA"

        discount_match = re.search(r'(\d+)\s*percent off', remaining)
        discount = f"{discount_match.group(1)}%" if discount_match else "0%"

        rating_match = re.search(r'Rating:\s*([^\s,]+)', remaining)
        rating = rating_match.group(1) if rating_match else "NA"

        url_patterns = [
            r'\[(https?://[^\]]+)\]',
            r'https?://[^\s,\]]+',
            r'\[([^\]]*myntra[^\]]*)\]'
        ]

        url = ""
        for pattern in url_patterns:
            url_match = re.search(pattern, line)
            if url_match:
                url = url_match.group(1) if url_match.lastindex else url_match.group(0)
                url = url.strip('[]')
                break

        if url:
            links_list.append(url)

        date_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', remaining)
        if date_match:
            try:
                dt = datetime.fromisoformat(date_match.group(1))
                scraped_date = dt.strftime("%b %d, %Y %I:%M %p")
            except:
                scraped_date = "NA"
        else:
            scraped_date = "NA"

        table_rows += f"| {product_name_clean} | {price} | {discount} | {rating} | {scraped_date} |\n"

    result = table_header + table_separator + table_rows

    if links_list:
        result += "\n**Product Links:**\n\n"
        for idx, link in enumerate(links_list, 1):
            result += f"{idx}. {link}\n"
    else:
        result += "\n**Product Links:**\n\nNo links found in response.\n"

    return result


def ask(query):
    route = router(query).name
    if route == "faq":
        return faq_chain(query)
    elif route == "sql":
        raw_response = sql_chain(query)
        return format_sql_response(raw_response)
    elif route == "small_talk":
        return small_talk_chain(query)
    else:
        return f"Route {route} not implemented yet"


st.set_page_config(page_title="Myntra Shoe Assistant", page_icon="👟", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stApp {
        background-color: #000000;
        max-width: 1200px;
        margin: 0 auto;
    }
    .title-container {
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 1rem;
    }
    .title-text {
        font-size: 2.5rem;
        font-weight: 400;
        color: #ffffff;
        margin: 0;
    }
    .stChatMessage {
        background: transparent !important;
    }
    [data-testid="stChatMessageContent"] {
        background-color: #1a1a1a !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #ffffff !important;
    }
    [data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
        background-color: #2a2a2a !important;
    }
    [data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
        background-color: #1a1a1a !important;
    }
    .stChatInputContainer {
        background-color: #000000;
        padding-top: 1rem;
    }
    input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    table {
        color: #ffffff !important;
        width: 100%;
    }
    th {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        padding: 0.5rem !important;
    }
    td {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        padding: 0.5rem !important;
    }
    a {
        color: #4da6ff !important;
    }
    .disclaimer {
        text-align: center;
        font-size: 0.65rem;
        color: #666666;
        padding: 2rem 1rem 1rem 1rem;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="title-container">
        <h1 class="title-text">👟 Myntra Shoe Assistant Chatbot</h1>
    </div>
""", unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

query = st.chat_input("Write your query:")

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state['messages'].append({"role": "user", "content": query})

    response = ask(query)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state['messages'].append({"role": "assistant", "content": response})

    st.rerun()

st.markdown("""
    <div class="disclaimer">
        ©All listings and product data are the sole property of Myntra Designs Private Limited.
    </div>
""", unsafe_allow_html=True)
``````python
import os
import streamlit as st
from helper_functions.router import router
from faq_route import ingest_faq_data, faq_chain
from sql_route import sql_chain
from small_talk_route import small_talk_chain
import re
from datetime import datetime

# Resolve faqs_path relative to this file
base_dir = os.path.dirname(os.path.abspath(__file__))
faqs_path = os.path.join(base_dir, "resources", "Myntra_FAQ.csv")

img_path = os.path.join(base_dir, "assets", "thumbnail_image.jpeg")

# Display the image in the Streamlit app
st.image(img_path)

# Use session state to ingest FAQ data only once per session
if 'faqs_ingested' not in st.session_state:
    ingest_faq_data(faqs_path)
    st.session_state['faqs_ingested'] = True


def format_sql_response(response):
    lines = response.strip().split('\n')
    if not lines:
        return response

    table_header = "| Product | Price | Discount | Rating | Scraped Date |\n"
    table_separator = "|---------|-------|----------|--------|-------------|\n"
    table_rows = ""
    links_list = []

    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue

        parts = line.split(': Rs. ')
        if len(parts) < 2:
            continue

        product_name = parts[0].strip()
        product_name_clean = re.sub(r'\s*\((Men|Women|Unisex|Kids)\)', '', product_name).strip()

        remaining = parts[1]

        price_match = re.match(r'(\d+)', remaining)
        price = f"Rs. {price_match.group(1)}" if price_match else "NA"

        discount_match = re.search(r'(\d+)\s*percent off', remaining)
        discount = f"{discount_match.group(1)}%" if discount_match else "0%"

        rating_match = re.search(r'Rating:\s*([^\s,]+)', remaining)
        rating = rating_match.group(1) if rating_match else "NA"

        url_patterns = [
            r'\[(https?://[^\]]+)\]',
            r'https?://[^\s,\]]+',
            r'\[([^\]]*myntra[^\]]*)\]'
        ]

        url = ""
        for pattern in url_patterns:
            url_match = re.search(pattern, line)
            if url_match:
                url = url_match.group(1) if url_match.lastindex else url_match.group(0)
                url = url.strip('[]')
                break

        if url:
            links_list.append(url)

        date_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', remaining)
        if date_match:
            try:
                dt = datetime.fromisoformat(date_match.group(1))
                scraped_date = dt.strftime("%b %d, %Y %I:%M %p")
            except:
                scraped_date = "NA"
        else:
            scraped_date = "NA"

        table_rows += f"| {product_name_clean} | {price} | {discount} | {rating} | {scraped_date} |\n"

    result = table_header + table_separator + table_rows

    if links_list:
        result += "\n**Product Links:**\n\n"
        for idx, link in enumerate(links_list, 1):
            result += f"{idx}. {link}\n"
    else:
        result += "\n**Product Links:**\n\nNo links found in response.\n"

    return result


def ask(query):
    route = router(query).name
    if route == "faq":
        return faq_chain(query)
    elif route == "sql":
        raw_response = sql_chain(query)
        return format_sql_response(raw_response)
    elif route == "small_talk":
        return small_talk_chain(query)
    else:
        return f"Route {route} not implemented yet"


st.set_page_config(page_title="Myntra Shoe Assistant", page_icon="👟", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stApp {
        background-color: #000000;
        max-width: 1200px;
        margin: 0 auto;
    }
    .title-container {
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 1rem;
    }
    .title-text {
        font-size: 2.5rem;
        font-weight: 400;
        color: #ffffff;
        margin: 0;
    }
    .stChatMessage {
        background: transparent !important;
    }
    [data-testid="stChatMessageContent"] {
        background-color: #1a1a1a !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #ffffff !important;
    }
    [data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
        background-color: #2a2a2a !important;
    }
    [data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
        background-color: #1a1a1a !important;
    }
    .stChatInputContainer {
        background-color: #000000;
        padding-top: 1rem;
    }
    input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    table {
        color: #ffffff !important;
        width: 100%;
    }
    th {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        padding: 0.5rem !important;
    }
    td {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        padding: 0.5rem !important;
    }
    a {
        color: #4da6ff !important;
    }
    .disclaimer {
        text-align: center;
        font-size: 0.65rem;
        color: #666666;
        padding: 2rem 1rem 1rem 1rem;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="title-container">
        <h1 class="title-text">👟 Myntra Shoe Assistant Chatbot</h1>
    </div>
""", unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

query = st.chat_input("Write your query:")

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state['messages'].append({"role": "user", "content": query})

    response = ask(query)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state['messages'].append({"role": "assistant", "content": response})

    st.rerun()

st.markdown("""
    <div class="disclaimer">
        ©All listings and product data are the sole property of Myntra Designs Private Limited.
    </div>
""", unsafe_allow_html=True)
