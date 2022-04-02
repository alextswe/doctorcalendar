from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import auto_field
from dateutil import parser
from datetime import datetime
from sqlalchemy import func

import requests, os, time

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
	 os.path.join(basedir, 'db.sqlite3')

db = SQLAlchemy(app)
ma = Marshmallow(app)

class DoctorModel(db.Model):
    doctor_id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

class DoctorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DoctorModel

class AppointmentModel(db.Model):
    appointment_id = db.Column(db.Integer, primary_key = True)
    appointment_date_time = db.Column(db.DateTime)
    patient_first_name = db.Column(db.String(255))
    patient_last_name = db.Column(db.String(255))
    patient_kind = db.Column(db.String(255))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_model.doctor_id'), nullable = False)

    def __init__(self, patient_first_name, patient_last_name, appointment_date_time, patient_kind, doctor_id):
        self.patient_first_name = patient_first_name
        self.patient_last_name = patient_last_name
        self.appointment_date_time = appointment_date_time
        self.patient_kind = patient_kind
        self.doctor_id = doctor_id

class AppointmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AppointmentModel

db.create_all()

doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many = True)

appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many = True)

@app.route('/doctors/', methods=['GET'])
def get_doctors():
    all_doctors = DoctorModel.query.all()
    return jsonify(doctors_schema.dump(all_doctors))

@app.route('/doctors/<int:doctor_id>/', methods=['GET'])
def get_doctor_all_appointments(doctor_id):
    all_appointments = AppointmentModel.query.filter(AppointmentModel.doctor_id == doctor_id)
    return jsonify(appointments_schema.dump(all_appointments))

@app.route('/doctors/<int:doctor_id>/<string:date>/', methods=['GET'])
def get_doctor_appointments(doctor_id, date): 
    appointment_date = datetime.strptime(date, "%Y-%m-%d")
    appointment_date = appointment_date.date()
    appointments = AppointmentModel.query.filter(func.date(AppointmentModel.appointment_date_time) == appointment_date, AppointmentModel.doctor_id == doctor_id)
    return jsonify(appointments_schema.dump(appointments))

@app.route('/doctors/', methods=['POST'])
def create_doctor():
    request_json = request.get_json()
    firstname = request_json.get('firstname')
    lastname = request_json.get('lastname')
    doctor = DoctorModel(firstname,lastname)

    db.session.add(doctor)
    db.session.commit()

    return doctor_schema.jsonify(doctor)

@app.route('/doctors/<int:doctor_id>/', methods=['DELETE'])
def delete_doctor(doctor_id):
    doctor = DoctorModel.query.get(doctor_id)

    db.session.delete(doctor)
    db.session.commit()

    return doctor_schema.jsonify(doctor)

@app.route('/doctors/<int:doctor_id>/', methods=['POST'])
def create_appointment(doctor_id):
    request_json = request.get_json()
    first_name = request_json.get('firstname')
    last_name = request_json.get('lastname')
    date_time = request_json.get('datetime')
    date_time = parser.parse(date_time)
    if date_time.minute % 15 != 0:
        return {"Error": "Valid appointment times are only at 15 minute intervals."}, 400
    kind = request_json.get('kind')

    #Check if doctor already has 3 appointments at the given time.
    appointment_count = AppointmentModel.query.filter(AppointmentModel.appointment_date_time == date_time, AppointmentModel.doctor_id == doctor_id).count()
    if appointment_count > 2:
        return {"Error": "3 appointments have already been scheduled for this doctor at this time."}, 400
    appointment = AppointmentModel(first_name, last_name, date_time, kind, doctor_id)
    db.session.add(appointment)
    db.session.commit()

    return appointment_schema.jsonify(appointment)

@app.route('/doctors/<int:doctor_id>/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(doctor_id, appointment_id):
    appointment = AppointmentModel.query.get(appointment_id)

    db.session.delete(appointment_id)
    db.session.commit()
    
    return appointment_schema.jsonify(appointment)

if __name__ == "__main__":
    app.run(debug=True)