import json
import time

import sqlalchemy
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
        int(time.time()) - Credential.last_used_timestamp > 24 * 60 * 60
    ).all()
    for cre in cre_record:
        cre.last_used_timestamp = time.time()
        cre.total_bytes_used = 0.0
        cre.is_abuse_reported = False
        session.commit()


@app.route('/credential', methods=['PUT'])
def abuse_report():
    credential_id = request.json.get('credential_id')
    if credential_id:
        abused_credential_obj: Credential = session.query(Credential).filter(
            Credential.id == credential_id
        ).first()
        if abused_credential_obj:
            abused_credential_obj.is_abuse_reported = True
            abused_credential_obj.last_used_timestamp = int(time.time())
            session.commit()
            return {'code': 3221, 'message': 'Ok'}
        abort(400, f"ID {credential_id} not found")
    abort(400, "credential_id not found")


@app.route('/credential', methods=['GET'])
def get_credential():
    restart_credential()
    is_check = request.args.get('is_check')
    filter_type = request.args.get('filter_type')
    total_upload_gb = request.args.get('total_upload_gb')
    if not filter_type:
        if total_upload_gb:
            cre_record: Credential = session.query(Credential).filter(
                and_(
                    Credential.total_bytes_used < 700.0,
                    Credential.is_abuse_reported == 0
                )).order_by(Credential.last_used_timestamp).first()
            if cre_record:
                if not is_check:
                    cre_record.total_bytes_used += float(total_upload_gb)
                    if cre_record.total_bytes_used >= 700:
                        cre_record.last_used_timestamp = int(time.time())
                    session.commit()
                return {'code': 3221, 'message': cre_record.to_json()}
            else:
                abort(404)
        abort(404, 'Please tell use how many byte you will use by param total_upload_gb')
    else:
        cre_record: Credential = session.query(Credential).all()
        if cre_record:
            return {'code': 3221, 'message': [x.to_json() for x in cre_record]}
        else:
            abort(404)


@app.route('/credential', methods=['POST'])
def post_credential():
    if request.is_json:
        rclone_token = request.json.get('rclone_token')
        client_id = request.json.get('client_id')
        client_secret = request.json.get('client_secret')
        if rclone_token:
            is_exist = session.query(Credential).filter(
                Credential.rclone_token == json.dumps(rclone_token)).first()
            if not is_exist:
                try:
                    new_credential = Credential(
                        rclone_token=json.dumps(rclone_token),
                        client_id=client_id,
                        client_secret=client_secret
                    )
                    session.add(new_credential)
                    session.commit()
                except sqlalchemy.exc.PendingRollbackError:
                    session.rollback()
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
