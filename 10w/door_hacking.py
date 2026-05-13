import itertools
import string
import struct
import time
import zipfile
from datetime import datetime, timedelta
 
 
# ---------------------------------------------------------------------------
# ZipCrypto 상수 및 유틸리티 (보너스: 사전 필터링용)
# ---------------------------------------------------------------------------
 
def _build_crc_table():
    """CRC-32 룩업 테이블을 생성하여 반환한다."""
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if crc & 1 else crc >> 1
        table.append(crc)
    return tuple(table)
 
 
_CRC_TABLE = _build_crc_table()
 
 
def _crc32_byte(crc, byte):
    """단일 바이트에 대한 CRC-32 갱신값을 반환한다."""
    return (_CRC_TABLE[(crc ^ byte) & 0xFF]) ^ (crc >> 8)
 
 
def _zipcrypto_check(password_bytes, enc_header, target_byte):
    """ZipCrypto 암호화 헤더를 복호화하여 마지막 바이트가 target_byte와
    일치하면 True를 반환한다 (사전 필터: ~1/256 통과율).
 
    ZipCrypto 키 초기화 및 헤더 복호화를 순수 Python으로 구현한다.
    외부 라이브러리 없이 zipfile.read() 보다 훨씬 빠르게 후보를 걸러낸다.
 
    Args:
        password_bytes (bytes): 검사할 비밀번호
        enc_header     (bytes): ZipCrypto 암호화 헤더 12바이트
        target_byte    (int):   예상 복호화 값
 
    Returns:
        bool: 마지막 복호화 바이트가 target_byte와 같으면 True
    """
    k0 = 0x12345678
    k1 = 0x23456789
    k2 = 0x34567890
 
    for b in password_bytes:
        k0 = _crc32_byte(k0, b)
        k1 = (k1 + (k0 & 0xFF)) & 0xFFFFFFFF
        k1 = (k1 * 0x08088405 + 1) & 0xFFFFFFFF
        k2 = _crc32_byte(k2, k1 >> 24)
 
    last_dec = 0
    for enc_byte in enc_header:
        t = (k2 | 2) & 0xFFFF
        keystream = ((t * (t ^ 1)) >> 8) & 0xFF
        last_dec = enc_byte ^ keystream
        k0 = _crc32_byte(k0, last_dec)
        k1 = (k1 + (k0 & 0xFF)) & 0xFFFFFFFF
        k1 = (k1 * 0x08088405 + 1) & 0xFFFFFFFF
        k2 = _crc32_byte(k2, k1 >> 24)
 
    return last_dec == target_byte
 
 
def _read_zip_crypto_header(zip_path):
    """ZIP 파일에서 ZipCrypto 암호화 헤더와 체크 바이트를 추출한다.
 
    ZIP 로컬 파일 헤더 구조 (PKWARE 스펙):
      오프셋  6: flag_bits (2 bytes)
      오프셋 10: mod_time  (2 bytes)
      오프셋 14: CRC-32    (4 bytes)
      오프셋 26: fname_len (2 bytes)
      오프셋 28: extra_len (2 bytes)
      오프셋 30 + fname_len + extra_len: 암호화 헤더 시작 (12 bytes)
 
    flag bit3(0x08) 설정 여부에 따라 체크 바이트 선택 (Python zipfile 기준):
      - bit3 설정:   target = (mod_time >> 8) & 0xFF
      - bit3 미설정: target = (CRC-32 >> 24) & 0xFF
 
    Args:
        zip_path (str): ZIP 파일 경로
 
    Returns:
        tuple: (enc_header: bytes, target_byte: int)
 
    Raises:
        FileNotFoundError: 파일이 없을 때
        ValueError: ZIP 헤더를 파싱할 수 없을 때
    """
    try:
        with open(zip_path, 'rb') as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f'파일을 찾을 수 없습니다: {zip_path}')
 
    if not raw.startswith(b'PK\x03\x04'):
        raise ValueError('올바른 ZIP 로컬 파일 헤더를 찾을 수 없습니다.')
 
    flag_bits = struct.unpack_from('<H', raw, 6)[0]
    mod_time = struct.unpack_from('<H', raw, 10)[0]
    crc32_val = struct.unpack_from('<I', raw, 14)[0]
    fname_len = struct.unpack_from('<H', raw, 26)[0]
    extra_len = struct.unpack_from('<H', raw, 28)[0]
 
    enc_start = 30 + fname_len + extra_len
    enc_header = raw[enc_start:enc_start + 12]
 
    if len(enc_header) < 12:
        raise ValueError('암호화 헤더(12바이트)를 읽을 수 없습니다.')
 
    # Python zipfile 소스 코드(_MASK_USE_DATA_DESCRIPTOR = 0x08)와 동일한 조건
    if flag_bits & 0x08:
        target_byte = (mod_time >> 8) & 0xFF
    else:
        target_byte = (crc32_val >> 24) & 0xFF
 
    return enc_header, target_byte
 
 
# ---------------------------------------------------------------------------
# 출력 헬퍼
# ---------------------------------------------------------------------------
 
def _print_progress(attempt, total, elapsed, extra=''):
    """진행 상황 한 줄을 출력한다."""
    pct = attempt / total * 100
    speed = attempt / elapsed if elapsed > 0 else 0
    remain = (total - attempt) / speed if speed > 0 else 0
    eta = str(timedelta(seconds=int(remain)))
    msg = (
        f'  시도 {attempt:>14,} / {total:,} '
        f'({pct:5.2f}%) | '
        f'경과 {elapsed:7.1f}s | '
        f'속도 {speed:>10,.0f}/s | '
        f'잔여 {eta}'
    )
    if extra:
        msg += f' | {extra}'
    print(msg)
 
 
def _print_success(password, attempt, elapsed, extra=''):
    """비밀번호 발견 메시지를 출력한다."""
    speed = attempt / elapsed if elapsed > 0 else 0
    print()
    print('=' * 62)
    print('  ★ 비밀번호 발견!')
    print(f'  비밀번호  : {password}')
    print(f'  시도 횟수 : {attempt:,}회')
    print(f'  소요 시간 : {elapsed:.2f}초')
    print(f'  평균 속도 : {speed:,.0f}회/초')
    if extra:
        print(f'  부가 정보 : {extra}')
    print('=' * 62)
 
 
def _save_password(password, output_txt):
    """비밀번호를 텍스트 파일에 저장한다."""
    try:
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(password)
        print(f'  저장 완료 : {output_txt}')
    except IOError as e:
        print(f'[오류] 파일 저장 실패: {e}')
 
 
# ---------------------------------------------------------------------------
# 기본 브루트포스
# ---------------------------------------------------------------------------
 
def unlock_zip(zip_path, output_txt='password.txt'):
    """ZIP 파일의 암호를 브루트포스로 해독한다.
 
    소문자 알파벳 + 숫자(36자)로 구성된 6자리 비밀번호를 순차 탐색한다.
    매 100,000회마다 시작 시간, 반복 횟수, 진행 시간을 출력한다.
    성공 시 비밀번호를 output_txt 파일에 저장한다.
 
    Args:
        zip_path   (str): 대상 ZIP 파일 경로
        output_txt (str): 발견된 비밀번호를 저장할 파일 경로
 
    Returns:
        str | None: 발견된 비밀번호 문자열, 실패 시 None
    """
    charset = string.ascii_lowercase + string.digits
    total = len(charset) ** 6
    report_interval = 100_000
 
    print('=' * 62)
    print('  [기본] ZIP 브루트포스 크래커')
    print('=' * 62)
    print(f'  대상 파일    : {zip_path}')
    print(f'  문자 집합    : {charset}')
    print(f'  비밀번호 길이: 6자리')
    print(f'  총 경우의 수 : {total:,} 가지')
    print(f'  시작 시간    : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 62)
 
    try:
        zf = zipfile.ZipFile(zip_path, 'r')
    except FileNotFoundError:
        print(f'[오류] 파일을 찾을 수 없습니다: {zip_path}')
        return None
    except zipfile.BadZipFile:
        print(f'[오류] 올바른 ZIP 파일이 아닙니다: {zip_path}')
        return None
 
    first_file = zf.namelist()[0]
    start_ts = time.time()
    attempt = 0
 
    try:
        for combo in itertools.product(charset, repeat=6):
            attempt += 1
            password = ''.join(combo)
 
            try:
                zf.read(first_file, pwd=password.encode())
                elapsed = time.time() - start_ts
                _print_success(password, attempt, elapsed)
                _save_password(password, output_txt)
                return password
            except (RuntimeError, Exception):
                pass  # 잘못된 비밀번호 → 계속
 
            if attempt % report_interval == 0:
                elapsed = time.time() - start_ts
                _print_progress(attempt, total, elapsed)
 
    except KeyboardInterrupt:
        print('\n[중단] 사용자가 중단했습니다.')
        return None
    finally:
        zf.close()
 
    print('[실패] 비밀번호를 찾지 못했습니다.')
    return None
 
 
# ---------------------------------------------------------------------------
# [보너스] ZipCrypto 헤더 사전 필터링 고속 크래커
# ---------------------------------------------------------------------------
 
def unlock_zip_fast(zip_path, output_txt='password.txt'):
    """[보너스] ZipCrypto 헤더 사전 필터링을 이용한 고속 크래커.
 
    ■ 알고리즘 설명
      ZipCrypto 암호화는 비밀번호로 초기화된 3개의 32비트 키(k0, k1, k2)를
      이용해 12바이트 헤더를 XOR 암호화한다. 이 헤더의 마지막 복호화 바이트는
      비밀번호 검증에 사용되는 체크 바이트(target_byte)와 일치해야 한다.
 
      단계별 처리:
        1. ZIP 파일 바이너리에서 12바이트 암호화 헤더와 target_byte 추출
        2. 각 후보 비밀번호에 대해 ZipCrypto 키 스케줄을 Python으로 실행,
           헤더 마지막 바이트만 복호화하여 target_byte와 비교
           → 불일치 시 즉시 기각 (약 255/256 ≈ 99.6% 기각)
        3. 필터 통과 후보만 zipfile.read()로 최종 검증
 
    ■ 성능 효과
      - 사전 필터 통과율: ~1/256 ≈ 0.39%
      - zipfile.read() 호출 횟수 약 256배 감소
      - 단일 스레드, 순수 Python으로도 기본 방식 대비 수배 빠름
 
    ■ 오탐(False Positive)
      - 필터를 통과했으나 실제 비밀번호가 아닌 경우
      - 약 256회 중 1회 발생, 최종 검증에서 걸러짐
 
    Args:
        zip_path   (str): 대상 ZIP 파일 경로
        output_txt (str): 발견된 비밀번호를 저장할 파일 경로
 
    Returns:
        str | None: 발견된 비밀번호 문자열, 실패 시 None
    """
    charset = string.ascii_lowercase + string.digits
    total = len(charset) ** 6
    report_interval = 5_000_000
 
    print('=' * 62)
    print('  [보너스] ZipCrypto 헤더 필터링 고속 크래커')
    print('=' * 62)
    print(f'  대상 파일    : {zip_path}')
    print(f'  문자 집합    : {charset}')
    print(f'  비밀번호 길이: 6자리')
    print(f'  총 경우의 수 : {total:,} 가지')
    print(f'  시작 시간    : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('  알고리즘     : ZipCrypto 헤더 사전 필터 (~1/256 통과)')
    print('=' * 62)
 
    # ZIP 헤더 파싱
    try:
        enc_header, target_byte = _read_zip_crypto_header(zip_path)
    except (FileNotFoundError, ValueError) as e:
        print(f'[경고] ZIP 헤더 파싱 실패: {e}')
        print('  → 기본 브루트포스로 전환합니다.')
        return unlock_zip(zip_path, output_txt)
 
    print(f'  암호화 헤더  : {enc_header.hex()}')
    print(f'  체크 바이트  : 0x{target_byte:02x}')
    print('=' * 62)
 
    # ZIP 파일 열기
    try:
        zf = zipfile.ZipFile(zip_path, 'r')
    except FileNotFoundError:
        print(f'[오류] 파일을 찾을 수 없습니다: {zip_path}')
        return None
    except zipfile.BadZipFile:
        print(f'[오류] 올바른 ZIP 파일이 아닙니다: {zip_path}')
        return None
 
    first_file = zf.namelist()[0]
    start_ts = time.time()
    attempt = 0
    candidates = 0
    false_positives = 0
 
    try:
        for combo in itertools.product(charset, repeat=6):
            attempt += 1
            pwd_bytes = bytes(ord(c) for c in combo)
 
            # ── 1단계: ZipCrypto 헤더 사전 필터 (순수 Python)
            if not _zipcrypto_check(pwd_bytes, enc_header, target_byte):
                if attempt % report_interval == 0:
                    elapsed = time.time() - start_ts
                    _print_progress(
                        attempt, total, elapsed,
                        extra=f'후보 {candidates:,}개'
                    )
                continue
 
            candidates += 1
 
            # ── 2단계: zipfile 최종 검증 (후보만)
            password = ''.join(combo)
            try:
                zf.read(first_file, pwd=password.encode())
                elapsed = time.time() - start_ts
                _print_success(
                    password, attempt, elapsed,
                    extra=(f'후보 {candidates}개 검증 | '
                           f'오탐 {false_positives}개')
                )
                _save_password(password, output_txt)
                return password
            except (RuntimeError, Exception):
                false_positives += 1
 
            if attempt % report_interval == 0:
                elapsed = time.time() - start_ts
                _print_progress(
                    attempt, total, elapsed,
                    extra=f'후보 {candidates:,}개'
                )
 
    except KeyboardInterrupt:
        print('\n[중단] 사용자가 중단했습니다.')
        return None
    finally:
        zf.close()
 
    print('[실패] 비밀번호를 찾지 못했습니다.')
    return None
 
 
# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------
 
if __name__ == '__main__':
    ZIP_PATH = 'emergency_storage_key.zip'
    OUTPUT_TXT = 'password.txt'
 
    # [보너스] 고속 크래커 실행
    result = unlock_zip_fast(ZIP_PATH, OUTPUT_TXT)
 
    # 고속 크래커 실패 시 기본 브루트포스로 재시도
    if result is None:
        print('\n고속 크래커 실패 → 기본 브루트포스로 재시도합니다.\n')
        result = unlock_zip(ZIP_PATH, OUTPUT_TXT)
 
    if result:
        print(f'\n[완료] ZIP 비밀번호: {result}')
    else:
        print('\n[실패] 비밀번호를 찾지 못했습니다.')