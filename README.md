# (Azure_function) Solar Power Generation Prediction 
- Real-time Data Pipeline

This project demonstrates a practical real-time data pipeline using Azure Functions, Event Hubs, and Teams Webhook integration.  
It collects solar power generation prediction data from an external API, transforms the data, and ingests it into Azure Event Hub for further real-time analysis.

## Features

- Collects real-time solar generation prediction data via external API
- Preprocesses and formats data using Azure Functions (serverless)
- Sends structured data to Azure Event Hubs
- Sends notification to Microsoft Teams via Webhook upon function execution

## Technologies

- Azure Functions (Python)
- Azure Event Hubs
- Microsoft Teams Webhook
- Visual Studio Code
- Azurite (Local Storage Emulator)

## How to Use

1. Clone the repository:

git clone https://github.com/mi-createcode/Azure_function.git

2. Create and configure `local.settings.json` with:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SolarEventHubName": "<Your Event Hub Name>",
    "SolarEventHubConnectionString": "<Your Event Hub Connection String>",
    "AzureWebHookUrl": "<Your Teams Webhook URL>"
  }
}
```

3. Run locally:
func start

4. Deploy to Azure and test using:

- Azure Portal Logs

- Teams Message Notification

- Event Hub Data Explorer




# 태양광 발전 예측 수집 - 실시간 데이터 파이프라인
이 프로젝트는 Azure Functions, Event Hubs, Teams Webhook을 활용한 실시간 데이터 수집 파이프라인 구축 실습입니다.
외부 API로부터 태양광 발전량 예측 데이터를 수집하고, 이를 정제 및 가공하여 Azure Event Hub로 전송합니다.

## 주요 기능
외부 API를 통한 실시간 태양광 발전 예측 데이터 수집

Azure Functions를 통한 데이터 전처리 및 포맷팅

구조화된 데이터를 Event Hub로 전송

Teams Webhook을 통해 실행 알림 전송

## 사용 기술
- Azure Functions (Python)

- Azure Event Hubs

- Microsoft Teams Webhook

- Visual Studio Code

- Azurite (로컬 Azure Storage 에뮬레이터)

## 사용 방법
1. 레포지토리 클론:
git clone https://github.com/mi-createcode/Azure_function.git

2. local.settings.json 구성:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SolarEventHubName": "<이벤트 허브 이름>",
    "SolarEventHubConnectionString": "<이벤트 허브 연결 문자열>",
    "AzureWebHookUrl": "<Teams 웹훅 주소>"
  }
}
```

3. 로컬 실행:
func start

4. Azure 배포 후 확인:
- Azure Portal 로그 확인

- Teams 채널에서 알림 확인

- Event Hub Data Explorer에서 데이터 수신 확인
