# set GROQ_API_KEY in the secrets

import os

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables in a file called .env
# Print the key prefixes to help with any debugging

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    print(f"OpenAI API Key exists and begins:{openai_api_key[:10]}")
else:
    print("OpenAI API Key not set")

client = OpenAI()
MODEL = "gpt-4o-mini"


class Agent:
    def __init__(self, client: client, system: str = "") -> None:
        self.client = client
        self.system = system
        self.messages: list = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
            result = self.execute()
            self.messages.append({"role": "assistant", "content": result})
            return result
        else:
            print("NO MESSAGE")

    def execute(self):
        completion = client.chat.completions.create(model=MODEL, messages=self.messages)
        return completion.choices[0].message.content


system_prompt = """
You run in a loop of THOUGHT, ACTION, OBSERVATION.
When you have a THOUGHT you return the THOUGHT and ACTION
At the end of the loop you output an ANSWER
Use THOUGHT to describe your THOUGHTS about the question you have been asked.
Use ACTION to run one of the ACTIONS available to you - then return PAUSE.
OBSERVATION will be the result of running those ACTIONS.

Your available ACTIONS are:

# calculate_total:

if amount = 200
then calculate_total(amount)

This returns amount * 1.2

Runs the calculate_total function and returns a JSON FORMAT output as follows:
{"result": 240, "fn": "calculate_total", "next": "PAUSE"}

# get_product_price:

This uses the get_product_price function and passes in the value of the product
e.g. get_product_price('bike')

This uses the get_product_price with a product = 'bike', finds the price of the bike and then returns a JSON FORMAT output as follows:
{"result": 200, "fn": "get_product_price", "next": "PAUSE"}

Example session:

Question: What is total cost of a bike including VAT?
THOUGHT: I need to find the cost of a bike|ACTION|get_product_price|bike

You will be called again with this:

OBSERVATION|200

THOUGHT: I need to calculate the total including the VAT|ACTION|calculate_total|200

You will be called again with this: 

OBSERVATION|240

If you have the ANSWER, output it as the ANSWER.

ANSWER|The price of the bike including VAT is 240

Now it's your turn:
""".strip()


def calculate_total(amount):
    amount = int(amount)
    return int(amount * 1.2)


def get_product_price(product):
    if product == "bike":
        return 100
    if product == "tv":
        return 200
    if product == "laptop":
        return 300

    return None


# We now loop over the query until an answer is found or the'max_iterations' is reached

answers = []


def loop(max_iterations=10, query: str = ""):
    agent = Agent(client=client, system=system_prompt)
    tools = ["calculate_total", "get_product_price"]
    next_prompt = query
    i = 0
    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        if "ACTION" in result:

            next = result.split("|")
            print(next)
            next_function = next[2].strip()
            next_arg = str(next[3]).strip()

            if next_function in tools:
                result_tool = eval(f"{next_function}('{next_arg}')")
                next_prompt = f"OBSERVATION: {result_tool}"
                print(next_prompt)
            else:
                next_prompt = "OBSERVATION: Tool not found"
            continue

        if "ANSWER" in result:
            # the result at top has final result
            print(f"Answer found:\n\t{result}")
            answers.append(result)
            break


loop(query="What is cost of a bike including VAT?")
loop(query="What is cost of a tv including VAT?")
loop(query="What is cost of a laptop including VAT?")


print("\n=========== SUMMARY ANSWERS ===========")

for answer in answers:
    print(answer)
