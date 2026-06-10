import csv
import mysql.connector


class MySQLHelper:
    """MySQL 연결 및 쿼리 헬퍼 클래스."""

    def __init__(self, host, user, password, database):
        self._connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        self._cursor = self._connection.cursor()

    def execute(self, query, params=None):
        """단일 쿼리를 실행한다."""
        self._cursor.execute(query, params or ())

    def commit(self):
        """트랜잭션을 커밋한다."""
        self._connection.commit()

    def fetchall(self):
        """마지막 쿼리의 전체 결과를 반환한다."""
        return self._cursor.fetchall()

    def close(self):
        """커서와 연결을 닫는다."""
        self._cursor.close()
        self._connection.close()


def read_csv(file_path):
    """CSV 파일을 읽어 행 목록으로 반환한다."""
    rows = []
    with open(file_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            rows.append(row)
    return rows


def print_csv_preview(rows, count=5):
    """CSV 데이터 미리보기를 출력한다."""
    print(f'총 {len(rows)}개 행 로드 완료. 상위 {count}개 미리보기:')
    for row in rows[:count]:
        print(row)


def insert_weather_data(helper, rows):
    """CSV 행 목록을 mars_weather 테이블에 INSERT한다."""
    query = (
        'INSERT INTO mars_weather (mars_date, temp, storm) '
        'VALUES (%s, %s, %s)'
    )
    count = 0
    for row in rows:
        mars_date = row['mars_date']
        temp = int(float(row['temp']))
        # CSV 헤더 오타('stom') 대응
        storm = int(row.get('storm', row.get('stom', 0)))
        helper.execute(query, (mars_date, temp, storm))
        count += 1

    helper.commit()
    print(f'{count}개 행 INSERT 완료.')


def create_table_if_not_exists(helper):
    """mars_weather 테이블이 없으면 생성한다."""
    ddl = (
        'CREATE TABLE IF NOT EXISTS mars_weather ('
        '  weather_id INT AUTO_INCREMENT PRIMARY KEY,'
        '  mars_date  DATETIME NOT NULL,'
        '  temp       INT,'
        '  storm      INT'
        ')'
    )
    helper.execute(ddl)
    helper.commit()
    print('테이블 준비 완료.')


def main():
    # ── 접속 정보 ──────────────────────────────────────────
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_password',   # 실제 비밀번호로 교체
        'database': 'mars_db',         # 실제 DB 이름으로 교체
    }
    csv_path = 'mars_weathers_data.CSV'
    # ──────────────────────────────────────────────────────

    helper = MySQLHelper(**db_config)

    try:
        create_table_if_not_exists(helper)

        rows = read_csv(csv_path)
        print_csv_preview(rows)

        insert_weather_data(helper, rows)
    finally:
        helper.close()
        print('연결 종료.')


if __name__ == '__main__':
    main()