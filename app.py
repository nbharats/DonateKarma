from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_session import Session
import mysql.connector
from generateotp import generateotp
from amail import send_mail
from secrecttoken import encrypt,decrypt
import bcrypt

app=Flask(__name__)
app.secret_key='donatekarma'

app.config['SESSION_TYPE']='filesystem'
Session(app)

# database=mysql.connector.connect(user='root',host='localhost',password='Vasudev@8',database='donatekarma')
database=mysql.connector.connect(user='root',host='localhost',password='bikki',database='donatekarma')


@app.route('/')
@app.route('/index')
def index():
    try:
        cursor=database.cursor(buffered=True)
        cursor.execute('select * from campaigns')
        camps=cursor.fetchall()
        cursor.close()
    except Exception as e :
        print(e)
        flash('Could not retrive details')
        return redirect(url_for('index'))
    return render_template('index.html',campaigns=camps)

@app.route('/adminregister',methods=['GET','POST'])
def adminregister():

    if request.method=='POST':
        adminmail=request.form['adminemail']
        adminname=request.form['adminname']
        phone=request.form['adminphone'].split('-')
        adminphone=''.join(phone)
        adminpassword=request.form['adminpassword']
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('select count(*) from admindata where admin_email=%s',[adminmail])
            mailcount=cursor.fetchone()[0] 
        except Exception as e:
            print(e)
            flash('Could not examine deatils')
            return redirect(url_for('adminregister'))
        else:
            if not mailcount:
                otp=generateotp()
                admindata={
                    'adminmail':adminmail,
                    'adminname':adminname,
                    'adminphone':adminphone,
                    'adminpassword':adminpassword,
                    'otp':otp
                }
                subject='Donate Karma registration email verification'
                body=f'Verification Otp {otp}'
                send_mail(subject=subject,body=body,to=adminmail)
                flash('OTP sent to given mail')
                return redirect(url_for('otpverify',ata=encrypt(admindata)))
            else:
                flash('User already exists')
                return redirect(url_for('adminregister'))
    return render_template('admin_registration.html')

@app.route('/otpverify/<ata>',methods=['GET',"POST"])
def otpverify(ata):
    if request.method=='POST':
        try:
            data=decrypt(ata)
        except Exception as e:
            print(e)
            flash('Could not decode data')
            return redirect(url_for('adminregister'))
        else:
            if request.method=='POST':
                opt=request.form['otp']
                if data['otp']==opt:
                    hash_pass=bcrypt.hashpw(data['adminpassword'].encode('utf-8'),bcrypt.gensalt())
                    try:
                        cursor=database.cursor(buffered=True)
                        cursor.execute('insert into admindata(admin_id,admin_email,admin_name,admin_phno,admin_password) values(uuid_to_bin(uuid()),%s,%s,%s,%s)',[data['adminmail'],data['adminname'],data['adminphone'],hash_pass])
                        database.commit()
                        cursor.close()
                    except Exception as e:
                        print(e)
                        flash('Could not store details')
                        return redirect(url_for('adminregister'))
                    else:
                        flash('OTP verified successfully')
                        return redirect(url_for('adminlogin'))
                else:
                    flash('Invalid OTP')
                    return redirect(url_for('otpverify'))
    return render_template('otpverify.html')

@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        adminname=request.form['adminname']
        adminpass=request.form['adminpassword']
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('select admin_password from admindata where admin_name=%s or admin_email=%s',[adminname,adminname])
            loginpass=cursor.fetchone()[0]
            if loginpass:
                if bcrypt.checkpw(adminpass.encode('utf-8'),loginpass):
                    session['admin']=adminname
                    return redirect(url_for('admindashboard'))
                else:
                    flash('Incorrect Password')
                    return redirect(url_for('adminlogin'))
            else:
                flash('Could not fetch password')
                return redirect(url_for('adminlogin'))
        except Exception as e:
            print(e)
            flash('Could not fetch details')
            return redirect(url_for('adminlogin'))

    return render_template('admin_login.html')

@app.route('/adminlogout')
def adminlogout():
    if not session.get('admin'):
        flash('Please login to proceed')
        return redirect(url_for('adminlogin'))
    session.pop('admin',None)
    
    flash('Logged out successfully')
    return redirect(url_for('adminlogin'))

@app.route('/deleteacc')
def deleteacc():
    if not session.get('admin'):
        flash('Please login to proceed')
        return redirect(url_for('adminlogin'))
    
    try:
        cursor=database.cursor(buffered=True)
        cursor.execute('delete from admindata where admin_name=%s or admin_email=%s',[session.get('admin'),session.get('admin')])
        database.commit()
        cursor.close()
    except Exception as e :
        print(e)
        flash('Could not delete account')
        return redirect(url_for('admindashboard'))
    else:
        session.pop('admin',None)
        flash('Account deleted succesfully')
        return redirect(url_for('adminregister'))

@app.route('/admindashboard')
def admindashboard():
    return render_template('admindashboard.html')

''' Here goes campaign details like 
    CRUD operations of campaign
    on admin side'''

@app.route('/ngos',methods=['GET','POST'])
def ngos():
    if not session.get('admin'):
        flash('Please login to proceed')
        return redirect(url_for('adminlogin'))

    if request.method=='POST':
        ngoname=request.form['name']
        ngoacc=request.form['account']
        ngodesc=request.form['description']

        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('insert into ngos(name,description,bank_account) values(%s,%s,%s)',[ngoname,ngodesc,ngoacc])
            database.commit()
            cursor.close()
        except Exception as e :
            print(e)
            flash('Could not store details')
            return redirect(url_for('ngos'))
        else:
            flash('details stored successfully')
            return redirect(url_for('ngos'))
    else:
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('select * from ngos')
            ngodata=cursor.fetchall()
            print(ngodata)
            cursor.close()
        except Exception as e :
            print(e)
            flash('Could not retrive details')
            return redirect(url_for('ngos'))
        # else:
        #     flash('details retrived successfully')
        
        return render_template('ngos.html',ngos=ngodata)

@app.route('/ngodelete/<ngoid>')
def ngodelete(ngoid):
    if not session.get('admin'):
        flash('Please login to proceed')
        return redirect(url_for('adminlogin'))
    
    try:
            cursor=database.cursor(buffered=True)
            cursor.execute('delete from ngos where id=%s',[ngoid])
            database.commit()
            cursor.close()
    except Exception as e :
        print(e)
        flash('Could not delete details')
        return redirect(url_for('ngos'))
    else:
        flash('details deleted successfully')
    return redirect(url_for('ngos'))

@app.route('/campaign',methods=['GET','POST'])
def campaign():
    if not session.get('admin'):
        flash('Please login to proceed')
        return redirect(url_for('adminlogin'))
    
    if request.method=='POST':
        name=request.form['name']
        desc=request.form['description']
        g_amount=request.form['goal_amount']
        ngoid=request.form['ngo_id']
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('insert into campaigns(name,description,goal_amount,ngo_id) values(%s,%s,%s,%s)',[name,desc,g_amount,ngoid])
            database.commit()
            cursor.close()
        except Exception as e :
            print(e)
            flash('Could not store details')
            return redirect(url_for('campaign'))
            
        else:
            flash('Details stored successfully')
            return redirect(url_for('campaign'))
        
    else:
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('select id,name from ngos')
            ngo=cursor.fetchall()
            cursor.execute('select c.*,n.name from campaigns c left join ngos n on c.ngo_id=n.id order by created_at')
            camp=cursor.fetchall()
            cursor.close()
        except Exception as e :
            print(e)
            flash('Could not store details')
            return redirect(url_for('campaign'))
            
        else:
            flash('Details retrived successfully')
    return render_template('campaign.html',ngos=ngo,campaigns=camp)

@app.route('/donations')
def donations():
    return render_template('donations.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/userregister')
def userregister():
    return 'userregister'

@app.route('/userlogin')
def userlogin():
    return 'userlogin'

@app.route('/campaignlist')
def campaignlist():
    return render_template('campaignlist.html')

@app.route('/campaigndetails')
def campaigndetails():
    return render_template('campaigndetails.html')

app.run(use_reloader=True,debug=True)
