# node에서 프롬프트 파람 Post 받음
# ollama에 만족도 프롬프트 전달
# ollama에서 조회 결과 받아서 param set
# node 서버에 전달

import ollama
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL","gemma3:4b")

# class param(BaseModel):
#     text: str
class TripSatisfaction:
    def __init__(self,arguments):
        self.arguments = arguments

    async def run_Satisfaction(self):

        print("param",self.arguments)

        prompt = f"""
         당신의 임무는 아래 문장을 읽고 규칙을 활용하여 만족도를 판단하는 것입니다.
    
        === 규칙 ===
         1. 판단항목 : 음식, 교통, 친절, 날씨, 청결, 분위기, 숙소, 시설, 안내
         2. 판단규칙 : 판단항목에 대한 만족도가 높으면 H, 낮으면 L, 없으면 X
         3. 출력형식 : json 형태로 모든 판단항목이 나오게 해줘
    
         === 출력형식 ===
         {{
           "items": [
             {{
               "label": 판단항목,
               "value": 만족도,
             }},
             {{
               "label": 판단항목,
               "value": 만족도,
             }},
             ...
           ]
         }}
    
        문장 : {self.arguments}
        
         """

        print("prompt\n", prompt)

        response = await ollama.AsyncClient().generate(model=MODEL, prompt=prompt, keep_alive=-1)

        raw_text = response.get('response',"").strip()

        print("\nraw_text\n", raw_text)

        match = re.search(r"\{.*\}", raw_text, re.DOTALL)

        if not raw_text:
            print("none")
            return { "error" : "비었음","raw":response }

        try:
            if match:
                satisfaction_list = json.loads(match.group())
                print("\nmatch\n", satisfaction_list)
                print("-----------------------------------")
            else:
                print("json 못찾음",raw_text)
            return satisfaction_list
        except json.JSONDecodeError as e:
            print("json parsing error", e)
            return { "result" : str(e) }
