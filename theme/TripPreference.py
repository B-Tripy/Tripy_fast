# node로 부터 사진 category 분류 전달 받음
# tripy_prefer_model.pkl 모델에 param 전달
# 결과값 받아서 다시 node에 전달

import pandas as pd
import pickle

class TripPreference:
    def __init__(self,arguments:list):
        self.arguments = arguments

    def run_preference(self):
        print("run_preference param",self.arguments);
        # pkl 파일 선언
        with open('./theme/tripy_prefer_model.pkl', 'rb') as f:
            model = pickle.load(f)

        items = self.arguments

        print('items=========',items)
        # 원하는 results 형태로 변환

        data = []
        data = convert_to_matrix(items)

        # print('data',data)

        # data 가 넘어왔다고 치고
        # data = [['a',0,0,1,0,0,0,1,0],['b',0,1,1,0,1,0,0,0],['c',1,1,1,1,1,1,1,1]]

        # column 선언
        cols = ['sea', 'mountain', 'forest', 'building', 'city', 'person', 'culture', 'food']

        # 1행 과 나머지행 으로 분리
        row1 = [i[0] for i in data]
        row2 = [i[1] for i in data]
        rows = [i[2:] for i in data]

        # 만들어진 ml 에 테우기
        param = pd.DataFrame(data=rows, columns = cols)
        prefer_classification = model.predict(param)

        # 결과가 [1 2 1] 이따구로 나와서 [1,2,1] 형태로 변경
        prefer_classification_list = prefer_classification.tolist()

        # print('row',row);
        # print('rows',rows);
        # print('prefer_classification_list', prefer_classification_list);

        # 던지는 결과를 [[a,1],[b,2],[c,1]] 와 같이 이차원배열고 변경
        result = [[r, p, z] for r, p, z in zip(row1,row2, prefer_classification_list)]

        print("preference result",result)

        return result

def convert_to_matrix(arguments):
    if not arguments:
        return []
    trip_id = arguments[0].TripId
    photo_id = arguments[0].PhotoId
    vals = [p.val for p in arguments]

    return [[trip_id,photo_id]+ vals]