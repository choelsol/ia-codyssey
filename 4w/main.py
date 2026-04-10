# Mars Base Inventory Analysis
# 화성 기지 물질 데이터를 분석하여 인화성 높은 물질을 분류하는 프로그램


def read_csv(file_name):
    """
    CSV 파일을 읽어서 리스트 형태로 변환하는 함수
    """
    inventory = []

    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()

            # 첫 줄은 헤더이므로 제외하고 반복
            for line in lines[1:]:
                parts = line.strip().split(',')

                # 인화성 값은 숫자로 변환 (에러 대비)
                try:
                    flammability = float(parts[4])
                except (ValueError, IndexError):
                    flammability = 0.0

                # 데이터를 딕셔너리 형태로 저장 (가독성 향상)
                item = {
                    'substance': parts[0],
                    'weight': parts[1],
                    'specific_gravity': parts[2],
                    'strength': parts[3],
                    'flammability': flammability
                }

                inventory.append(item)

    # 파일이 없을 경우 예외 처리
    except FileNotFoundError:
        print('파일을 찾을 수 없습니다.')

    # 기타 에러 처리
    except Exception as error:
        print('파일 읽기 오류:', error)

    return inventory


def sort_inventory(data):
    """
    인화성 기준으로 내림차순 정렬
    (위험한 물질이 위로 오도록)
    """
    return sorted(data, key=lambda x: x['flammability'], reverse=True)


def filter_dangerous(data):
    """
    인화성 0.7 이상인 위험 물질만 필터링
    """
    return [item for item in data if item['flammability'] >= 0.7]


def print_data(title, data):
    """
    데이터를 출력하는 공통 함수
    (코드 중복 제거 목적)
    """
    print(f'\n=== {title} ===')
    for item in data:
        print(item)


def save_csv(file_name, data):
    """
    위험 물질 데이터를 CSV 파일로 저장
    """
    try:
        with open(file_name, 'w') as file:
            # CSV 헤더 작성
            file.write('Substance,Weight,Specific Gravity,Strength,Flammability\n')

            # 데이터 한 줄씩 작성
            for item in data:
                line = (
                    f"{item['substance']},"
                    f"{item['weight']},"
                    f"{item['specific_gravity']},"
                    f"{item['strength']},"
                    f"{item['flammability']}\n"
                )
                file.write(line)

        print(f'{file_name} 저장 완료')

    except Exception as error:
        print('CSV 저장 오류:', error)


def save_binary(file_name, data):
    """
    데이터를 이진 파일로 저장
    (문자열 → 바이트 변환)
    """
    try:
        with open(file_name, 'wb') as file:
            file.write(str(data).encode())

        print(f'{file_name} 저장 완료')

    except Exception as error:
        print('이진 파일 저장 오류:', error)


def read_binary(file_name):
    """
    이진 파일을 읽어서 출력
    """
    try:
        with open(file_name, 'rb') as file:
            content = file.read().decode()

        print('\n=== 이진 파일 내용 ===')
        print(content)

    except Exception as error:
        print('이진 파일 읽기 오류:', error)


def main():
    """
    전체 실행 흐름을 담당하는 메인 함수
    """
    file_name = 'Mars_Base_Inventory_List.csv'

    # 1. CSV 파일 읽기
    inventory = read_csv(file_name)
    print(inventory)

    # 2. 인화성 기준 정렬
    sorted_inventory = sort_inventory(inventory)
    print_data('인화성 기준 정렬', sorted_inventory)

    # 3. 위험 물질 필터링
    dangerous_items = filter_dangerous(sorted_inventory)
    print_data('위험 물질 (0.7 이상)', dangerous_items)

    # 4. CSV 파일 저장
    save_csv('Mars_Base_Inventory_danger.csv', dangerous_items)

    # 5. 보너스 - 이진 파일 저장 및 읽기
    save_binary('Mars_Base_Inventory_List.bin', sorted_inventory)
    read_binary('Mars_Base_Inventory_List.bin')


# 프로그램 실행 시작점
if __name__ == '__main__':
    main()