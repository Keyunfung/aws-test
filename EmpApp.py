from tokenize import Double
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import datetime as dt

app=Flask(__name__,template_folder='template')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'leave'

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about/", methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route("/employee/", methods=['GET','POST'])
def employee():
    return render_template('employee.html')

@app.route("/attendance/", methods=['GET','POST'])
def attendance():
    return render_template('attendance.html')

@app.route("/leave/", methods=['GET','POST'])
def leave():
    return render_template('leave.html')

@app.route("/leave/output", methods=['GET','POST'])
def leaveoutput():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        startdate = dt.datetime.strptime(request.form['startdate'], '%Y-%m-%d').strftime(format="%d-%B-%Y")
        enddate = dt.datetime.strptime(request.form['enddate'], '%Y-%m-%d').strftime(format="%d-%B-%Y")
        description = request.form['description']
        status = ""
        b4format_statusdate = datetime.now()
        b4format_statustime = datetime.now()
        statusdate = b4format_statusdate.strftime("%d-%B-%Y")
        statustime = b4format_statustime.strftime("%H:%M:%S")
        insert_sql = "INSERT INTO leave VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        try:
            cursor.execute(insert_sql, (emp_id, startdate, enddate, description, status, statusdate, statustime))
            db_conn.commit()
        finally:
            cursor.close()
            
        return render_template('payroll-output.html', title = 'Employee Leave Added Successfully', emp_id = emp_id)
    else:
        emp_id = request.form['emp_id']
        startdate = request.form['startdate']
        enddate = request.form['enddate']
        description = request.form['description']
        status = request.form['status']
        b4format_statusdate = datetime.now()
        b4format_statustime = datetime.now()
        statusdate = b4format_statusdate.strftime("%d-%B-%Y")
        statustime = b4format_statustime.strftime("%H:%M:%S")
        
        return render_template('leave-output.html', title = 'Employee Leave Added Unsuccessfully')

@app.route("/leave/statusupdate", methods=['GET','POST'])
def leavestatus():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        status = request.form['status']
        b4format_statusdate = datetime.now()
        b4format_statustime = datetime.now()
        statusdate = b4format_statusdate.strftime("%d-%B-%Y")
        statustime = b4format_statustime.strftime("%H:%M:%S")
        
        cursor = db_conn.cursor()
        update_sql = "UPDATE leave SET status = (%(status)s) AND statusdate = (%(statusdate)s) AND statustime = (%(statustime)s) WHERE emp_id = (%(emp_id)s)"
        try:
            cursor.execute(select_sql, (emp_id, status, statusdate, statustime))
            db_conn.commit()
        finally:
            cursor.close()
            
        return render_template('leave.html')
    else:
        emp_id = request.form['emp_id']
        status = request.form['status']
        
        return render_template('leave.html')

#################### PAYROLL ####################
@app.route("/payroll/", methods=['GET','POST'])
def payroll():
    return render_template('payroll.html')

@app.route("/payroll/addsalary", methods=['GET','POST'])
def addsalary():
    return render_template('calculate-payroll.html')

@app.route("/payroll/updatesalary", methods=['GET','POST'])
def updatesalary():
    return render_template('update-payroll.html')

@app.route("/payroll/updatesalary/info", methods=['GET','POST'])
def updatesalaryinfo():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        payroll_month = dt.datetime.strptime(request.form['payroll_month'],'%Y-%m').strftime(format="%B %Y")
        
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM payroll where emp_id = (%s) and payroll_month = (%s)"
        try:
            cursor.execute(select_sql, (emp_id, payroll_month))
        finally:
            cursor.close()

        return render_template('update-salary-payroll.html')
    else:
        emp_id = request.args.get('emp_id')
        payroll_month = request.args.get('payroll_month')
        return render_template('update-salary-payroll.html')

@app.route("/payroll/addsalary/results", methods=['GET','POST'])
def salaryresult():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        work_day = float(request.form['work_day'])
        hour_rate = float(request.form['hour_rate'])  
        hour_work = float(request.form['hour_work'])
        payroll_month = dt.datetime.strptime(request.form['payroll_month'],'%Y-%m').strftime(format="%B %Y")
        monthly_salary = work_day * hour_work * hour_rate
        insert_sql = "INSERT INTO payroll VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        try:
            cursor.execute(insert_sql, (emp_id, work_day, hour_rate, hour_work, payroll_month, monthly_salary))
            db_conn.commit()
        finally:
            cursor.close()

        print("all modification done...")
        return render_template('payroll-output.html', title = 'New Payroll added successfully', emp_id = emp_id,
        payroll_month = payroll_month, monthly_salary = monthly_salary)
    else:
        emp_id = request.args.get('emp_id')
        work_day = request.args.get('work_day')
        hour_rate = request.args.get('hour_rate')
        hour_work = request.args.get('hour_work')
        payroll_month = request.args.get('payroll_month')
        return render_template('payroll-output.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
