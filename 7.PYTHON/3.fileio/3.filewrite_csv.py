import csv

# 약간 옛날 방식.. 리스트로 데이터 관리하는 방식
data = [
    ["Name", "Age", "City"], # 헤딩 = 첫번째줄
    ["John", 25, "Seoul"],
    ["James", 23, "Busan"],
    ["Bob", 24, "Seoul"]
]

filename = "data.csv"

with open(filename, "w", newline="") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerows(data)

# 좀더 모던 방식.. Dict로 데이터 관리하는 방식
data2 = [
    {"Name":"John", "Age":25, "City":"Seoul"},
    {"Name":"James", "Age":23, "City":"Busan"},
    {"Name":"Bob", "Age":24, "City":"Seoul"}
]

with open(filename, "w", newline="") as file:
    # headers = ["Name", "Age", "City"]
    headers = data2[0].keys()
    csv_writer = csv.DictWriter(file, fieldnames=headers)
    csv_writer.writeheader() # 첫줄에 헤더 쓰기
    csv_writer.writerows(data2) # dict를 csv로 파싱해서 저장하기
