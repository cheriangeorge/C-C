# from flask import Flask,render_template,request,redirect

# from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from model import *
from validate import *
# from rest_api import *
# from backend_jobs import *
# from main import *
# from frontend import *
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore,auth_required, login_required, current_user,roles_required
from flask_security.forms import RegisterForm, LoginForm
from flask_security.utils import login_user
from sqlalchemy.ext.mutable import MutableList
from wtforms import StringField
from wtforms.validators import DataRequired
# from flask_user import user_registered
from flask_security.signals import user_registered,user_authenticated


@user_registered.connect_via(app)
# def _after_user_registered_hook(sender, user, user_invite, **extra):
def _after_user_registered_hook(sender,user, **extra):

    role = Role.query.filter_by(name='student').one()
    user.roles.append(role)
    # app.user_manager.db_adapter.commit()
    db.session.commit()

# @user_authenticated.connect_via(app)
# def _after_user_authenticated_hook(sender,user, **extra):
#   print("HERE HERE HERE")
#   for r in user.roles:
#     print(r.name)
#     if r.name == 'Admin':
#       print(url_for('admin_dashboard'))
#       return redirect(url_for('admin_dashboard'))
#     elif r.name == 'student':
#       print(url_for('student_dashboard'))
#       return redirect(url_for('student_dashboard'))

################
# class ExtendedRegisterForm(RegisterForm):
#     username = StringField('Userame', [DataRequired()])

# security = Security(app, user_datastore,
#          register_form=ExtendedRegisterForm)
################
# @app.route('/')
# def home():
#     return render_template('index.html')

#################
# from model import Security, User, user_datastore
# from forms import logform, signupform

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=RegisterForm, login_form=LoginForm)

# security = Security(app, user_datastore, register_form=signupform,  login_form=logform, confirm_register_form=signupform)

# db.create_all()
# db.session.commit()

@app.before_first_request
def create_db():
  db.create_all()
  if not user_datastore.find_role('Admin'):
    admin_role = user_datastore.create_role(name="Admin",description="Admin related role")
    db.session.commit()
  if not user_datastore.find_user(email="admin@demo.com"):
    admin_user = user_datastore.create_user(email="admin@demo.com",password=hash_password("pass123#"))
    user_datastore.add_role_to_user(admin_user, admin_role)
    db.session.commit()
  if not user_datastore.find_role('student'):
    student_role= user_datastore.create_role(name="student",description="Student related role")
    db.session.commit()
  if not user_datastore.find_user(email="student1@demo.com"):
    student_user = user_datastore.create_user(email="student1@demo.com",password=hash_password("pass123#"))
    user_datastore.add_role_to_user(student_user, student_role)
    db.session.commit()


@app.route('/')
@auth_required()
# @roles_required('Admin')
def home():
    print("Home")
    # log = logform(csrf_enabled=False)
    # flash("HELLO.")
    # return render_template("index.html")
    roles = current_user.roles
    for role in roles:
      if role.name=='Admin':
        return redirect(url_for('admin_content'))
      elif role.name=='student':
        return redirect(url_for('student_content'))

@app.route('/admin/content', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def admin_content():
  print("Admin_Dashboard")
  if request.method=="POST":
    submit = request.form.get('submit',None)
    if submit.startswith("delete"):
      content_id=submit.split('_')[-1]
      User_Content_Rel.query.filter_by(content_id=content_id).delete()
      Tag_Content_Rel.query.filter_by(content_id=content_id).delete()
      Content.query.filter_by(id=content_id).delete()
      db.session.commit()
      return redirect('/admin/content')
    elif submit.startswith("edit"):
      tags = Tag.query.all()
      tag_list=[i.name for i in tags]
      content_id=submit.split('_')[-1]
      contentx = Content.query.filter_by(id=content_id).first()
      if contentx:
        contentxx = get_content_obj(contentx,True)
        return render_template('admin_content_edit.html',content=contentxx,tag_list=tag_list)
  elif request.method=="GET":
    content = Content.query.all()
    content_list=[]
    for i in content:
      content_list.append(get_content_obj(i,False))
    # return render_template("admin_tags.html",tag_list=tags)
    return render_template("admin_content.html",contents=content_list)

@app.route('/admin/content_create', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def admin_content_create():
  tags = Tag.query.all()
  tag_list=[i.name for i in tags]
  if request.method=="POST":
    from datetime import date
    today = date.today()
    # print("Admin Content Create POST")
    title = request.form.get('title',None)
    body = request.form.get('body',None)
    selected_tags=request.form.get('tags',None)
    isanon=request.form.get('anon_check',None)
    # print(title)
    # print(body)
    # print(selected_tags)
    # print("Is anon",isanon)
    # print(check_tags(selected_tags))
    message = ""
    tag_ids=[]
    if len(selected_tags)>0:
      message,tag_ids = check_tags(selected_tags)
    message2 = validate_text(title,100,"Title")
    message3 = validate_text(body,2000,"Content Body")
    if len(message)>0:
      message+=", "
    if len(message2)>0:
      message2+=", "
    if len(message3)>0:
      message3+=" "
    message+=message2+message3
    is_anon = False
    if isanon=='anon':
      is_anon = True
    print("Message Length : ",len(message)," Message: ",message)
    if len(message)==0:
      Contentx=Content(title=title,content_body=body,created_at=today,is_anon=is_anon,user_id=current_user.id)
      db.session.add(Contentx)
      db.session.flush()
      # print(Contentx.id)
      Userrelx = User_Content_Rel(content_id=Contentx.id,user_id=current_user.id)
      db.session.add(Userrelx)
      for i in tag_ids:
        Tagrelx = Tag_Content_Rel(tag_id=i,content_id=Contentx.id)
        db.session.add(Tagrelx)
      db.session.commit()
      return redirect('/admin/content')
    else:
      #Invalid input
      return render_template("admin_content_create.html",content=dict(title=title,body=body,tags=selected_tags),tag_list=tag_list,message=message)
  elif request.method=="GET":
    # print("Admin_Content Create")
    
    return render_template("admin_content_create.html",tag_list=tag_list)

@app.route('/admin/content_edit', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def admin_content_edit():
  tags = Tag.query.all()
  tag_list=[i.name for i in tags]
  if request.method=="POST":
    from datetime import date
    # today = date.today()
    # print("Admin Content Create POST")
    id = request.form.get('contentid',None)
    title = request.form.get('title',None)
    body = request.form.get('body',None)
    selected_tags=request.form.get('tags',None)
    isanon=request.form.get('anon_check',None)
    print(request.form)
    # print(title)
    # print(body)
    # print(selected_tags)
    # print("Is anon",isanon)
    # print(check_tags(selected_tags))
    message = ""
    tag_ids=[]
    if len(selected_tags)>0:
      message,tag_ids = check_tags(selected_tags)
    message2 = validate_text(title,100,"Title")
    message3 = validate_text(body,2000,"Content Body")
    if len(message)>0:
      message+=", "
    if len(message2)>0:
      message2+=", "
    if len(message3)>0:
      message3+=" "
    message+=message2+message3
    is_anon = False
    if isanon=='anon':
      is_anon = True
    print("Message Length : ",len(message)," Message: ",message)
    if len(message)==0:
      Contentx=Content.query.filter_by(id=id).first()
      Contentx.title = title
      Contentx.content_body = body
      Contentx.is_anon = is_anon
      Tag_Content_Rel.query.filter_by(content_id=id).delete()
      # print(Contentx.id)
      # Userrelx = User_Content_Rel(content_id=Contentx.id,user_id=current_user.id)
      # db.session.add(Userrelx)
      for i in tag_ids:
        Tagrelx = Tag_Content_Rel(tag_id=i,content_id=Contentx.id)
        db.session.add(Tagrelx)
      db.session.commit()
      return redirect('/admin/content')
    else:
      #Invalid input
      return render_template("admin_content_edit.html",content=dict(id=id,title=title,body=body,tags=selected_tags),tag_list=tag_list,message=message)
  elif request.method=="GET":
    # print("Admin_Content Create")
    return redirect('/admin/content')

@app.route('/admin/tags', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def admin_tags():
  print("Admin_Tags")
  if request.method=="POST":
    submit = request.form.get('submit',None)
    if submit.startswith("delete"):
      tag_id=submit.split('_')[-1]
      Tag_Question_Rel.query.filter_by(tag_id=tag_id).delete()
      Tag_Assessment_Rel.query.filter_by(tag_id=tag_id).delete()
      Tag_Content_Rel.query.filter_by(tag_id=tag_id).delete()
      Tag.query.filter_by(id=tag_id).delete()
      db.session.commit()
      return redirect('/admin/tags')
    elif submit.startswith("edit"):
      tag_id=submit.split('_')[-1]
      tagx = Tag.query.filter_by(id=tag_id).first()
      if tagx:
        return render_template('admin_tag_edit.html',tag=tagx)
  elif request.method=="GET":
    tags = Tag.query.all()
    return render_template("admin_tags.html",tag_list=tags)

@app.route('/admin/create_tag', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def admin_tag_create():

  print("Admin_Tags")
  if request.method=="POST":
    tagname=request.form.get('tagname',None)
    tagname=tagname.lower()
    validation_message= tag_validation_error(tagname)
    print(validation_message)
    if len(validation_message)>0:
      return render_template("admin_tag_create.html",message=validation_message)
    else:
      tagx=Tag(name=tagname,user_id=current_user.id)
      db.session.add(tagx)
      db.session.commit()
      ##########
      return render_template("admin_tag_create.html",message="Tag Added Successfully")
  elif request.method=="GET":
    return render_template("admin_tag_create.html")



@app.route('/admin/edit_tag', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def admin_tag_edit():
  print("Admin_Tags")
  if request.method=="POST":
    ##########
    tagid=request.form.get('tagid',None)
    tagname=request.form.get('tagname',None)
    tagname=tagname.lower()
    validation_message = tag_validation_error(tagname)
    if len(validation_message)>0:
      return render_template("admin_tag_edit.html",tag=dict(id=tagid,name=tagname),message=validation_message)

    tagx=Tag.query.filter_by(id=int(tagid)).first()
    if tagx:
      tagx.name = tagname
      db.session.commit()
      return redirect('/admin/tags')
    else:
      return redirect('/admin/tags')
    ##########
    return render_template("admin_tag_create.html",message="Tag Added Successfully")
  elif request.method=="GET":
    return redirect('/admin/tags')

@app.route('/admin/rest-api', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def rest_api():
  return render_template("swagger.html",username='swagger')

@app.route('/admin/question_create', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def admin_question_create():
  tags = Tag.query.all()
  tag_list=[i.name for i in tags]
  print("Admin Question Create")
  return render_template("admin_question_create.html",tag_list=tag_list)

@app.route('/student/content', methods=['GET', 'POST'])
@auth_required()
@roles_required('student')
def student_content():
  print("Student_Dashboard")
  # log = logform(csrf_enabled=False)
  # flash("HELLO.")
  content = Content.query.all()
  content_list=[]
  for i in content:
    cont_x=get_content_obj(i,True)
    if cont_x['is_anon']==True:
      cont_x['author'] = "Anonymous"
    cont_x['body'] = "<p>" + cont_x['body'].replace("\n", "<br>") + "</p>"
    cont_x['tags'] = cont_x['tags'].split(',')
    content_list.append(cont_x)
  # print(content_list)
  return render_template("student_content.html",contents=content_list)

# @app.route('/login')
# def login():
#     print("/LOGIN REQUESTED")
#     # form = logform(csrf_enabled=False)
#     return render_template("login.html", form=LoginForm, security=security)


# #not sure if I need this function at all
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     print ("/SIGNUP REQUESTED")
#     form = signupform(csrf_enabled=False)
#     # form = RegisterForm()

#     if request.method == 'GET':
#         return render_template("security/register.html", register_user_form=form, security=security)

#     else:
#         #log = logform(csrf_enabled=False)
#         if form.validate_on_submit() or form.validate():
#             print ("HERE NOW SOMEONE SUBMITTED SOMETHING")
#             print (form.email.data)
#             print (form.username.data)
#             print (form.password.data)
#             user_datastore.create_user(form)
#             db.session.commit()

#         return redirect('/')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     print("Here")
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))

#     form = LoginForm()

#     if form.validate_on_submit():
#         user = user_datastore.find_user(email=form.email.data)

#         if user and user.verify_and_update_password(form.password.data):
#             login_user(user, remember=form.remember.data)
#             return redirect(url_for('home'))

#     return render_template('login.html', form=form)

#################


@app.route("/apidoc")
# @login_required
def api_docs():
  return render_template("swagger.html",username="swagger")


if __name__ == "__main__":
    app.run(debug=True,port=5000)
