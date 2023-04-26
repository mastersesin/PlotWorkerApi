import datetime

import requests
import time
import threading


def test():
    telegram_token = '6260316858:AAG8xtzEHQH5NTfCnmuFLUvpxYp4Bbg2RyU'
    group_id = '-803770856'
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    while True:
        time.sleep(30 * 60)
        # resp = requests.get('http://127.0.0.1:5000/log?sort_type=group')
        resp = requests.get('http://35.238.217.175:5000/log?sort_type=group')
        json_data = resp.json()
        list_worker = json_data.get('message').get('detail')
        for worker in list_worker:
            last_seen = int(worker['last_seen'].split()[0])
            if last_seen > 20:
                params = {'chat_id': group_id, 'text': f'<{worker["ip"]}> has down'}
                requests.post(url, params=params)
        params = {'chat_id': group_id, 'text': f'--Check at {datetime.datetime.now()}'}
        requests.post(url, params=params)


threading.Thread(target=test).start()
