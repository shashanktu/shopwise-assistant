import streamlit as st
from PIL import Image
import google.generativeai as genai  
import sqlite3
import random
import os
import logging
from dotenv import load_dotenv
load_dotenv()

# hi Shashank
#Hi Anil
 
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Application started.")
 
db = 'synthetic.db'
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
 
# Page Configuration
st.set_page_config(page_title="ShopWise Assistant", page_icon="", layout="wide")
 
# Custom styling
st.markdown("""
<style>
        .centered {
            text-align: center;
        }
</style>
""", unsafe_allow_html=True)
 
st.markdown("""
<style>
        .centered-buttons {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
        }
</style>
""", unsafe_allow_html=True)
 

st.markdown('<h1 class="centered">Welcome to ShopWise Assistant </h1>', unsafe_allow_html=True)
image_url = "https://valuemomentum.club/wp-content/uploads/2024/11/shutterstock_2459700141-scaled.jpg"
st.markdown(f"""
<div style="display: flex; justify-content: center; align-items: center;">
<img src="{image_url}" style="width: 650px; height: 350px; object-fit: cover; border-radius: 10px;">
</div>
""", unsafe_allow_html=True)
 

 
def read_sql_query(sql, db):
    logging.debug(f"Executing SQL query: {sql}")
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        if not rows:
            logging.warning("SQL query returned no results.")
            return "No results found."
        # Log and return rows
        logging.debug(f"Query results: {rows}")
        return rows
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return f"Database error: {str(e)}"
 
def get_gemini_response(user_message):
    logging.info(f"Generating Gemini response for: {user_message}")
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash-8b')  # Ensure the model name is correct
        response = model.generate_content(f"You are a helpful assistant. User: {user_message}")
        if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
            answer = response.candidates[0].content.parts[0].text
            return answer
        else:
            return "Sorry, I couldn't get a response from Gemini. Please try again."
    except Exception as e:
        logging.error(f"Error generating Gemini response: {e}")
        return f"Error: {str(e)}"
def bot_reply(query_result,user_message):
    reply_prompt = f"Now according to the response {query_result} generate a reply in a human-friendly manner for the query {user_message} do not ask any more questions."
    response_content = get_gemini_response(reply_prompt)
    return response_content

def is_greeting(user_message):
    greetings = ["hello", "hi ", "hey ", "greetings", "howdy", "good morning", "good afternoon", "good evening"]
    return any(greeting in user_message.lower() for greeting in greetings)
 
def get_random_greeting():
    greetings = [
        "Hello! How can I assist you today?",
        "Hi there! What can I do for you?",
        "Greetings! Let me know how I can help.",
        "Hey! What brings you here today?",
        "Hello! Feel free to ask me anything."
    ]
    return random.choice(greetings)
 
def is_sql_query(user_message):
    sql_keywords = ["SELECT", "FROM", "WHERE", "JOIN", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "GROUP BY", "ORDER BY", "HAVING", "UNION", "DISTINCT", "LIMIT", "OFFSET"]
    return any(keyword.lower() in user_message.lower() for keyword in sql_keywords)
 
def extract_sql_query(text):
    if "`" in text:
        clean_query = text.replace("`", "").replace("sql", "")
        return clean_query
    else:
        return text
 
if "messages" not in st.session_state:
    st.session_state.messages = []
 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
st.markdown("<h4 style='font-weight: bold;'>Track Order</h4>", unsafe_allow_html=True)
order_id_input = st.text_input(" Enter Order ID")
if order_id_input.isdigit():
    try:
        order_id = int(order_id_input)
        query = f"SELECT OrderStatus FROM synthetic_orders_data WHERE OrderID = {order_id};"
        order_status = read_sql_query(query, db)
        response=bot_reply(order_status,"what is the order status?")
        st.write(response)
    except ValueError:
        st.error("Please enter a valid Order ID (numeric).")
 
st.markdown("<h4 style='font-weight: bold;'>Product Details</h4>", unsafe_allow_html=True)
product_id_input = st.text_input("Enter Product ID:")
if product_id_input:
    try:
        product_id = int(product_id_input)
        query = f"SELECT * FROM synthetic_product_data WHERE ProductID = {product_id};"
        product_details = read_sql_query(query, db)
        response=bot_reply(product_details,"what is the product details?")
        st.markdown(response)
    except ValueError:
        st.error("Please enter a valid Product ID (numeric).")
 
if user_message := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)
    if is_greeting(user_message):
        response_content = get_random_greeting()
    else:
        question_prompt = f"""
        You are an expert SQL assistant. I have two tables in a database called 'synthetic.db'. Below are the details of the tables:
 
        1. **synthetic_product_data**:
            - **ProductID**: Unique identifier for the product.
            - **ProductName**: Name of the product.
            - **MerchantID**: ID of the merchant selling the product.
            - **ClusterID**: ID of the product cluster.
            - **ClusterLabel**: Label or name for the product cluster.
            - **CategoryID**: ID of the product category.
            - **Category**: Name of the product category.
            - **Price**: Price of the product.
            - **StockQuantity**: Quantity of the product in stock.
            - **Description**: Description of the product.
            - **Rating**: Customer rating of the product.
 
        2. **synthetic_orders_data**:
            - **OrderID**: Unique identifier for the order.
            - **ProductName**: Name of the product ordered.
            - **Category**: Category of the product.
            - **CategoryID**: ID of the product category.
            - **CustomerID**: ID of the customer placing the order.
            - **OrderStatus**: Current status of the order (e.g., "shipped", "pending").
            - **ReturnEligible**: Boolean field indicating if the product is eligible for return.
            - **ShippingDate**: Date the product was shipped.
            - **ProductID**: Foreign key referencing the **ProductID** from the **synthetic_product_data** table.
 
        ---
 
        Please generate an **SQL query in plain text format only without any code block interpretation and delimiters even if the code has multiple lines**, based on the following question. **Do not add any additional explanation or surrounding text**.
 
        Question: {user_message}
        """
        response = get_gemini_response(question_prompt)
        sql_response = extract_sql_query(response).strip().replace("\n", " ")
        query_result = read_sql_query(sql_response, db)
        logging.debug(f"The Query result is: {query_result}")
       
        response_content = bot_reply(query_result,user_message)#get_gemini_response(reply_prompt)
 
    with st.chat_message("assistant"):
        reply = response_content
        st.markdown(reply)
 
    st.session_state.messages.append({"role": "assistant", "content": reply})
 
# Footer
st.markdown("---")
st.markdown("© 2024 Valuemomentum | Designed with Streamlit")
