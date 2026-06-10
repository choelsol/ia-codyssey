import json
 
 
LOG_FILE = 'mission_computer_main.log'
JSON_FILE = 'mission_computer_main.json'
 
 
def read_log_file(filepath):
    """로그 파일을 읽어 리스트로 반환한다. 첫 번째 행(헤더)은 건너뛴다."""
    log_list = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for index, line in enumerate(f):
                line = line.strip()
                if index == 0 or not line:
                    continue
                parts = line.split(',', 2)
                if len(parts) == 3:
                    log_list.append([parts[0], parts[1], parts[2]])
    except FileNotFoundError:
        print(f'[오류] 파일을 찾을 수 없습니다: {filepath}')
    except PermissionError:
        print(f'[오류] 파일 읽기 권한이 없습니다: {filepath}')
    except OSError as e:
        print(f'[오류] 파일 읽기 중 오류 발생: {e}')
    return log_list
 
 
def print_log_list(log_list):
    """리스트 객체를 화면에 출력한다."""
    print('=' * 70)
    print('[ 로그 리스트 출력 ]')
    print('=' * 70)
    for entry in log_list:
        print(entry)
    print()
 
 
def sort_log_list_desc(log_list):
    """리스트 객체를 시간의 역순으로 정렬한다 (in-place)."""
    log_list.sort(key=lambda x: x[0], reverse=True)
 
 
def convert_to_dict(log_list):
    """리스트 객체를 사전(Dict) 객체로 전환한다."""
    log_dict = {}
    for index, entry in enumerate(log_list):
        log_dict[str(index)] = {
            'timestamp': entry[0],
            'event': entry[1],
            'message': entry[2],
        }
    return log_dict
 
 
def save_as_json(log_dict, filepath):
    """사전 객체를 JSON 파일로 저장한다."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_dict, f, ensure_ascii=False, indent=4)
        print(f'[완료] JSON 파일 저장 성공: {filepath}')
    except PermissionError:
        print(f'[오류] 파일 쓰기 권한이 없습니다: {filepath}')
    except OSError as e:
        print(f'[오류] 파일 저장 중 오류 발생: {e}')
 
 
def search_logs(log_dict, keyword):
    """사전 객체에서 특정 키워드가 포함된 로그를 검색해 출력한다."""
    print('=' * 70)
    print(f'[ 검색어: "{keyword}" ]')
    print('=' * 70)
    results = [
        v for v in log_dict.values()
        if keyword.lower() in v['message'].lower()
    ]
    if results:
        for entry in results:
            print(f"{entry['timestamp']}  [{entry['event']}]  {entry['message']}")
    else:
        print('검색 결과가 없습니다.')
    print()
 
 
def main():
    # 1. 로그 파일 읽기 및 리스트 변환
    log_list = read_log_file(LOG_FILE)
    if not log_list:
        print('[종료] 처리할 로그 데이터가 없습니다.')
        return
 
    # 2. 리스트 출력
    print_log_list(log_list)
 
    # 3. 시간 역순 정렬 후 출력
    sort_log_list_desc(log_list)
    print('[ 시간 역순 정렬 후 ]')
    print_log_list(log_list)
 
    # 4. 리스트 → 사전 변환
    log_dict = convert_to_dict(log_list)
 
    # 5. JSON 파일 저장
    save_as_json(log_dict, JSON_FILE)
 
    # 보너스: 키워드 검색
    keyword = input('\n검색할 키워드를 입력하세요 (건너뛰려면 Enter): ').strip()
    if keyword:
        search_logs(log_dict, keyword)
 
 
if __name__ == '__main__':
    main()