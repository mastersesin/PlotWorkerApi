import time
import threading

from sqlalchemy import and_

from source import session
from source.object.sql import Credential


class BackgroundWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    @staticmethod
    def restart_credential():
        cre_record = session.query(Credential).filter(
            and_(
                Credential.used_times >= 8,
                int(time.time()) - Credential.last_used_timestamp > 24 * 60 * 60
            )
        ).all()
        for cre in cre_record:
            cre.last_used_time = 0
            cre.used_times = 0
            session.commit()

    def run(self):
        while True:
            self.restart_credential()
            print('Background service start normally')
            time.sleep(10 * 60)


b_worker = BackgroundWorker()
b_worker.start()