# Brave is all Mistral need for Automatic Blog Generation






## Motivation
One of the best ways to learn something is reading a good blog.
In this application, we use Mistral and Brave to build a automatic tool, to generate a blog with texts and images for any interested topic from the user. 

## Architecture

<img width="788" alt="image" src="https://github.com/tyu008/mistral_hackthon_blog_generator/assets/3173580/0874b6cd-e265-4653-bcfd-be2885c3a485">


## Highlight

### Hierachical Retrieval Augmented Generation

Vanilla RAG is far from enough to generate a high-qaulity blog covering much details of the topics.
So we build a Hierachical Retrieval Augmented Generation (HRAG) architeture.
In the first layer, we use vanilla RAG to generate an outline with several headlines.
In the second layer, we use each headline to conduct another round RAG to complete each section.
At last, we merge all the sections into a holistic Blog.

Our HRAG is related with the sub-query engine in Llama-Index.
But different sub-query engine solely relying on LLM to decompose the query, we use RAG (LLM + Search Engine) to decompose the query.
Benefit from the poweful knoweledge of search engine, our decomposition is more meaningful.

### Parallel Async LLM call

## Generated Blogs

<img width="969" alt="Screenshot 2024-03-24 at 11 50 56 AM" src="https://github.com/tyu008/mistral_hackthon_blog_generator/assets/3173580/a61e6baf-fc8f-4010-a6d5-955c563df657">



<img width="1725" alt="Screenshot 2024-03-24 at 11 03 25 AM" src="https://github.com/tyu008/mistral_hackthon_blog_generator/assets/3173580/bff5350d-c89c-42a7-9ce0-8ab453e009a5">




<img width="1228" alt="Screenshot 2024-03-24 at 11 05 19 AM" src="https://github.com/tyu008/mistral_hackthon_blog_generator/assets/3173580/2d8219bf-44ce-45ae-a0a4-451eda273909">



<img width="966" alt="Screenshot 2024-03-24 at 11 25 50 AM" src="https://github.com/tyu008/mistral_hackthon_blog_generator/assets/3173580/36d8eeae-a8b5-451d-8f19-a4c89bad07dd">

