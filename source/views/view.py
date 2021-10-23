import json
import time

from flask import request, abort
from sqlalchemy import and_, desc, func

from source import app, session
from source.object.sql import Credential, Log


def convert_sort_to_json(obj):
    print(obj)
    return {
        'ip': obj[0],
        'total_uploaded_plot': obj[1],
        'last_seen': '{} minutes'.format(int((time.time() - obj[2]) / 60))
    }


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


@app.route('/credential', methods=['GET'])
def get_credential():
    restart_credential()
    is_check = request.args.get('is_check')
    filter_type = request.args.get('filter_type')
    drive = request.args.get('drive')
    if drive:
        if not filter_type:
            cre_record: Credential = session.query(Credential).filter(
                and_(Credential.used_times < 8, Credential.drive == drive)).order_by(
                desc(Credential.last_used_timestamp)).first()
            if cre_record:
                if not is_check:
                    cre_record.last_used_timestamp = int(time.time())
                    cre_record.used_times += 1
                    session.commit()
                return {'code': 3221, 'message': cre_record.to_json()}
            else:
                abort(404)
        else:
            cre_record: Credential = session.query(Credential).all()
            if cre_record:
                return {'code': 3221, 'message': [x.to_json() for x in cre_record]}
            else:
                abort(404)
    else:
        abort(400, 'Not specified drive id')


@app.route('/credential', methods=['POST'])
def post_credential():
    if request.is_json:
        json_credential_obj = request.json.get('json_credential')
        drive = request.json.get('drive')
        if json_credential_obj and drive:
            is_exist = session.query(Credential).filter(
                Credential.json_credential == json.dumps(json_credential_obj)).first()
            if not is_exist:
                new_credential = Credential(
                    json_credential=json.dumps(json_credential_obj),
                    drive=drive
                )
                session.add(new_credential)
                session.commit()
                return {'code': 3221, 'message': 'hihi'}
            else:
                abort(400, 'Credential existed')
        else:
            abort(400, 'json_credential or drive param not found')
    else:
        abort(400)


@app.route('/log', methods=['POST'])
def post_log():
    if request.is_json:
        file_name = request.json.get('file_name')
        if file_name:
            new_log = Log(
                ip=request.remote_addr,
                file_name=file_name,
                timestamp=int(time.time()),
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
    sort_type = request.args.get('sort_type')
    if not sort_type:
        record = session.query(Log)
        if pem_name:
            record = record.filter(Log.pem_name == pem_name)
        record = record.order_by(Log.timestamp.desc()).limit(100).all()
        return {'code': 3221, 'message': [x.to_json() for x in record]}
    else:
        if sort_type == 'group':
            current_timestamp = int(time.time())
            delta_utc_to_gmt7 = 7 * 60 * 60
            today_start_timestamp = current_timestamp - (current_timestamp + delta_utc_to_gmt7) % 86400
            # record = session.query(Log.).filter(Log.timestamp >= today_start_timestamp).order_by(
            #     Log.timestamp.desc()).group_by(Log.ip).all()
            records = session.query(Log.ip, func.count(Log.ip), func.max(Log.timestamp)).filter(
                Log.timestamp >= today_start_timestamp).group_by(
                Log.ip)
            total_plot_posted = session.query(Log).filter(Log.timestamp >= today_start_timestamp).count()
            return {
                'code': 3221,
                'message': {
                    'total_plot': total_plot_posted,
                    'total_ip': records.count(),
                    'detail': [convert_sort_to_json(x) for x in records.all()]
                }
            }
