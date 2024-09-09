from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# SQLiteデータベースの設定
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "ip_management.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False, unique=True)
    hostname = db.Column(db.String(255), nullable=True)
    purpose = db.Column(db.String(255), nullable=True)
    device_type = db.Column(db.String(255), nullable=True)
    admin = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Boolean, nullable=True)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(255), nullable=False)


def ipUpdate(ip: IPAddress, new_ip: IPAddress):
    ip.ip = new_ip.ip
    ip.hostname = new_ip.hostname
    ip.purpose = new_ip.purpose
    ip.device_type = new_ip.device_type
    ip.admin = new_ip.admin


# データベースの初期化
with app.app_context():
    db.create_all()


@app.route("/api/ip-addresses", methods=["POST"])
def add_ip_address():
    data = request.get_json()
    new_ip = IPAddress(
        ip=data["ip"],
        hostname=data["hostname"],
        purpose=data["purpose"],
        device_type=data["device_type"],
        admin=data["admin"],
    )
    db.session.add(new_ip)
    db.session.commit()
    return jsonify({"message": "IP address added successfully", "data": data}), 201


@app.route("/api/ip-addresses", methods=["PUT"])
def change_ip_address():
    data = request.get_json()
    new_ip = IPAddress(
        ip=data["ip"],
        hostname=data["hostname"],
        purpose=data["purpose"],
        device_type=data["device_type"],
        admin=data["admin"],
    )
    ip = db.session.query(IPAddress).where(IPAddress.ip == new_ip.ip).first()
    if ip:
        ipUpdate(ip, new_ip)
        db.session.commit()
        return (
            jsonify({"message": "IP address changed successfully", "data": data}),
            201,
        )
    else:
        return jsonify({"message": "IP not found", "data": data}), 404


@app.route("/api/ip-addresses", methods=["GET"])
def get_ip_addresses():
    ip_addresses = IPAddress.query.all()
    result = [
        {
            "id": ip.id,
            "ip": ip.ip,
            "hostname": ip.hostname,
            "purpose": ip.purpose,
            "device_type": ip.device_type,
            "admin": ip.admin,
            "status": ip.status,
        }
        for ip in ip_addresses
    ]
    return jsonify(result)


@app.route("/api/ip-addresses", methods=["DELETE"])
def delete_ip_address():
    data = request.get_json()
    ipId = data["id"]

    if (db.session.get(IPAddress, ipId)) is None:
        return jsonify({"message": "IP address not found"}), 404
    db.session.query(IPAddress).filter(IPAddress.id == ipId).delete()
    db.session.commit()
    return jsonify({"message": "IP address deleted successfully"}), 200


@app.route("/api/admins", methods=["GET"])
def get_admins():
    admins = Admin.query.all()
    result = [
        {"id": admin.id, "name": admin.name, "grade": admin.grade} for admin in admins
    ]
    return jsonify(result)


@app.route("/api/zabbix", methods=["POST"])
def updateState():
    data = request.get_json()
    pingLists = data["ping"]
    ipAddresses = IPAddress.query.all()
    for ipAddress in ipAddresses:
        if ipAddress.ip in pingLists:
            ipAddress.status = True
            pingLists.remove(ipAddress.ip)
        else:
            ipAddress.status = False

    for aliveIp in pingLists:
        new_ip = IPAddress(ip=aliveIp, status=True)
        db.session.add(new_ip)
    db.session.commit()
    return (
        jsonify({"message": "Machine state changed successfully", "data": data}),
        201,
    )


@app.route("/")
def index():
    return send_from_directory("dist", "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("dist", path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # FlaskアプリをWaitressで稼働させる
