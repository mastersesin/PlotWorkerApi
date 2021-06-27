import json
import time

from flask import request, abort
from sqlalchemy import and_

from source import app, session
from source.object.sql import Credential


def restart_credential():
    cre_record = session.query(Credential).filter(
        and_(
            Credential.used_times >= 8,
        )
    )
    for cre in cre_record:
        cre: Credential
        if time.time() - cre.last_used_time > 24 * 60 * 60:
            cre.last_used_time = 0
            cre.used_times = 0
        session.commit()


@app.route('/credential', methods=['GET'])
def get_credential():
    restart_credential()
    cre_record: Credential = session.query(Credential).filter(
        and_(
            Credential.used_times < 8,
        )
    ).first()
    if cre_record:
        cre_record.last_used_time = int(time.time())
        cre_record.used_times += 1
        session.commit()
        return {'code': 3221, 'message': cre_record.to_json()}
    else:
        abort(500)


@app.route('/credential', methods=['POST'])
def post_credential():
    if request.is_json:
        json_credential_obj = request.json.get('json_credential')
        if json_credential_obj:
            new_credential = Credential(
                json_credential=json.dumps(json_credential_obj)
            )
            session.add(new_credential)
            session.commit()
            return {'code': 3221, 'message': 'hihi'}
        else:
            abort(400, 'json_credential param not found')
    else:
        abort(400)
