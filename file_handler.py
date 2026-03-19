# 파일 이름: file_handler.py

# 파일 처리 시 발생할 수 있는 다양한 예외 상황을 고려한다.
try:
    # with open()을 사용하면 파일을 자동으로 닫아주기 때문에 안전하다.
    with open("mission_computer_main.log", "r", encoding="utf-8") as file:
        
        # readlines()를 사용하여 파일의 모든 줄을 리스트 형태로 가져온다.
        lines = file.readlines()
        
        # 로그 파일이 비어있는 경우를 체크한다.
        if not lines:
            print("로그 파일이 비어 있습니다.")
        
        # 리스트에 저장된 각 줄을 하나씩 출력한다.
        for line in lines:
            print(line.strip())

# 파일이 존재하지 않을 경우
except FileNotFoundError:
    print("❌ 파일이 존재하지 않습니다.")

# 파일 접근 권한이 없는 경우
except PermissionError:
    print("❌ 파일 접근 권한이 없습니다.")

# 파일 인코딩 문제가 발생한 경우
except UnicodeDecodeError:
    print("❌ 파일 인코딩 오류 발생")

# 모든 예외를 처리하여 프로그램 안정성을 높인다.
except Exception as e:
    print("❌ 알 수 없는 오류 발생:", e)

# finally는 예외 발생 여부와 관계없이 항상 실행된다.
finally:
    print("파일 처리 종료")