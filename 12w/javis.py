import os
import datetime
 
try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
except ImportError:
    print('필요한 라이브러리가 설치되어 있지 않습니다.')
    print('다음 명령어로 설치해 주세요:')
    print('  pip install sounddevice soundfile numpy')
    exit(1)
 
 
RECORDS_DIR = 'records'
SAMPLE_RATE = 44100
CHANNELS = 1
 
 
def ensure_records_dir():
    """records 폴더가 없으면 생성한다."""
    if not os.path.exists(RECORDS_DIR):
        os.makedirs(RECORDS_DIR)
        print(f'녹음 폴더 생성: {RECORDS_DIR}/')
 
 
def list_microphones():
    """시스템에서 사용 가능한 마이크 목록을 출력한다."""
    print('\n=== 사용 가능한 마이크 목록 ===')
    devices = sd.query_devices()
    mic_found = False
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            marker = '  [기본]' if idx == sd.default.device[0] else ''
            print(f'  [{idx}] {device["name"]}{marker}')
            mic_found = True
    if not mic_found:
        print('  사용 가능한 마이크를 찾을 수 없습니다.')
    print()
    return mic_found
 
 
def get_filename():
    """현재 날짜와 시간을 기반으로 파일 이름을 생성한다.
 
    반환 형식: 년월일-시간분초.wav (예: 20240315-143022.wav)
    """
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d-%H%M%S') + '.wav'
 
 
def record_audio(duration, device_id=None):
    """지정된 시간(초) 동안 음성을 녹음하고 파일로 저장한다.
 
    Args:
        duration: 녹음 시간 (초)
        device_id: 사용할 마이크 장치 ID (None이면 기본 장치 사용)
 
    Returns:
        저장된 파일 경로 또는 None (실패 시)
    """
    ensure_records_dir()
    filename = get_filename()
    filepath = os.path.join(RECORDS_DIR, filename)
 
    print(f'\n녹음을 시작합니다... ({duration}초)')
    print('녹음 중... (말씀하세요)')
 
    try:
        audio_data = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='float32',
            device=device_id
        )
        sd.wait()
        sf.write(filepath, audio_data, SAMPLE_RATE)
        print(f'녹음 완료! 저장 위치: {filepath}')
        return filepath
    except sd.PortAudioError as e:
        print(f'마이크 오류: {e}')
        return None
    except Exception as e:
        print(f'녹음 중 오류 발생: {e}')
        return None
 
 
def list_records_by_date(start_date_str, end_date_str):
    """특정 날짜 범위의 녹음 파일 목록을 출력한다. (보너스 기능)
 
    Args:
        start_date_str: 시작 날짜 문자열 (예: '20240301')
        end_date_str: 종료 날짜 문자열 (예: '20240315')
    """
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        print('날짜 형식이 올바르지 않습니다. 형식: YYYYMMDD (예: 20240301)')
        return
 
    if not os.path.exists(RECORDS_DIR):
        print('녹음 파일이 없습니다. (records 폴더 없음)')
        return
 
    print(f'\n=== {start_date_str} ~ {end_date_str} 녹음 파일 목록 ===')
    found_files = []
 
    for fname in sorted(os.listdir(RECORDS_DIR)):
        if not fname.endswith('.wav'):
            continue
        try:
            name_part = fname.replace('.wav', '')
            file_dt = datetime.datetime.strptime(name_part, '%Y%m%d-%H%M%S')
            if start_date <= file_dt <= end_date:
                found_files.append((file_dt, fname))
        except ValueError:
            continue
 
    if found_files:
        for file_dt, fname in found_files:
            filepath = os.path.join(RECORDS_DIR, fname)
            size_kb = os.path.getsize(filepath) / 1024
            print(f'  {file_dt.strftime("%Y년 %m월 %d일 %H:%M:%S")}  |  {fname}  |  {size_kb:.1f} KB')
        print(f'\n총 {len(found_files)}개의 파일을 찾았습니다.')
    else:
        print('  해당 날짜 범위에 녹음 파일이 없습니다.')
 
 
def list_all_records():
    """저장된 모든 녹음 파일 목록을 출력한다."""
    if not os.path.exists(RECORDS_DIR):
        print('녹음 파일이 없습니다. (records 폴더 없음)')
        return
 
    files = [f for f in sorted(os.listdir(RECORDS_DIR)) if f.endswith('.wav')]
    if not files:
        print('저장된 녹음 파일이 없습니다.')
        return
 
    print(f'\n=== 전체 녹음 파일 목록 ({len(files)}개) ===')
    for fname in files:
        filepath = os.path.join(RECORDS_DIR, fname)
        size_kb = os.path.getsize(filepath) / 1024
        try:
            name_part = fname.replace('.wav', '')
            file_dt = datetime.datetime.strptime(name_part, '%Y%m%d-%H%M%S')
            date_str = file_dt.strftime('%Y년 %m월 %d일 %H:%M:%S')
        except ValueError:
            date_str = '날짜 불명'
        print(f'  {date_str}  |  {fname}  |  {size_kb:.1f} KB')
 
 
def select_microphone():
    """사용자가 마이크를 선택하도록 안내한다.
 
    Returns:
        선택한 마이크 ID 또는 None (기본값 사용)
    """
    has_mic = list_microphones()
    if not has_mic:
        return None
 
    choice = input('사용할 마이크 번호를 입력하세요 (Enter: 기본 마이크): ').strip()
    if choice == '':
        return None
    try:
        return int(choice)
    except ValueError:
        print('잘못된 입력입니다. 기본 마이크를 사용합니다.')
        return None
 
 
def get_duration():
    """사용자로부터 녹음 시간을 입력받는다.
 
    Returns:
        녹음 시간 (초), 기본값 10초
    """
    try:
        value = input('녹음 시간을 입력하세요 (초, Enter: 10초): ').strip()
        if value == '':
            return 10
        duration = int(value)
        if duration <= 0:
            print('1초 이상 입력해 주세요. 기본값 10초로 설정합니다.')
            return 10
        return duration
    except ValueError:
        print('숫자를 입력해 주세요. 기본값 10초로 설정합니다.')
        return 10
 
 
def show_menu():
    """메인 메뉴를 출력한다."""
    print('\n' + '=' * 40)
    print('   JAVIS - 화성 일지 음성 녹음 시스템')
    print('=' * 40)
    print('  1. 마이크 목록 확인')
    print('  2. 음성 녹음 시작')
    print('  3. 전체 녹음 파일 보기')
    print('  4. 날짜 범위로 녹음 파일 검색')
    print('  0. 종료')
    print('=' * 40)
 
 
def main():
    """JAVIS 메인 실행 함수."""
    print('\nJAVIS 음성 녹음 시스템을 시작합니다.')
    ensure_records_dir()
 
    while True:
        show_menu()
        choice = input('메뉴를 선택하세요: ').strip()
 
        if choice == '1':
            list_microphones()
 
        elif choice == '2':
            device_id = select_microphone()
            duration = get_duration()
            record_audio(duration, device_id)
 
        elif choice == '3':
            list_all_records()
 
        elif choice == '4':
            start = input('시작 날짜를 입력하세요 (YYYYMMDD, 예: 20240301): ').strip()
            end = input('종료 날짜를 입력하세요 (YYYYMMDD, 예: 20240315): ').strip()
            list_records_by_date(start, end)
 
        elif choice == '0':
            print('\nJAVIS를 종료합니다. 오늘도 화성에서 수고하셨습니다, 한송희 박사님.\n')
            break
 
        else:
            print('올바른 메뉴 번호를 입력해 주세요.')
 
 
if __name__ == '__main__':
    main()