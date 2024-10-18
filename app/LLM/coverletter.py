import requests
import os
import json
import time

from dotenv import load_dotenv
from pathlib import Path
import time

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
import pandas as pd

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_auth.json"

class Generate_CoverLetter:

    def __init__(self, Job_Description, Skills, Job_Title, path=""):
        self.Job_Description = Job_Description
        self.Skills = Skills
        self.Job_Title = Job_Title
        self.path = path
        self.model = VertexAI(model_name='gemini-pro',temperature=0.1)

    def read_text_file(self,filepath):
        with open(f"{self.path}{filepath}", 'r') as file:
            return file.read()
        
    def Validator(self,response):
        # prompt = self.build_prompt('prompts/Output_validation.txt')
        # chain = prompt | self.model
        # response = chain.invoke({"input":input})
        data = ""
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print("JSON Decode Error , Trying to correct the JSON")
            try:
                corrected_result = response[response.find('['):response.rfind(']') + 1]
                data = json.loads(corrected_result)
                print("Corrected Parsed JSON successfully")
            except json.JSONDecodeError as e:
                print("Failed to parse corrected JSON")
        return data

    def build_prompt(self,filepath):
        template = self.read_text_file(filepath)
        prompt = PromptTemplate.from_template(template)
        return prompt

    def Generate_CoverLetter(self) -> str:
        prompt = self.build_prompt('/prompts/coverletter.txt')

        chain = prompt | self.model

        response  =chain.invoke(
                        {
                            'Job_Description' : self.Job_Description,
                            'Job_Title' : self.Job_Title,
                            "Skills" : self.Skills
                        })
        
        return self.Validator(response)
    
    def Generate_Quiz(self) -> str:
        pass

    def Learning_Guide(self) -> str:  # Use a list of missing sklls and generate materials to help the user learn those missing skills
        pass

    def Resume_Checker(self) -> str: # Recommend skills to be added in the resume given the job description
        pass

    # Add new features such as ---> 
    





