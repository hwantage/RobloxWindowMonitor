import pygetwindow as gw
from PIL import ImageGrab, Image, ImageChops
import time
import requests
import os
import re
import numpy as np
import configparser
import win32gui
import win32com.client
from skimage.metrics import structural_similarity as ssim

def get_roblox_window():
    """모든 윈도우 창을 검색하여 Roblox 게임 창을 찾습니다."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            class_name = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd)
            if class_name == "WINDOWSCLIENT" and title == "Roblox":
                windows.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)

    if windows:
        hwnd = windows[0]
        rect = win32gui.GetWindowRect(hwnd)
        window = gw.Window(hwnd)
        print(f"You have found the {window.title} window")
        return window

    return None  # 찾지 못한 경우 None 반환

def bring_window_to_front(window):
    """주어진 윈도우를 최상단으로 올리고 포커스를 맞춥니다."""
    try:
        # Win32 API를 사용하여 창을 최상단으로 가져옵니다.
        hwnd = window._hWnd
        win32gui.SetForegroundWindow(hwnd)
        
        # Shell을 사용하여 창을 활성화합니다.
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)  # 창이 완전히 활성화될 때까지 잠시 대기
        print(f"The window '{window.title}' to the top.")
    except Exception as e:
        print(f"An error occurred while raising the window to the top: {e}")

def capture_region(window, position):
    """윈도우의 특정 영역을 캡처합니다."""
    # Roblox 윈도우의 위치 및 크기
    bbox = (window.left, window.top, window.right, window.bottom)
    
    # 화면의 특정 영역을 캡처
    screenshot = ImageGrab.grab(bbox=bbox)
    
    # 특정 영역만 잘라내기
    position_tuple = tuple(map(int, position.split(", ")))
    capture = screenshot.crop(position_tuple)
    
    return capture

def capture_full_window(window, filename):
    """윈도우 전체 화면을 캡처하여 파일로 저장합니다."""
    # Roblox 윈도우의 위치 및 크기
    bbox = (window.left, window.top, window.right, window.bottom)
    
    # 전체 화면을 캡처
    full_screenshot = ImageGrab.grab(bbox=bbox)
    
    # 캡처한 전체 화면을 파일로 저장
    full_screenshot.save(filename)

def save_image(image, filename='capture_region.png'):
    """이미지를 파일로 저장합니다."""
    # 이미지를 지정된 파일 경로로 저장
    image.save(filename)
    print(f"The image was saved as {filename}.")

def calculate_image_similarity(image1, image2):
    """두 이미지의 구조적 유사도(SSIM)를 계산하여 퍼센트로 반환합니다."""
    # 이미지를 그레이스케일로 변환
    img1 = np.array(image1.convert('L'))
    img2 = np.array(image2.convert('L'))
    
    # SSIM 계산
    similarity = ssim(img1, img2)
    
    # 유사도를 퍼센트로 변환
    similarity_percent = similarity * 100
    
    return similarity_percent

def read_config_file(config_file):
    # 기본 환경 설정 값을 지정
    df_position = '600, 400, 730, 586'
    df_webhook = ''
    df_interval = 30
    df_similarity = 91.0
    # 파일이 없으면 에러 메시지를 출력하고 기본 값으로 리턴한다.
    if not os.path.exists(config_file):
        print(f"Config file '{config_file}' does not exist.")
        return {
            'screen_position': df_position,
            'webhook_url': df_webhook,
            'interval_seconds': df_interval,
            'similarity_percent': df_similarity
        }
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    screen_position = config['DEFAULT'].get('screen_position', df_position)
    webhook_url = config['DEFAULT'].get('webhook_url', df_webhook)
    interval_seconds = config['DEFAULT'].getint('interval_seconds', df_interval)
    similarity_percent = config['DEFAULT'].getfloat('similarity_percent', df_similarity)
    
    return {
        'screen_position': df_position,
        'webhook_url': webhook_url,
        'interval_seconds': interval_seconds,
        'similarity_percent': similarity_percent
    }

def send_discord_message_with_file(webhook_url, message, file_path):
    with open(file_path, 'rb') as file:
        data = {
            "content": message
        }
        files = {
            "file": file
        }
        response = requests.post(webhook_url, data=data, files=files)
    
    if response.status_code == 200:
        print("The message and file were sent successfully.")
    else:
        print(f"Message transmission failed. Status code: {response.status_code}")

def monitor_roblox():
    print("\n############ Information ############")
    print("# This program that detects whether the screen of a Roblox window has changed.")
    print("# Author: hwantagexsw2@gmail.com")
    print("# Git: https://github.com/hwantage")
    print("# License: MIT")
    
    previous_image = None  # 이전에 캡처한 이미지를 저장하는 변수
    saved_image_path = 'capture_region.png'
    print("\n############ Read Config Files ############")
    config_file = 'config.ini'
    print(f"Current Directory: {os.getcwd()}")
    print(f"config.ini Path: {os.path.abspath(config_file)}")
    config_values = read_config_file(config_file)

    screen_position = config_values['screen_position']
    webhook_url = config_values['webhook_url']
    interval_seconds = config_values['interval_seconds']
    similarity_percent = config_values['similarity_percent']

    print("\n############ Current Configure ############")
    print(f"Screen Position: {screen_position}")
    print(f"Webhook url: {webhook_url}")
    print(f"Time interval: {interval_seconds}s")
    print(f"Similarity: {similarity_percent}")
    if not webhook_url:
        print("\n* Webhook url isn't set up. Set the webhook URL to receive notifications.")

    print("\n############ Start Monitoring ############")
    while True:
        current_time = time.strftime('%Y.%m.%d - %H:%M:%S')
        print("\nCurrent time : " + current_time)
        
        window = get_roblox_window()
        
        if not window:
            print(f"Can't find the Roblox window. Check again after {interval_seconds} seconds.")
            time.sleep(interval_seconds)
            continue

        # 창을 최상단으로 올리고 포커스를 맞춤
        bring_window_to_front(window)

        current_image = capture_region(window, screen_position)
        
        # 이전 이미지가 존재하면 비교
        if previous_image is not None:
            similarity = calculate_image_similarity(previous_image, current_image)
            
            print(f"Image Similarity: {similarity:.2f}%")

            if similarity < similarity_percent:
                # 유사도가 설정값 미만인 경우 변화가 있는 것으로 간주
                full_capture_path = 'capture_full.png'
                capture_full_window(window, filename=full_capture_path)
                message = "Change detected: " + current_time + " (Similarity : " + "{:.2f}".format(similarity) + "%)"
                print(message)
                if webhook_url:
                    send_discord_message_with_file(webhook_url, message, full_capture_path)
            else:
                print("Nothing changes. Do nothing.")

        # 현재 이미지를 저장하고 다음 루프에서 비교에 사용
        previous_image = current_image
        
        # 현재 이미지를 파일로 저장 (항상 같은 파일을 덮어씀)
        save_image(current_image, filename=saved_image_path)

        # 초단위 대기 시간 설정
        time.sleep(interval_seconds)

if __name__ == "__main__":
    monitor_roblox()