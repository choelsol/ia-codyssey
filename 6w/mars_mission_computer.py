import time
import json
import random


class DummySensor:
    '''화성 기지의 환경 데이터를 생성하는 더미 센서 클래스'''

    def get_temperature_internal(self):
        return round(random.uniform(18.0, 26.0), 2)

    def get_temperature_external(self):
        return round(random.uniform(-120.0, -20.0), 2)

    def get_humidity_internal(self):
        return round(random.uniform(30.0, 50.0), 2)

    def get_illuminance_external(self):
        return round(random.uniform(0.0, 1000.0), 2)

    def get_co2_internal(self):
        return round(random.uniform(300.0, 500.0), 2)

    def get_oxygen_internal(self):
        return round(random.uniform(19.0, 22.0), 2)


class MissionComputer:
    '''화성 기지의 환경 정보를 수집하고 출력하는 미션 컴퓨터 클래스'''

    def __init__(self):
        self.ds = DummySensor()
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0
        }
        # 5분 평균 계산을 위한 데이터 저장소
        self.history = {key: [] for key in self.env_values.keys()}
        self.start_time = time.time()

    def get_sensor_data(self):
        '''5초마다 센서 데이터를 수집하고 출력하며, 5분마다 평균을 계산함'''
        try:
            while True:
                # 1. 센서의 값을 가져와서 env_values에 담기
                self.env_values['mars_base_internal_temperature'] = \
                    self.ds.get_temperature_internal()
                self.env_values['mars_base_external_temperature'] = \
                    self.ds.get_temperature_external()
                self.env_values['mars_base_internal_humidity'] = \
                    self.ds.get_humidity_internal()
                self.env_values['mars_base_external_illuminance'] = \
                    self.ds.get_illuminance_external()
                self.env_values['mars_base_internal_co2'] = \
                    self.ds.get_co2_internal()
                self.env_values['mars_base_internal_oxygen'] = \
                    self.ds.get_oxygen_internal()

                # 평균 계산을 위해 히스토리에 추가
                for key in self.env_values:
                    self.history[key].append(self.env_values[key])

                # 2. env_values의 값을 JSON 형태로 출력
                print('--- Real-time Environment Data ---')
                print(json.dumps(self.env_values, indent=4))

                current_time = time.time()
                elapsed_time = current_time - self.start_time

                # 5분(300초)이 경과했는지 확인
                if elapsed_time >= 300:
                    self._display_average_data()
                    self.start_time = current_time  # 시간 초기화
                    # 히스토리 초기화
                    self.history = {key: [] for key in self.env_values.keys()}

                # 3. 5초 대기
                time.sleep(5)

        except KeyboardInterrupt:
            # 보너스 과제: 특정 키(Ctrl+C) 입력 시 종료
            print('\nSystem stopped....')

    def _display_average_data(self):
        '''5분간 수집된 데이터의 평균을 출력'''
        avg_values = {}
        for key, values in self.history.items():
            if values:
                avg_values[key] = round(sum(values) / len(values), 2)
        
        print('\n' + '=' * 40)
        print('AVERAGE DATA FOR THE LAST 5 MINUTES')
        print(json.dumps(avg_values, indent=4))
        print('=' * 40 + '\n')


if __name__ == '__main__':
    # MissionComputer 인스턴스화
    RunComputer = MissionComputer()
    # 환경 데이터 출력 시작
    RunComputer.get_sensor_data()