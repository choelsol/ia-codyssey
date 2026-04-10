# 파일 이름: main.py

# 예외 처리를 통해 파일 읽기 중 발생할 수 있는 오류를 대비한다.
try:
    # open() 함수로 로그 파일을 읽기 모드("r")로 연다.
    # encoding="utf-8"은 한글 및 문자열 깨짐 방지를 위해 설정한다.
    file = open("mission_computer_main.log", "r", encoding="utf-8")
    
    # 파일의 내용을 한 줄씩 읽기 위해 반복문을 사용한다.
    for line in file:
        # strip()을 사용하여 줄 끝의 개행문자(\n)를 제거하고 출력한다.
        print(line.strip())
    
    # 파일 사용이 끝났기 때문에 반드시 close()로 닫아준다.
    file.close()

# 파일이 존재하지 않을 경우 발생하는 예외 처리
except FileNotFoundError:
    print("파일을 찾을 수 없습니다.")

# 그 외 모든 예외를 처리하여 프로그램이 종료되지 않도록 한다.
except Exception as e:
    print("파일 처리 중 오류 발생:", e)