import json
import time

from flask import request, abort
from sqlalchemy import and_

from source import app, session
from source.object.sql import Credential, Log


@app.route('/credential', methods=['GET'])
def get_credential():
    cre_record: Credential = session.query(Credential).filter(
        Credential.used_times < 8,
    ).first()
    if cre_record:
        cre_record.last_used_time = int(time.time())
        cre_record.used_times += 1
        session.commit()
        return {'code': 3221, 'message': cre_record.to_json()}
    else:
        abort(404)


@app.route('/credential', methods=['POST'])
def post_credential():
    if request.is_json:
        json_credential_obj = request.json.get('json_credential')
        email = request.json.get('email')
        if json_credential_obj and email:
            is_exist = session.query(Credential).filter(
                Credential.json_credential == json.dumps(json_credential_obj)).first()
            if not is_exist:
                new_credential = Credential(
                    json_credential=json.dumps(json_credential_obj),
                    email=email
                )
                session.add(new_credential)
                session.commit()
                return {'code': 3221, 'message': 'hihi'}
            else:
                abort(400, 'Credential existed')
        else:
            abort(400, 'json_credential param not found')
    else:
        abort(400)


@app.route('/log', methods=['POST'])
def post_log():
    if request.is_json:
        ip = request.json.get('ip')
        file_name = request.json.get('file_name')
        email = request.json.get('email')
        if ip and file_name:
            new_log = Log(
                ip=ip,
                file_name=file_name,
                timestamp=int(time.time()),
                email=email
            )
            session.add(new_log)
            session.commit()
            return {'code': 3221, 'message': 'hihi'}
        else:
            abort(400, 'json_credential param not found')
    else:
        abort(400)


@app.route('/log', methods=['GET'])
def get_log():
    pem_name = request.args.get('pem_name')
    record = session.query(Log)
    if pem_name:
        record = record.filter(Log.pem_name == pem_name)
    record = record.all()
    return {'code': 3221, 'message': [x.to_json() for x in record]}
