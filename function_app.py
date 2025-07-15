import logging
import azure.functions as func
import pandas as pd
import datetime
from datetime import timezone
import pytz
import requests
import json
import os

# Azure Functions 앱을 생성합니다.
app = func.FunctionApp()

# (UTC 시간대 기준) 매일 자정에 실행되는 타이머 트리거를 설정합니다.
@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer", run_on_startup=False, use_monitor=False)
# Event Hub에 데이터를 보내는 출력을 설정합니다.
@app.event_hub_output(arg_name="event", event_hub_name= os.environ["SolarEventHubName"], connection="SolarEventHubConnectionString")
def solar_predict_eventhubs_scheduler(timer: func.TimerRequest, event: func.Out[str]) -> None:
    # 로그를 통해 스케줄러 시작 알림을 기록합니다.
    logging.info('태양광 예측 데이터 수집 스케줄러가 시작되었습니다.')

    #  CSV 파일에서 태양광 데이터 읽어오기
    df = pd.read_csv("./data/solar_city.csv", encoding="euc-kr")

    #  현재 UTC 시간 가져오기
    utc_timestamp = datetime.datetime.now(tz=timezone.utc)
    #  KST (한국 표준시)로 변환합니다.
    kst = pytz.timezone('Asia/Seoul')
    kst_timestamp = utc_timestamp.astimezone(kst)
    # 현재 날짜를 "YYYYMMDD" 형식으로 변환합니다.
    base_date = kst_timestamp.strftime("%Y%m%d")

    # 기상 데이터 API URL 설정
    url = "https://bd.kma.go.kr/kma2020/energy/energyGeneration.do"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded", # 요청하는 데이터 형식 설정
    }
    # 수집할 태양광 데이터를 저장할 리스트입니다.
    solar_data_list = []
    # 데이터 수집에서 제외된 행의 인덱스를 저장할 리스트입니다.
    skiped_index = []

    # CSV 파일의 각 행을 반복합니다.
    for index, row in df.iterrows():
        # 중요한 데이터가 없는 경우, 해당 행을 생략합니다.
        if pd.isna(row["격자X"]) or pd.isna(row["격자Y"]) or pd.isna(row["행정구역코드"]) or row["발전설비유무"] == "무":
            # 생략된 인덱스를 리스트에 추가합니다.
            skiped_index.append(index)
            continue
            
        try:
            # 필요한 데이터 추출
            reg_cd = row["행정구역코드"]
            city = row["도"]
            county = row["시"]
            lat = row["위도(초/100)"]
            lon = row["경도(초/100)"]

            # API 요청에 사용할 데이터 설정
            payload = f"baseDate={base_date}&fcstDate={base_date}&fcstTime=0000&regCd={reg_cd}"

            # API에 POST 요청을 보내고 응답을 받습니다.
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status() # 요청이 성공하지 않으면 오류를 발생시킵니다.

            data = response.json() # JSON 형식으로 데이터를 변환합니다.

            items = data['result'] # 필요한 데이터 항목을 추출합니다.

            # 받은 데이터에서 필요한 정보만 추출하여 리스트에 추가합니다.
            for item in items:
                solar_data = {
                    "city": city,
                    "county": county,
                    "fcstDate": item["fcstDate"],
                    "fcstTime": item["fcstTime"],
                    "pcap": item["pcap"],
                    "qgen": item["qgen"],
                    "regCd": item["regCd"],
                    "srad": item["srad"],
                    "temp": item["temp"],
                    "wspd": item["wspd"],
                    "lat": lat,
                    "lon": lon
                }
                solar_data_list.append(solar_data) # 수집된 태양광 예측 데이터를 추가합니다.

        except (ValueError, TypeError) as e:
            # 데이터 변환 중 오류가 발생하면 로그를 기록합니다.
            logging.error(f"Failed to convert 격자X or 격자Y to integer in row {index}: {e}")

    # 태양광 데이터 수집이 완료되었음을 기록합니다.
    logging.info(f"태양광 예측 데이터 수집이 완료되었습니다. 수집된 데이터: {len(solar_data_list)}개")   
    # 수집된 데이터를 Event Hub에 전송합니다.
    event.set(solar_data_list)
    logging.info(f"EventHub로 {len(solar_data_list)}개 데이터 전송 완료.")

    # 환경 변수에서 웹훅 URL을 확인합니다.
    if os.environ.get("AzureWebHookUrl") is not None:
        logging.info("환경 변수에 웹훅 URL이 설정되어있습니다. 웹훅을 요청합니다.")
        # 웹훅 URL을 불러옵니다.
        webhook_url = os.environ["AzureWebHookUrl"]
        # Teams Incoming Webhook 참고 자료: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using?tabs=cURL%2Ctext1
        # 웹훅에 보낼 데이터 형식 설정
        webhook_payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "태양광 예측 데이터 수집 스케줄러가 실행되었습니다."
                            }
                        ]
                    }
                }
            ]
        }
        # 웹훅에 POST 요청을 보내고 응답을 확인합니다.
        response = requests.post(webhook_url, json=webhook_payload)
        logging.info(f"웹훅 실행 결과: {response.status_code}")
        response.raise_for_status() # 요청 실패 시 오류를 발생시킵니다.
    else:
        logging.info("웹훅 URL이 설정되어 있지 않습니다. 웹 훅 요청을 생략합니다.")

    # 데이터 수집에서 제외된 행의 인덱스를 로그로 기록합니다.
    logging.info(f"{skiped_index}번 행은 데이터 수집에서 제외되었습니다.")
    # 종료 알림을 기록합니다.
    logging.info('태양광 예측 데이터 수집 스케줄러가 종료되었습니다.')