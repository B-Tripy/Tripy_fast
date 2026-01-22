import os
from theme.TripPreference import TripPreference
from theme.TripSatisfaction import TripSatisfaction
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Depends
from typing import Optional
# ml pickle을 이용하여 선호도 획득 znddi

router = APIRouter(
    prefix="/theme",
    tags=["theme"],
)

class PreferenceRequest(BaseModel):
    TripId:Optional[int]=None
    PhotoId: Optional[int] = None
    category:str
    val:Optional[int]=None

@router.post("/preference")
def preference(request:list[PreferenceRequest]):

    try:
        print('request',request)
        tp = TripPreference(request)
        result = tp.run_preference()
        print('preference result',result)
        return {"result" : result}
    except Exception as e:
        return {"error" : str(e)}

# class SatisfyRequest(BaseModel):
#     TripId:Optional[int]=None
#     PhotoId: Optional[int] = None
#     contents:str
# @app.get("/theme/satisfy")
# def satisfy(request:SatisfyRequest):
#     try:
#         print('-----------------------')
#         print('satisfy request/n',request)
#         print('-----------------------')
#
#         ts = TripSatisfaction(request)
#         result = ts.run_Satisfaction()
#         print('satisfy result',result)
#         return {"result" : result}
#     except Exception as e:
#         return {"error" : str(e)}

# ollama 를 이용하여 만족도 획득 znddi
class SatisfactionRequest(BaseModel):
    TripId:Optional[int]=None
    PhotoId: Optional[int] = None
    contents:str
@router.post("/satisfaction")
# def satisfaction(request:SatisfactionRequest):
async def satisfaction():
    param = """
    충청남도 공주시에 있는 갑사에 다녀왔는데,
    공기도 맑고 조용하고, 하늘도 시린듯이 파랗게 빛났어 절로 감탄이 나왔지
    갑사에 오르는 길은 힘들지 않았지.
    계룡산을 넘어오면서 계곡에 있는 많은 음식점이 있었는데 상품은 죄다 중국산이어서 좀 그랬어
    음식은 비쌋고 맛도 머 그럭저럭 좀 관리가 필요한것 같아
    조금 내려오니 시내버스 승강장이 있던데 왜케 지저분한지 담배는 왜 아무데서나 피는지 조금 괴로웠어
    """
    try:
        print('-----------------------')
        print('satisfaction request/n', param)
        print('-----------------------')

        ts = TripSatisfaction(param)
        result = await ts.run_Satisfaction()
        print('satisfaction result',result)
        return {"result" : result}
    except Exception as e:
        return {"error" : str(e)}

@router.get("/ai/theme/connectfastApi")
def connect_fastapi():
    result = "ok good"
    return {"result":result}

