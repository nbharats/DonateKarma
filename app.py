from flask import Flask,render_template,request,url_for,session

app=Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return 'home page'

@app.route('/adminregister')
def adminregister():
    return 'adminregister'

@app.route('/adminlogin')
def adminlogin():
    return 'adminlogin'

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