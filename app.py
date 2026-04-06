from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_session import Session
import mysql.connector
from generateotp import generateotp
from amail import send_mail
from secrecttoken import encrypt,decrypt
import bcrypt
import razorpay
from math import floor

app=Flask(__name__)
app.secret_key='donatekarma'

app.config['SESSION_TYPE']='filesystem'
Session(app)

database=mysql.connector.connect(user='root',host='localhost',password='Vasudev@8',database='donatekarma')
# database=mysql.connector.connect(user='root',host='localhost',password='bikki',database='donatekarma')

client = razorpay.Client(auth=("rzp_test_SHy3zlzWZXNg3W", "B67PBLrrvi1BP38vgyIEdOHg"))

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
    
    print(session)
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
                        cursor.execute('insert into admindata(admin_id,admin_email,admin_name,admin_phno,admin_password) values(uuid_to_bin(uuid()),%s,%s,%s,%s)',[data['adminmail'],data['adminname'].capitalize(),data['adminphone'],hash_pass])
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
        adminname=request.form['adminname'].capitalize()
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

@app.route('/campdelte/<campid>')
def campdelete(campid):
    if not session.get('admin'):
        flash('Please login to proceed')
        return redirect(url_for('adminlogin'))
    try:
        cursor=database.cursor(buffered=True)
        cursor.execute('delete from campaign where id=%s',[campid])
        database.commit()
        cursor.close()
    except Exception as e:
        print(e)
        flash('Could not delete Campaign')
        return redirect(url_for('campaign'))
    else:
        flash('Campaign deleted successfully')
        return redirect(url_for('campaign'))
    
@app.route('/donations')
def donations():
    if 'admin' not in session: 
        return redirect(url_for('adminlogin'))
    try:
        cursor = database.cursor(buffered=True)
        cursor.execute("""
            SELECT d.*, c.name as campaign_name, n.name as ngo_name 
            FROM donations d 
            LEFT JOIN campaigns c ON d.campaign_id=c.id 
            LEFT JOIN ngos n ON d.ngo_id=n.id
            ORDER BY d.created_at DESC
        """)
        donations = cursor.fetchall()
        print(donations[0])
        cursor.close()
    except Exception as e:
        print(e)
        flash('Could not fetch details')
        return redirect(url_for('admindashboard'))
    return render_template('donations.html', donations=donations)

@app.route('/reports')
def reports():
    if not session.get('admin'):
        return redirect(url_for('adminlogin'))
    try:
        cursor=database.cursor(buffered=True)
        cursor.execute('select n.name,sum(d.amount) as total,count(d.ngo_id) from ngos n left join donations d on n.id=d.ngo_id where d.status="paid" group by n.id order by total desc')
        ngos=cursor.fetchall()
        for i in range(len(ngos)):
            print(i,ngos[i])
        print(ngos)
        
        cursor.execute('select name,raised_amount,goal_amount from campaigns')
        campaigns=cursor.fetchall()
        for i in range(len(campaigns)):
            print(i,campaigns[i])
        print(campaigns)
    except Exception as e:
        print(e)
        flash('Couldnot fetch data')
        return redirect(url_for('admindashboard'))
    return render_template('reports.html',ngo_reports=ngos,campaign_reports=campaigns)

@app.route('/userregister',methods=['GET','POST'])
def userregister():
    if request.method=='POST':
        usermail=request.form['useremail']
        username=request.form['username']
        phone=request.form['userphone'].split('-')
        userphone=''.join(phone)
        userpassword=request.form['userpassword']
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('select count(*) from users where email=%s',[usermail])
            mailcount=cursor.fetchone()[0] 
        except Exception as e:
            print(e)
            flash('Could not examine deatils')
            return redirect(url_for('userregister'))
        else:
            if not mailcount:
                otp=generateotp()
                userdata={
                    'usermail':usermail,
                    'username':username,
                    'userphone':userphone,
                    'userpassword':userpassword,
                    'otp':otp
                }
                subject='Donate Karma registration email verification'
                body=f'Verification Otp {otp}'
                send_mail(subject=subject,body=body,to=usermail)
                flash('OTP sent to given mail')
                return redirect(url_for('userotpverify',ata=encrypt(userdata)))
            else:
                flash('User already exists')
                return redirect(url_for('userregister'))
    return render_template('user_registration.html')

@app.route('/userotpverify/<ata>',methods=['GET',"POST"])
def userotpverify(ata):
    if request.method=='POST':
        try:
            data=decrypt(ata)
        except Exception as e:
            print(e)
            flash('Could not decode data')
            return redirect(url_for('userregister'))
        else:
            if request.method=='POST':
                opt=request.form['otp']
                if data['otp']==opt:
                    hash_pass=bcrypt.hashpw(data['userpassword'].encode('utf-8'),bcrypt.gensalt())
                    try:
                        cursor=database.cursor(buffered=True)
                        cursor.execute('insert into users(id,name,email,phone,password) values(uuid_to_bin(uuid()),%s,%s,%s,%s)',[data['username'].captilize(),data['usermail'],data['userphone'],hash_pass])
                        database.commit()
                        cursor.close()
                        print('data stored')
                    except Exception as e:
                        print(e)
                        flash('Could not store details')
                        return redirect(url_for('userregister'))
                    else:
                        flash('OTP verified successfully')
                        return redirect(url_for('userlogin'))
                else:
                    flash('Invalid OTP')
                    return redirect(url_for('userotpverify'))
    return render_template('otpverify.html')

@app.route('/userlogin',methods=['GET','POST'])
def userlogin():
    if request.method=='POST':
        username=request.form['username'].capitalize()
        userpass=request.form['userpassword']
        # print(username,userpass)
        try:
            cursor=database.cursor(buffered=True)
            # print('before')
            cursor.execute('select password from users where name=%s or email=%s',[username,username])
            loginpass=cursor.fetchone()
            print(loginpass)
            # print('after')
            if loginpass and loginpass[0]:
                passw=loginpass[0]
                if bcrypt.checkpw(userpass.encode('utf-8'),passw):
                    session['user']=username
                    session.setdefault(username, {})
                    # print(username,userpass)
                    return redirect(url_for('index'))
                else:
                    flash('Incorrect Password')
                    return redirect(url_for('userlogin'))
            else:
                flash('Could not fetch password')
                return redirect(url_for('userlogin'))
        except Exception as e:
            print(e)
            flash('Could not fetch details')
            return redirect(url_for('userlogin'))

    return render_template('user_login.html')

@app.route('/userlogout')
def userlogout():
    if not session.get('user'):
        flash('Please login to proceed')
        return redirect(url_for('userlogin'))
    session.pop(session.get('user'))
    session.pop('user',None)
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.route('/campaignlist')
def campaignlist():
    try:
        cursor=database.cursor(buffered=True)
        cursor.execute('select c.*,n.name from campaigns c left join ngos n on c.ngo_id = n.id')
        camps=cursor.fetchall()
        cursor.close()
    except Exception as e :
        print(e)
        flash('Could not retrive details')
        return redirect(url_for('campaignlist'))
    return render_template('campaignlist.html',campaigns=camps)

@app.route('/campaigndetails/<campaignid>',methods=['GET','POST'])
def campaigndetails(campaignid):
    if session.get('user'):
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('select c.*,n.name,n.id from campaigns c left join ngos n on c.ngo_id = n.id where c.id = %s',[campaignid])
            camps=cursor.fetchone()
            cursor.execute('select sum(raised_amount) from campaigns where campaigns.id = %s',[campaignid])
            total=cursor.fetchone()[0]
            # print('total',total/camps[3])
            cursor.execute('select id,email from users where name=%s or email=%s',[session.get('user'), session.get('user')])
            userlog=cursor.fetchone()
            cursor.close()
        except Exception as e :
            print(e)
            flash('campaign Could not retrive details')
            return redirect(url_for('campaigndetails',campaignid=campaignid))
        # print('campaignid',campaignid)
        else:
            if request.method=='POST':
                d_amount=request.form['amount']
                d_name=request.form['donor_name']
                d_email=request.form['donor_email']
                d_phno=request.form['donor_phone']
                # print(d_amount,d_name,d_email,d_phno)

                session[session.get('user')][campaignid]=[d_name,
                                              d_email,
                                              d_phno,
                                              d_amount,campaignid,
                                              camps[10],
                                              userlog[0]
                ]
                ses=session[session.get('user')][campaignid]
                # print(ses[3])
                flash('message sent')
                return redirect(url_for('donation_pay',campaignid=campaignid))
            else:

                return render_template('campaigndetails.html',campaignid=campaignid,campaign=camps, total_raised=total)
    else:
        flash('Please Sign in to Proceed')
        return redirect(url_for('userlogin'))

@app.route('/donation_pay/<campaignid>',methods=['GET','POST'])
def donation_pay(campaignid):
    # print("campaignid",campaignid)
    if session.get('user'):
        try:
            cursor=database.cursor(buffered=True)
            cursor.execute('select name from users where name=%s or email=%s',[session.get('user'), session.get('user')])
            userlog=cursor.fetchone()[0]
            cursor.close()
            ses=session[session.get('user')][campaignid]
            # print(ses)
            amount=int(float(ses[3])+(float(ses[3])*0.2))
            razor_amount=amount*100
            # print(razor_amount)
            order=client.order.create({
                'amount':razor_amount,
                "currency": "INR",
                'receipt':f"{ses[0]}",
                'payment_capture':'1'
            })
            # print(order)
            return render_template('donation_pay.html',campaignid=campaignid,order=order,client=ses)
        except Exception as e :
            print(e)
            flash('donation Could not retrive details',category='danger')
            return redirect(url_for('campaigndetails',campaignid=campaignid))
        
    else:
        flash('Please Sign in to Proceed',category='danger')
        return redirect(url_for('userlogin'))

@app.route('/success_donation/<campaignid>',methods=['POST'])
def success_donation(campaignid):
    try:
        # print(request.form)
        pay_id=request.form['razorpay_payment_id']
        order_id=request.form['razorpay_order_id']
        sign=request.form['razorpay_signature']
        amount=request.form['grand_total']
        print(f"Payment: {pay_id}, Order: {order_id}, Sign: {sign}")
        dic={
            'razorpay_payment_id':pay_id,
            'razorpay_order_id':order_id,
            'razorpay_signature':sign
        }
        payment='paid'
        try:
            client.utility.verify_payment_signature(dic)
        except Exception as e:
            print(e)
            flash('payment verification failed')
            payment='failed'
            return redirect(url_for('index'))
        else:
            donation_data=session.get(session.get('user'))
            print(donation_data,'\n',donation_data.get(campaignid))
            # donation_data=donation_data.get('campaignid')
            # print(donation_data)
            
            try:
                cursor=database.cursor(buffered=True)
                cursor.execute('insert into donations(razorpay_payment_id,razorpay_order_id,razorpay_signature,amount,donor_name,donor_email,donor_phone,campaign_id,status,ngo_id,user_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[pay_id,order_id,sign,donation_data.get(campaignid)[3],donation_data.get(campaignid)[0],donation_data.get(campaignid)[1],donation_data.get(campaignid)[2],donation_data.get(campaignid)[4],payment,donation_data.get(campaignid)[5],donation_data.get(campaignid)[6]])
                database.commit()
                cursor.execute('select raised_amount from campaigns where id=%s',[campaignid])
                raised=cursor.fetchone()[0]
                print(raised,donation_data.get(campaignid)[3])
                raised=float(raised)+float(donation_data.get(campaignid)[3])
                cursor.execute('update campaigns set raised_amount=%s where id=%s',[raised,campaignid])
                database.commit()
                cursor.close()
                print('data stored')
                if session.get(session.get('user')):
                    donation_dat=session[session['user']].pop(campaignid)
                    print(donation_dat)
                    print('session data deleted',session)
                # return redirect(url_for('index'))
            except Exception as e:
                print('exception',e)
                flash('Could not store details')
                return redirect(url_for('index'))
            
            return redirect(url_for('index'))
    except Exception as e:
        print(e)
        app.logger.exception(f'Payment verification failed {e}')
        flash('Payment Failed ')
        return redirect(url_for('index'))

app.run(use_reloader=True,debug=True)
