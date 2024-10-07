import os
import ollama
import logging
from openai import OpenAI
import google.generativeai as genai
from abc import ABC, abstractmethod
from config import SYSTEM_PROMPT, USER_PROMPT

class LLMQueryGenerator(ABC):

    @abstractmethod
    def generate_sql_from_nl(self, db_schema, nl_query):
        raise NotImplementedError


class OpenAIQueryGenerator(LLMQueryGenerator):

    def __init__(self, model: str = "gpt-4o", sys_prompt: str = SYSTEM_PROMPT, user_prompt: str = USER_PROMPT):
        self.model = model
        self.sys_prompt = sys_prompt
        self.user_prompt = user_prompt

    def generate_sql_from_nl(self, db_schema, nl_query):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.sys_prompt
                    },
                    {
                        "role": "user",
                        "content": self.user_prompt.format(db_schema, nl_query),
                    },
                ],
            )
            response = completion.choices[0].message.content.strip()
            return response
        except Exception as e:
            logging.error("Failed to send request to OpenAI: %s", e)
            raise Exception(f"Failed to send request to OpenAI: {e}")


class OllamaQueryGenerator(LLMQueryGenerator):

    def __init__(self, model: str = "llama3.2:latest", sys_prompt: str = SYSTEM_PROMPT, user_prompt: str = USER_PROMPT):
        self.model = model
        self.sys_prompt = sys_prompt
        self.user_prompt = user_prompt

    def generate_sql_from_nl(self, db_schema, nl_query):
        from ollama import Client
        client = Client(host="http://localhost:11434")
        try:      
            response = client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.sys_prompt
                    },
                    {
                        "role": "user",
                        "content": self.user_prompt.format(db_schema, nl_query),
                    },
                ],
            )   
            return response['message']['content']
        except ollama.ResponseError as e:
            logging.error(f"Error: {e} CODE: {e.status_code}")
            if e.status_code == 404:
                ollama.pull(self.model)
        

class GeminiQueryGenerator(LLMQueryGenerator):

    def __init__(self, model: str = 'gemini-1.5-pro-002', sys_prompt: str = SYSTEM_PROMPT, user_prompt: str = USER_PROMPT):
        self.model = model
        self.sys_prompt = sys_prompt,
        self.user_prompt = user_prompt

    def generate_sql_from_nl(self, db_schema, nl_query):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                  "temperature": 1,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
            },
            system_instruction=self.sys_prompt,
        )
        chat_session = model.start_chat(history=[])

        response = chat_session.send_message(self.user_prompt.format(db_schema, nl_query))
        return response.text
        