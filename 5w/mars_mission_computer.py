import random
from datetime import datetime


class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)

    def get_env(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        log_data = (
            f'{now}, '
            f"{self.env_values['mars_base_internal_temperature']}, "
            f"{self.env_values['mars_base_external_temperature']}, "
            f"{self.env_values['mars_base_internal_humidity']}, "
            f"{self.env_values['mars_base_external_illuminance']}, "
            f"{self.env_values['mars_base_internal_co2']}, "
            f"{self.env_values['mars_base_internal_oxygen']}\n"
        )

        with open('mars_log.txt', 'a') as file:
            file.write(log_data)

        return self.env_values


# 인스턴스 생성
ds = DummySensor()

# 환경값 설정
ds.set_env()

# 환경값 출력 및 로그 저장
env = ds.get_env()

print(env)