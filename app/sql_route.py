import sqlite3
import pandas as pd
from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()

DB_PATH = r"C:\Users\Inspire\Code\Gen AI\Myntra_chat_assistant\app\resources\myntra_db.sqlite"

# Initialize Groq client with API key from environment variables
if not os.getenv('GROQ_API_KEY'):
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
sql_client = Groq(api_key=os.getenv('GROQ_API_KEY'))


def run_query(query):
    """
    Execute a SQL SELECT query against the database and return results as a DataFrame.

    Args:
        query (str): SQL query string to execute

    Returns:
        pd.DataFrame: Query results as a pandas DataFrame

    Raises:
        ValueError: If query is not a SELECT statement
        sqlite3.Error: If database connection or query execution fails
    """
    # Remove leading/trailing whitespace and convert to uppercase for comparison
    normalized_query = query.strip().upper()

    # Validate that the query is a SELECT statement (read-only)
    if not normalized_query.startswith("SELECT"):
        raise ValueError(
            f"Only SELECT queries are allowed. Query must start with 'SELECT', "
            f"but received: '{query[:50]}...'"
        )

    # Execute the query and return results
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Execute query and load results into DataFrame
            df = pd.read_sql_query(query, conn)
            return df
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Database query failed: {str(e)}")


sql_prompt = """
You are an expert SQL query generator. Generate a syntactically correct SQL query that answers the user's question based on the provided schema.

### DATABASE SCHEMA:
Table: product

Columns:
- product_link (string): Product URL
- title (string): Product name
- brand (string): Brand name
- gender (string): 'men' or 'women'
- mrp (integer): Original price in INR
- discount_percent (float): Discount as decimal (0.1 = 10%)
- price_after_discount (integer): Final price in INR
- star_rating (float): Average rating 0-5 (nullable)
- num_ratings (integer): Total rating count (nullable)
- scraped_on (datetime): Data collection timestamp

### QUERY REQUIREMENTS:
1. Generate exactly ONE SQL query
2. Always use `SELECT *` to return all columns
3. For brand filtering, use case-insensitive matching:
   - Use: `WHERE LOWER(brand) LIKE LOWER('%brand_name%')`
   - Never use: `ILIKE` or exact matching
4. Return ONLY the SQL query with no explanations

### OUTPUT FORMAT:
<SQL>
[Your SQL query here]
</SQL>

### EXAMPLE:
Question: "Show all Nike products for women"
<SQL>
SELECT * FROM product WHERE LOWER(brand) LIKE LOWER('%nike%') AND gender = 'women'
</SQL>
"""

comprehension_prompt = """
You are a language comprehension assistant. Generate natural, clear answers to questions using ONLY the provided Data.

### YOUR TASK:
Given a Question and Data, produce a natural-sounding answer using only the information provided.

**Inputs:**
- Question: A natural language question
- Data: The answer information (may be a value, dictionary, array, or dataframe)

**Output:**
A clear, natural response without technical jargon or phrases like "Based on the data" or "According to the dataset".

---

### RESPONSE RULES:

**General Guidelines:**
1. Write in plain, natural English
2. Never mention "Data", "dataframe", "array", or "dictionary"
3. Use only the provided Data — no external calculations or reasoning
4. Be concise and factual

**For Single Values:**
Example:
- Question: What is the average rating?
- Data: 4.3
- ✅ Response: "The average rating is 4.3."

**For Product Lists:**
Use this EXACT format for each product:

<Brand> <Product Title> (<Gender>): Rs. <price_after_discount> (<discount_percent> percent off), Rating: <rating>, <product_link>, <datetime>

Requirements:
- Each product on a new line
- Use "NA" for missing fields
- Convert discount decimals to percentages (0.35 → 35 percent off)
- Always include "Rs." for prices

---

### EXAMPLES:

**Example 1: Single Value**
Question: What is the average rating of Nike Perforated Fly By 3 Mid-Top Basketball Shoes?  
Data: 4.8  
✅ Response: The average rating is 4.8.

**Example 2: Product List (Men)**
Question: List 3 pairs of men's shoes.  
Data:
| brand | title | gender | price_after_discount | discount_percent | rating | link | datetime |
| Campus | Men's Running Shoes | Men | 1104 | 0.35 | 4.4 | link1 | datetime1 |
| Nike | Perforated Fly By 3 | Men | 3996 | 0.2 | 4.8 | link2 | datetime2 |
| On | Mesh Running Shoes | Men | 21499 | 0.0 | NA | link3 | datetime3 |

✅ Response:
1. Campus Men's Running Shoes (Men): Rs. 1104 (35 percent off), Rating: 4.4, link1, datetime1
2. Nike Perforated Fly By 3 (Men): Rs. 3996 (20 percent off), Rating: 4.8, link2, datetime2
3. On Mesh Running Shoes (Men): Rs. 21499 (0 percent off), Rating: NA, link3, datetime3

**Example 3: Product List (Women)**
Question: Pick 3 pairs of women's shoes.  
Data:
| brand | title | gender | price_after_discount | discount_percent | rating | link | datetime |
| Puma | MagMax Nitro Running Shoes | Women | 2104 | 0.35 | 4.2 | link1 | datetime1 |
| Asics | Gel Nimbus-27 Shoes | Women | 4996 | 0.15 | 4.7 | link2 | datetime2 |
| Nike | Pegasus Turbo | Women | 10499 | 0.0 | NA | link3 | datetime3 |

✅ Response:
1. Puma MagMax Nitro Running Shoes (Women): Rs. 2104 (35 percent off), Rating: 4.2, link1, datetime1
2. Asics Gel Nimbus-27 Shoes (Women): Rs. 4996 (15 percent off), Rating: 4.7, link2, datetime2
3. Nike Pegasus Turbo (Women): Rs. 10499 (0 percent off), Rating: NA, link3, datetime3

---

### OUTPUT:
Return ONLY the final answer as plain text or numbered list. No headings, explanations, or tags.
"""


def generate_sql_query(question):

    chat_completion = sql_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=os.environ["GROQ_MODEL"],
        temperature=0.2,
        #max_tokens=1024

    )

    return chat_completion.choices[0].message.content

def data_comprehension(question, context):
    chat_completion = sql_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": f"QUESTION: {question}. DATA: {context}",
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,
        # max_tokens=1024
    )

    return chat_completion.choices[0].message.content


def sql_chain(question):
    """
    Process a natural language question through the SQL generation and execution pipeline.

    This function:
    1. Generates a SQL query from the question using an LLM
    2. Extracts the query from XML tags
    3. Executes the query against the database
    4. Converts results to natural language using comprehension model

    Args:
        question (str): Natural language question about the database

    Returns:
        str: Natural language answer to the question, or error message if processing fails
    """
    # Step 1: Generate SQL query from natural language question
    sql_query_response = generate_sql_query(question)

    # Step 2: Extract SQL query from <SQL>...</SQL> tags
    sql_tag_pattern = r"<SQL>(.*?)</SQL>"
    extracted_queries = re.findall(
        pattern=sql_tag_pattern,
        string=sql_query_response,
        flags=re.DOTALL  # Allow matching across multiple lines
    )

    # Step 3: Validate that a SQL query was extracted
    if len(extracted_queries) == 0:
        error_message = "Sorry, the LLM is unable to generate the SQL query for the question"
        return error_message

    # Extract the first (and should be only) SQL query and clean whitespace
    sql_query = extracted_queries[0].strip()
    print(f"Generated SQL query is: {sql_query}")

    # Step 4: Execute the SQL query against the database
    query_results = run_query(sql_query)

    # Step 5: Validate that query execution was successful
    if query_results is None:
        error_message = "Sorry, there was a problem executing the SQL query."
        return error_message

    # Step 6: Convert DataFrame results to dictionary format for comprehension model
    results_as_context = query_results.to_dict(orient='records')

    # Step 7: Generate natural language answer from query results
    natural_language_answer = data_comprehension(question, results_as_context)

    return natural_language_answer


if __name__ == "__main__":
    question = "Show me any 3 Nike women's shoes with rating greater 4 and discount of at least 10% and price under 6000"


    print(sql_chain(question))
