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
        print('Background refresh worker started.')
        cre_record = session.query(Credential).filter(
            and_(
                Credential.used_times >= 8,
                time.time() - Credential.last_used_timestamp > 24 * 60 * 60
            )
        ).all()
        print(cre_record)
        for cre in cre_record:
            cre.last_used_time = 0
            cre.used_times = 0
            session.commit()

    def run(self):
        while True:
            self.restart_credential()
            time.sleep(3)


b_worker = BackgroundWorker()
b_worker.start()