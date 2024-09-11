# RobloxWindowMonitor

로블록스 매크로 돌리는 도중 튕김이나 방해를 받았는지 확인하기 위한 모니터링 프로그램입니다.

Python 으로 제작되었습니다.

게임 화면의 일부분을 캡처후 전후 비교를 통해 방해 여부를 판단합니다.

## 동작 방식

1. 프로그램을 실행하면 `class_name == "WINDOWSCLIENT" and title == "Roblox"` 인 윈도우가 있는지 확인합니다.

2. 윈도우를 최상단으로 올리고 포커스를 맞춥니다.

3. 윈도우의 특정 영역을 캡처해 `capture_region.png` 파일로 저장합니다.

4. 첫 번째 캡처 동작을 수행했다면 비교대상이 없으므로 인터벌 시간(초) 후 1)의 동작 부터 다시 수행합니다.

5. 이전 캡처 화면과 현재 캡처된 화면이 모두 있는 경우(두번째 수행부터) 이미지 유사도 비교를 수행합니다.

6. 이미지를 그레이스케일로 변환, 구조적 유사도(SSIM)를 계산, 유사도를 퍼센트로 변환합니다.

7. 설정된 유사도 임계치에 미달(이전화면과 달라짐)된 경우에 Roblox 윈도우 전체화면을 `capture_full.png` 파일로 저장합니다.

8. webhook_url 로 메시지와 이미지를 전송합니다.

9. 설정된 인터벌 시간마다 1)의 동작부터 반복 수행합니다.

## SSIM(Structural Similarity Index Measure : 구조적 유사도)

SSIM은 이미지의 구조, 밝기, 대비 등 세 가지 요소를 고려하여 두 이미지 간의 유사성을 평가합니다.

이 방법은 인간의 시각 시스템이 이미지를 인식하는 방식을 모방하여, 단순히 픽셀 값의 차이가 아닌 이미지의 구조적 특성을 비교함으로써 더 인간적인 시각에서 이미지의 유사성을 평가합니다.

SSIM은 MSE나 PSNR과 다르게 이미지의 질감, 구조, 밝기 등이 유사한지를 평가하여, 단순한 색상의 정확도보다는 이미지가 얼마나 ‘비슷하게 보이는지’에 더 중점을 둡니다.

MSE와 PSNR 대비 SSIM이 가지는 가장 큰 차이점은 SSIM이 이미지의 픽셀 값의 정확한 일치 여부가 아니라, 이미지의 구조적인 측면과 인간의 시각적 인식에 더 초점을 맞춘다는 점입니다. 이는 SSIM이 MSE나 PSNR보다 이미지의 질적인 측면을 더 잘 평가할 수 있게 해줍니다.

## config.ini

config.ini 파일은 다음과 같습니다.

```ini
[DEFAULT]
webhook_url =
screen_position = 600, 400, 730, 586
interval_seconds = 30
similarity_percent = 91
```

Discord 의 webhook_url 을 설정해야 알림 메시지를 받을 수 있습니다.

## capture_region.png 샘플

아래와 같은 영역을 대상으로 전후 비교를 수행합니다.

스크린의 위치는 config.ini 파일의 screen_position 값을 변경하여 조정할 수 있습니다.

![captured_region](https://github.com/user-attachments/assets/07fd6f0e-cdff-4153-8bdd-d3fc4f8780d5)

## Discord 메시지

아래와 같이 Discord 메시지를 발송합니다.

`Change detected: 2024.09.11 - 00:14:07 (Similarity : 80.06%)`

전체 스크린샷이 함께 전달됩니다.

- Similarity 값이 작을수록 전후 이미지가 낮은 유사도를 가지고 있다고 판단되어 차이가 심하다고 볼 수 있습니다.

## Install

```bash
> git clone https://github.com/hwantage/RobloxWindowMonitor.git
> pip3 install pyinstaller
> pyinstaller --onefile RobloxWindowMonitor.py
```

dist 디렉토리에 생성된 exe 파일을 실행하여 프로그램을 구동합니다.

## License

MIT
