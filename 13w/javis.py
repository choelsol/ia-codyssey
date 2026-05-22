import os
import csv
import datetime

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    print('필요한 라이브러리가 설치되어 있지 않습니다.')
    print('다음 명령어로 설치해 주세요:')
    print('  pip install sounddevice soundfile')
    exit(1)

try:
    import speech_recognition as sr
except ImportError:
    print('STT 라이브러리가 설치되어 있지 않습니다.')
    print('다음 명령어로 설치해 주세요:')
    print('  pip install SpeechRecognition')
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

    반환 형식: 년월일-시간분초 (예: 20240315-143022)
    """
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d-%H%M%S')


def record_audio(duration, device_id=None):
    """지정된 시간(초) 동안 음성을 녹음하고 WAV 파일로 저장한다.

    Args:
        duration: 녹음 시간 (초)
        device_id: 사용할 마이크 장치 ID (None이면 기본 장치 사용)

    Returns:
        저장된 파일 경로 또는 None (실패 시)
    """
    ensure_records_dir()
    base_name = get_filename()
    wav_path = os.path.join(RECORDS_DIR, base_name + '.wav')

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
        sf.write(wav_path, audio_data, SAMPLE_RATE)
        print(f'녹음 완료! 저장 위치: {wav_path}')
        return wav_path
    except sd.PortAudioError as e:
        print(f'마이크 오류: {e}')
        return None
    except Exception as e:
        print(f'녹음 중 오류 발생: {e}')
        return None


def transcribe_audio(wav_path):
    """WAV 파일을 STT로 변환하여 CSV 파일로 저장한다.

    음성 파일을 일정 구간으로 나누어 각 구간의 시작 시간과
    인식된 텍스트를 CSV로 저장한다.

    Args:
        wav_path: 변환할 WAV 파일 경로

    Returns:
        저장된 CSV 파일 경로 또는 None (실패 시)
    """
    if not os.path.exists(wav_path):
        print(f'파일을 찾을 수 없습니다: {wav_path}')
        return None

    base_name = os.path.splitext(os.path.basename(wav_path))[0]
    csv_path = os.path.join(RECORDS_DIR, base_name + '.csv')

    recognizer = sr.Recognizer()
    rows = []

    print(f'\nSTT 변환 시작: {wav_path}')

    try:
        with sr.AudioFile(wav_path) as source:
            audio_duration = source.DURATION
            chunk_duration = 30
            offset = 0.0

            while offset < audio_duration:
                remaining = audio_duration - offset
                current_chunk = min(chunk_duration, remaining)

                audio_chunk = recognizer.record(
                    source,
                    duration=current_chunk,
                    offset=0
                )

                time_str = _seconds_to_time_str(offset)

                try:
                    text = recognizer.recognize_google(
                        audio_chunk,
                        language='ko-KR'
                    )
                    print(f'  [{time_str}] {text}')
                except sr.UnknownValueError:
                    text = '(인식 불가)'
                    print(f'  [{time_str}] {text}')
                except sr.RequestError as e:
                    text = f'(API 오류: {e})'
                    print(f'  [{time_str}] {text}')

                rows.append([time_str, text])
                offset += current_chunk

    except Exception as e:
        print(f'STT 처리 중 오류 발생: {e}')
        return None

    if not rows:
        print('변환된 내용이 없습니다.')
        return None

    try:
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['시간', '인식된 텍스트'])
            writer.writerows(rows)
        print(f'CSV 저장 완료: {csv_path}')
        return csv_path
    except Exception as e:
        print(f'CSV 저장 중 오류 발생: {e}')
        return None


def _seconds_to_time_str(seconds):
    """초를 HH:MM:SS 형식의 문자열로 변환한다.

    Args:
        seconds: 변환할 시간 (초)

    Returns:
        HH:MM:SS 형식의 문자열
    """
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f'{hours:02d}:{minutes:02d}:{secs:02d}'


def transcribe_all_records():
    """records 폴더의 모든 WAV 파일을 STT 변환하여 CSV로 저장한다."""
    if not os.path.exists(RECORDS_DIR):
        print('녹음 파일이 없습니다. (records 폴더 없음)')
        return

    wav_files = [
        f for f in sorted(os.listdir(RECORDS_DIR))
        if f.endswith('.wav')
    ]

    if not wav_files:
        print('변환할 WAV 파일이 없습니다.')
        return

    print(f'\n총 {len(wav_files)}개의 파일을 변환합니다.')

    for fname in wav_files:
        wav_path = os.path.join(RECORDS_DIR, fname)
        csv_name = fname.replace('.wav', '.csv')
        csv_path = os.path.join(RECORDS_DIR, csv_name)

        if os.path.exists(csv_path):
            print(f'\n[건너뜀] 이미 변환된 파일: {fname}')
            continue

        transcribe_audio(wav_path)


def transcribe_selected_record():
    """사용자가 선택한 WAV 파일을 STT 변환한다."""
    if not os.path.exists(RECORDS_DIR):
        print('녹음 파일이 없습니다. (records 폴더 없음)')
        return

    wav_files = [
        f for f in sorted(os.listdir(RECORDS_DIR))
        if f.endswith('.wav')
    ]

    if not wav_files:
        print('변환할 WAV 파일이 없습니다.')
        return

    print('\n=== WAV 파일 목록 ===')
    for idx, fname in enumerate(wav_files):
        print(f'  [{idx + 1}] {fname}')

    choice = input('\n변환할 파일 번호를 입력하세요: ').strip()
    try:
        file_idx = int(choice) - 1
        if file_idx < 0 or file_idx >= len(wav_files):
            print('올바른 번호를 입력해 주세요.')
            return
        wav_path = os.path.join(RECORDS_DIR, wav_files[file_idx])
        transcribe_audio(wav_path)
    except ValueError:
        print('숫자를 입력해 주세요.')


def search_keyword_in_csv(keyword):
    """저장된 모든 CSV 파일에서 키워드를 검색하여 결과를 출력한다. (보너스)

    Args:
        keyword: 검색할 키워드 문자열
    """
    if not os.path.exists(RECORDS_DIR):
        print('CSV 파일이 없습니다. (records 폴더 없음)')
        return

    csv_files = [
        f for f in sorted(os.listdir(RECORDS_DIR))
        if f.endswith('.csv')
    ]

    if not csv_files:
        print('검색할 CSV 파일이 없습니다. 먼저 STT 변환을 진행해 주세요.')
        return

    print(f'\n=== "{keyword}" 검색 결과 ===')
    total_found = 0

    for fname in csv_files:
        csv_path = os.path.join(RECORDS_DIR, fname)
        file_results = []

        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)
                for row in reader:
                    if len(row) >= 2 and keyword in row[1]:
                        file_results.append(row)
        except Exception as e:
            print(f'  {fname} 읽기 오류: {e}')
            continue

        if file_results:
            print(f'\n  [파일] {fname}')
            for row in file_results:
                print(f'    {row[0]}  |  {row[1]}')
            total_found += len(file_results)

    if total_found == 0:
        print(f'  "{keyword}"를 포함한 내용을 찾을 수 없습니다.')
    else:
        print(f'\n총 {total_found}건의 결과를 찾았습니다.')


def list_records_by_date(start_date_str, end_date_str):
    """특정 날짜 범위의 녹음 파일 목록을 출력한다.

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
            csv_name = fname.replace('.wav', '.csv')
            csv_exists = '(CSV 있음)' if os.path.exists(
                os.path.join(RECORDS_DIR, csv_name)
            ) else ''
            date_str = file_dt.strftime('%Y년 %m월 %d일 %H:%M:%S')
            print(f'  {date_str}  |  {fname}  |  {size_kb:.1f} KB  {csv_exists}')
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
        csv_name = fname.replace('.wav', '.csv')
        csv_exists = '(CSV 있음)' if os.path.exists(
            os.path.join(RECORDS_DIR, csv_name)
        ) else ''
        try:
            name_part = fname.replace('.wav', '')
            file_dt = datetime.datetime.strptime(name_part, '%Y%m%d-%H%M%S')
            date_str = file_dt.strftime('%Y년 %m월 %d일 %H:%M:%S')
        except ValueError:
            date_str = '날짜 불명'
        print(f'  {date_str}  |  {fname}  |  {size_kb:.1f} KB  {csv_exists}')


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
    print('\n' + '=' * 45)
    print('   JAVIS - 화성 일지 음성 녹음 및 STT 시스템')
    print('=' * 45)
    print('  [녹음]')
    print('  1. 마이크 목록 확인')
    print('  2. 음성 녹음 시작')
    print('  3. 전체 녹음 파일 보기')
    print('  4. 날짜 범위로 녹음 파일 검색')
    print()
    print('  [STT 변환]')
    print('  5. 선택한 파일 STT 변환')
    print('  6. 전체 파일 STT 변환')
    print()
    print('  [검색] (보너스)')
    print('  7. CSV에서 키워드 검색')
    print()
    print('  0. 종료')
    print('=' * 45)


def main():
    """JAVIS 메인 실행 함수."""
    print('\nJAVIS 음성 녹음 및 STT 시스템을 시작합니다.')
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
            start = input('시작 날짜 (YYYYMMDD, 예: 20240301): ').strip()
            end = input('종료 날짜 (YYYYMMDD, 예: 20240315): ').strip()
            list_records_by_date(start, end)

        elif choice == '5':
            transcribe_selected_record()

        elif choice == '6':
            transcribe_all_records()

        elif choice == '7':
            keyword = input('검색할 키워드를 입력하세요: ').strip()
            if keyword:
                search_keyword_in_csv(keyword)
            else:
                print('키워드를 입력해 주세요.')

        elif choice == '0':
            print('\nJAVIS를 종료합니다. 오늘도 화성에서 수고하셨습니다, 한송희 박사님.\n')
            break

        else:
            print('올바른 메뉴 번호를 입력해 주세요.')


if __name__ == '__main__':
    main()
