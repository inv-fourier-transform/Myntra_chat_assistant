from semantic_router import Route, SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder


faq = Route(
        name="faq",
        utterances=[
        "What is the return policy of the products?",
        "How do I cancel the order, I have placed?",
        "How do I initiate a return request?",
        "How can I redeem accumulated Myntra points?",
        "What is meant by Platform fee?",
        "How can I track my order and check current status?",
        "Do you ship your products outside India?",
        "Is there an option for faster delivery",
        "What is your cancellation policy?",
        "Can shipping address be modified after order placement?",
        "Tell me about your return and exchange policy.",
        "How long will it take to receive refund for returned product?",
        "How do I return multiple products from a single order?",
        "Does you pick up the product I want to return from my location?",
        "Why did the pick up of my product fail?",
        "How can I pay for my order?",
        "Does you accept Rs. 2,000 notes for COD payments?",
        "What is the COD limit for an order?",
        "Do you have any extra fee for COD orders?",
        "Tell me more about the EMI payment option using my credit card.",
        "How can I add money to Myntra Credit?",
        "How much money can be added to Myntra Credit?",
        "What's the validity for Myntra Credit?",
        "How can I apply a coupon to my order?",
        "How do I purchase a Gift Card?",
        "How do I check my available Gift Card balance and expiration date?",
        "Do you provide open box delivery?",
        "Do you have a Referral program?",
        "Is there a limit to the amount of referral rewards that I can earn?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "Do you accept cash?",
        "Can I pay for my order using cash at the time of delivery?"
      ]
)

sql = Route(
    name="sql",
    utterances=[
        "I want to buy Nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have Asics running shoes in the price range of Rs.4000-Rs.6000?",
        "Are there any Puma shoes on sale?",
        "What is the price of the most expensive shoes that you have on sale?",


    ]
)

small_talk = Route(
    name="small_talk",
    utterances=[
        "How are you?",
        "What is your name?",
        "Are you a robot?",
        "What are you?",
        "What do you do?",
        "Who created you?",
        "Where are you from?",
        "Can you help me?",
        "How’s your day going?",
        "Do you sleep?",
        "Were you able to sleep well yesterday?",
        "Do you have feelings?",
        "What’s your favorite color?",
        "Tell me a joke.",
        "What can you do?",
        "Can you talk?",
        "How old are you?",
        "Do you like humans?",
        "Are you real?",
        "Do you have friends?",
        "What’s your purpose?",
        "Who made you?",
        "Do you like your job?",
        "What’s up?",
        "Good morning!",
        "Good evening!",
        "How’s it going?",
        "How’s life?",
        "Nice to meet you!",
        "Can you tell me something interesting?",
        "Do you ever get tired?",
        "What are you doing right now?",
        "Can you sing?",
        "Can you dance?",
        "Are you smart?",
        "Do you like me?",
        "Tell me something fun.",
        "Do you eat food?",
        "Are you human?",
        "Who is your favorite person?",
        "Can we be friends?",
        "Do you know Siri?",
        "Do you know Alexa?",
        "How’s the weather there?",
        "What’s new?",
        "I’m bored.",
        "Talk to me.",
        "Say something funny.",
        "Tell me a fun fact.",
        "Do you dream?",
        "Do you like music?",
        "Can you play games?",
    ]
)


encoder = HuggingFaceEncoder(model="sentence-transformers/all-mpnet-base-v2")

router = SemanticRouter(routes=[faq, sql, small_talk], encoder=encoder, auto_sync="local")

if __name__ == "__main__":
    print(router("Do you accept ICICI credit card EMI as a payment option?").name)
    print(router("Show me a pair of Nike running shoes").name)
    print(router("What's the weather like today?").name)
    print(router("Did you sleep well yesterday?").name)


