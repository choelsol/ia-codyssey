# 파일 이름: reverse_log.py

# 로그를 최신순(역순)으로 출력하기 위한 코드
try:
    # 로그 파일을 읽기 모드로 연다.
    with open("mission_computer_main.log", "r", encoding="utf-8") as file:
        
        # readlines()로 전체 데이터를 리스트로 저장한다.
        # 역순 정렬을 위해서는 반드시 리스트 형태가 필요하다.
        lines = file.readlines()
        
        # 슬라이싱 [::-1]을 사용하여 리스트를 뒤집는다.
        # 이는 가장 간단하고 효율적인 역순 처리 방법이다.
        reversed_lines = lines[::-1]
        
        # 역순으로 정렬된 데이터를 한 줄씩 출력한다.
        for line in reversed_lines:
            print(line.strip())

# 파일이 존재하지 않을 경우 예외 처리
except FileNotFoundError:
    print("파일을 찾을 수 없습니다.")

# 기타 예외 처리
except Exception as e:
    print("오류 발생:", e)