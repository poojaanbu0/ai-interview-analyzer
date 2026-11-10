import os,json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

print("API key loaded:", bool(api_key))

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
    timeout=90.0,
    max_retries=1,
    
)

try:
    print("\nSending request to NVIDIA...")

    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        messages=[
            {
                "role": "user",
                "content": '''{"q": "Tell me about yourself.","a":"I am Pujai. I have done my Gitaim machine learning from Savita Anjana College, graduated in the year of 2026. I have expertise in machine learning, deep learning and gendered Bayer. I have worked as an intern in all the main vortex solutions for five months, as an software engineering intern, wherever I have been, I have raised the assistant, which reiterates answers based on research papers, that are stored in light by engineering squareings."}
                                The given object, i need to get the progress indication upto 100%, which includes strength,filling words,emotions, accuracy. i need the output in a object eg; {"strength":20,"fillingWords":30,"emotions":87,"accuracy":45} and one more suggestions for the counter question''' }
        ],
        max_tokens=50,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
    )

    print("\nAPI REQUEST SUCCESSFUL")
    # print("Response object:", response)
    content =  response.choices[0].message.content
    # print("Model output:",content)
    print("==================================Ai Response=======================================")
    print(content)
    final = content.split("```json")[1].split("```")[0].strip()
    print("=====================================")
    print(final)
    print("=====================================")
    output = json.loads(final)
    print("Token usage:", response.usage)
    print(output)

except Exception as error:
    print("\nAPI REQUEST FAILED")
    print("Exception type:", type(error).__name__)
    print("Exception:", repr(error))
    print("Underlying cause:", repr(error.__cause__))