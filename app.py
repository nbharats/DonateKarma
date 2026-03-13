from flask import Flask,render_template,request,url_for,session

app=Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')

@app.route('/adminregister')
def adminregister():
    return render_template('admin_registration.html')

@app.route('/adminlogin')
def adminlogin():
    return render_template('admin_login.html')

@app.route('/admindashboard')
def admindashboard():
    return 'admindashboard'

''' Here goes campaign details like 
    CRUD operations of campaign
    on admin side'''

@app.route('/userregister')
def userregister():
    return 'userregister'

@app.route('/userlogin')
def userlogin():
    return 'userlogin'



app.run(use_reloader=True,debug=True)