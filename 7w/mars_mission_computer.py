import platform
import os
import json
import subprocess


class MissionComputer:
    '''우주 기지 미션 컴퓨터의 상태를 관리하고 진단하는 클래스'''

    def __init__(self):
        self.settings = self._load_settings()

    def _load_settings(self):
        '''setting.txt 파일을 읽어 출력 항목 설정을 로드함'''
        settings = {}
        try:
            with open('setting.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        settings[key.strip()] = value.strip().lower() == 'true'
        except FileNotFoundError:
            # 설정 파일이 없을 경우 모든 항목을 기본적으로 True로 설정
            default_keys = [
                'os', 'os_version', 'cpu_type', 'cpu_cores',
                'memory_size', 'cpu_load', 'memory_load'
            ]
            settings = {key: True for key in default_keys}
        return settings

    def get_mission_computer_info(self):
        '''운영체제, CPU, 메모리 등 하드웨어 정적 정보를 반환함'''
        info = {}
        try:
            if self.settings.get('os'):
                info['os'] = platform.system()
            if self.settings.get('os_version'):
                info['os_version'] = platform.version()
            if self.settings.get('cpu_type'):
                info['cpu_type'] = platform.processor()
            if self.settings.get('cpu_cores'):
                info['cpu_cores'] = os.cpu_count()
            if self.settings.get('memory_size'):
                # 기본 라이브러리만 사용 시 OS별 명령어로 메모리 크기 확인
                if platform.system() == 'Windows':
                    cmd = 'wmic computersystem get totalphysicalmemory'
                    mem_bytes = subprocess.check_output(cmd, shell=True)
                    info['memory_size'] = mem_bytes.decode().split('\n')[1].strip()
                else:
                    # Linux/Unix 계열
                    info['memory_size'] = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        except Exception as e:
            info['error'] = f'시스템 정보를 가져오는 중 오류 발생: {e}'

        print(json.dumps(info, indent=4))
        return info

    def get_mission_computer_load(self):
        '''CPU 및 메모리의 실시간 사용량을 반환함'''
        load_info = {}
        try:
            # CPU 사용량 (기본 라이브러리만 사용할 경우 OS 명령 활용)
            if self.settings.get('cpu_load'):
                if platform.system() == 'Windows':
                    cmd = 'wmic cpu get loadpercentage'
                    output = subprocess.check_output(cmd, shell=True)
                    load_info['cpu_load_percent'] = output.decode().split('\n')[1].strip() + '%'
                else:
                    # Linux 계열 (1분 평균 부하량)
                    load_info['cpu_load_avg'] = os.getloadavg()[0]

            # 메모리 사용량
            if self.settings.get('memory_load'):
                if platform.system() == 'Windows':
                    cmd = 'wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value'
                    output = subprocess.check_output(cmd, shell=True).decode()
                    lines = [line.strip() for line in output.split('\n') if '=' in line]
                    mem_data = {l.split('=')[0]: int(l.split('=')[1]) for l in lines}
                    used_p = (1 - (mem_data['FreePhysicalMemory'] / mem_data['TotalVisibleMemorySize'])) * 100
                    load_info['memory_load_percent'] = f'{used_p:.2f}%'
                else:
                    # Linux 계열 예시
                    import tty  # 단순 예외 처리 확인용
                    load_info['memory_load'] = 'Linux memory parsing logic required'

        except Exception as e:
            load_info['error'] = f'부하 정보를 가져오는 중 오류 발생: {e}'

        print(json.dumps(load_info, indent=4))
        return load_info


if __name__ == '__main__':
    # MissionComputer 클래스를 runComputer 라는 이름으로 인스턴스화
    runComputer = MissionComputer()

    print('--- 미션 컴퓨터 시스템 정보 ---')
    runComputer.get_mission_computer_info()

    print('\n--- 미션 컴퓨터 실시간 부하 정보 ---')
    runComputer.get_mission_computer_load()