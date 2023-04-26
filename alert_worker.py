import datetime

import requests
import time
import threading


def test():
    telegram_token = '6260316858:AAG8xtzEHQH5NTfCnmuFLUvpxYp4Bbg2RyU'
    group_id = '-803770856'
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    print('Alert worker started')
    while True:
        is_not_empty = False
        # resp = requests.get('http://127.0.0.1:5000/log?sort_type=group')
        resp = requests.get('http://35.238.217.175:5000/log?sort_type=group')
        json_data = resp.json()
        list_worker = json_data.get('message').get('detail')
        text = '--Incident Worker Report\n'
        for worker in list_worker:
            last_seen = int(worker['last_seen'].split()[0])
            if last_seen > 20:
                is_not_empty = True
                text += f'<{worker["ip"]}> has down\n'
        text += f'--End report. Report time: {datetime.datetime.now()}'
        params = {'chat_id': group_id, 'text': text}
        if is_not_empty:
            requests.post(url, params=params)
        time.sleep(30 * 60)


threading.Thread(target=test).start()
