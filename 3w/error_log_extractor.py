# 파일 이름: error_log_extractor.py

# 문제(에러) 로그만 추출하여 별도의 파일로 저장하는 코드
try:
    # 원본 로그 파일을 연다.
    with open("mission_computer_main.log", "r", encoding="utf-8") as file:
        # 전체 로그를 리스트로 저장한다.
        lines = file.readlines()

    # 로그 레벨이 INFO만 존재하기 때문에
    # 메시지 내용을 기준으로 문제를 판단하기 위한 키워드를 정의한다.
    error_keywords = ["unstable", "explosion", "error", "fail"]

    # 문제 로그를 저장할 리스트
    error_logs = []

    # 각 로그를 하나씩 검사한다.
    for line in lines:
        # 대소문자 구분 없이 비교하기 위해 소문자로 변환한다.
        lower_line = line.lower()
        
        # 키워드가 포함되어 있는지 확인한다.
        for keyword in error_keywords:
            if keyword in lower_line:
                # 문제 로그로 판단되면 리스트에 추가한다.
                error_logs.append(line)
                # 중복 저장을 방지하기 위해 break로 빠져나온다.
                break

    # 추출한 문제 로그를 별도의 파일로 저장한다.
    # 운영 환경에서 분석을 쉽게 하기 위한 방식이다.
    with open("error_logs.txt", "w", encoding="utf-8") as file:
        for log in error_logs:
            file.write(log)

    print("문제 로그 추출 완료 → error_logs.txt 생성됨")

# 파일이 없을 경우
except FileNotFoundError:
    print("로그 파일이 존재하지 않습니다.")

# 기타 예외 처리
except Exception as e:
    print("오류 발생:", e)