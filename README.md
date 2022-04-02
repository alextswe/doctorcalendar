1. Run "pip install -r requirements.txt"
2. Run "python3 Doctors.py"

For each HTTP request:
Run these against the localhost address that is set up. My base address was http://127.0.0.1:5000/

1.Send a GET request to /doctors/
2.Send a GET request to /doctors/ with parameters /doctor_id/date/
	ex. GET http://127.0.0.1:5000/doctors/1/2022-04-15/
3.Send a DELETE request to /doctors/ with parameters /doctor_id/
	ex. DELETE http://127.0.0.1:5000/doctors/1/
4.Send a POST request to /doctors/ with parameters /doctor_id/ with a JSON file with the paramaters firstname, lastname, datetime, kind.
	ex. POST http://127.0.0.1:5000/doctors/1/
	{"firstname":"Alex","lastname":"Tran","datetime":"2018-01-02T22:20:00","kind":"New Patient"}

I have also added a POST to /doctors/ requiring a JSON with parameters firstname, lastname to add doctors for testing.
{"firstname":"Doctor","lastname":"Tran"}
