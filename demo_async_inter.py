import streamlit as st
import requests
import json
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from mistralai.async_client import MistralAsyncClient
import nest_asyncio
import sys

nest_asyncio.apply()
#st.set_page_config(layout="wide")

IR_TOKEN = os.environ["IR_TOKEN"]
LLM_TOKEN = os.environ["LLM_TOKEN"]



PROMPT_TEMPLATE="""
[INST] You are a super smart generative AI tool.
Understand a list of content surrounded by ``` and generated a blog about TOPIC in markdown format.
The title starts with '#'.
MUST Generate the blog in an organized format with a list of SIX sections.
The first section MUST BE Introduction.
The last section MUST BE Conclusion.
For the other sections, each section covers a part of TOPIC, and sections are complementary with each other.
Each section starts with '##'.
[\INST]
TOPIC: {topic}

```
{content}
```

[INST]
Return the markdown-format newsletter and nothing else.
[\INST]

"""
SUBPROMPT_TEMPLATE="""
[INST]
You are a super smart generative AI tool for revising a section in a blog of markdown format.
You are given an intial markdown section and you are given a list of additional content surrounded by ```.
Rewrite the origianl section into a new section with more information.
The new section starts with the section title, following by a list of 4 sub-sections.
DO not conlcude anything in the new section.
The generate new sections starts with '##' in an organized markdown format with a list of 4 sub-sections.
For each subsection, it starts with '###'.
[\INST]
INITIAL SECTION: {section}
TOPIC: {topic}

```
{content}
```

[INST]
Return the markdown-format newsletter and nothing else.
[\INST]
"""


def retrieve_image(query):
    headers = {
        'Accept': 'application/json',
        # 'Accept-Encoding': 'gzip',
        'X-Subscription-Token': IR_TOKEN,
    }

    params = {
        'q': query,
        'safesearch': 'strict',
        'count': '5',
        'search_lang': 'en',
        'country': 'us',
        'spellcheck': '1',
    }

    response = requests.get('https://api.search.brave.com/res/v1/images/search', params=params, headers=headers)
    try:
        return response.json().get("results")[0].get("properties").get('url')
    except:
        return None

def retrieval_content(query):

    content = ""
    headers = {
        'Accept': 'application/json',
        # 'Accept-Encoding': 'gzip',
        'X-Subscription-Token': IR_TOKEN,
    }
    params = {
        'q': query,
        'count':20,
    }
    response = requests.get('https://api.search.brave.com/res/v1/web/search', params=params, headers=headers).json()

    keys = ["web"]

    for key in keys:
        results = response.get(key).get("results")
        for res in results:
            if res:
                content += "\n content: " + res.get("description")
            
    return content

def retrieval_content_short(query):

    content = ""
    headers = {
        'Accept': 'application/json',
        # 'Accept-Encoding': 'gzip',
        'X-Subscription-Token': IR_TOKEN,
    }   
    params = { 
        'q': query,
        'count':10
    }
    response = requests.get('https://api.search.brave.com/res/v1/web/search', params=params, headers=headers).json()

    keys = ["web"]
        
    for key in keys:
        results = response.get(key).get("results")
        for res in results:
            if res:
                content += "\n content: " + res.get("description")

    return content



import asyncio


def generate_answer(query):


    api_key = LLM_TOKEN
    model = "mistral-large-latest"

    client = MistralClient(api_key=api_key)

    messages = [
        ChatMessage(role="user", content=query)
    ]

    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
        temperature = 0.5
    )

    return chat_response.choices[0].message.content



async def agenerate_answer2(query):


    api_key = LLM_TOKEN
    model = "mistral-medium-latest"

    #client = MistralClient(api_key=api_key)
    client = MistralAsyncClient(api_key=api_key)

    messages = [
        ChatMessage(role="user", content=query)
    ]

    # No streaming
    chat_response = client.chat_stream(
        model=model,
        messages=messages,
        temperature = 0.5
    )

    content = ""
    async for chunk in chat_response: 
        content+=chunk.choices[0].delta.content

    return content#chat_response.choices[0].message.content




async def agenerate_answer(query):


    api_key = LLM_TOKEN
    model = "open-mixtral-8x7b" #"mistral-medium-latest"

    client = MistralClient(api_key=api_key)
    #client = MistralAsyncClient(api_key=api_key)

    messages = [
        ChatMessage(role="user", content=query)
    ]

    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
         temperature = 0.0
    )

    return chat_response.choices[0].message.content

async def get_subanswers(sub_titles,sub_irs,sub_orgs):
    pre_list = []
    final_list = []

    for i in range(0, len(sub_titles)):
        print("finish " + str(i))    
        args = {"topic":sub_titles[i], "content": sub_irs[i], "section": sub_orgs[i]}
        prompt = SUBPROMPT_TEMPLATE.format(**args)
        pre_list.append(agenerate_answer2(prompt))

    await_list = asyncio.gather(*pre_list)

    for result in await await_list:
        final_list.append(result)


    return final_list



async def main():

    sub_answers = []
    topic = sys.argv[1]#"Mango DB"
    print(topic)
    content = retrieval_content(topic)
    img_urls = [retrieve_image(topic)]

    args = {"topic":topic, "content":content}

    prompt = PROMPT_TEMPLATE.format(**args)

    ans = generate_answer(prompt)
    print(ans)

    subsecs = ans.split("##") 
    sub_answers.append(subsecs[0])
    sub_answers.append("## " + subsecs[1])


    sub_titles = []
    sub_irs = []
    sub_orgs = []

    for i in range(2, len(subsecs)-1):
        print("finish " + str(i))
        section_title = subsecs[i].split("\n")[0]
        sub_titles.append(section_title)
        content = retrieval_content_short(section_title)
        sub_irs.append(content)
        sub_orgs.append("## "+ subsecs[i])
        img = retrieve_image(topic + " " + section_title)
        if img:
            img_urls.append(img)

    sub_answers.extend(await get_subanswers(sub_titles,sub_irs,sub_orgs))

    sub_answers.append("## " + subsecs[len(subsecs)-1])

    json.dump(sub_answers,open("/Users/tayu/sub_ans.json","w"))

    for idx,item in enumerate(sub_answers):
        if idx > 1 and idx < len(sub_answers) - 1 and idx < len(img_urls)+1:
            st.image(image=img_urls[idx-1] ,width=600)
        st.markdown(item)


asyncio.run(main())



