from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_login import UserMixin
from flask_security import UserMixin, RoleMixin, hash_password
#from security import user_datastore,sec
from flask_security import Security, SQLAlchemyUserDatastore
# from flask_cors import CORS
# from flask_caching import Cache #caching


app = Flask(__name__)
# CORS(app) # Cross-Origin Resource Sharing
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///campusconnect.sqlite3"
app.config["SECRET_KEY"]='thisismysecretkey123@34'
app.config["SECURITY_PASSWORD_SALT"]='salt'
# app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]='Authentication-Token'
app.config["WTF_CSRF_ENABLED"]=False
app.config["SECURITY_PASSWORD_HASH"]="bcrypt"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

app.config['DEBUG'] = True

#########
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = False
app.config['SECURITY_RECOVERABLE'] = False
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

app.config['SECURITY_CONFIRM_LOGIN_WITHOUT_CONFIRMATION'] = False
# app.config['SECURITY_REGISTER_URL'] = '/signup'
app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'security/register.html'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'security/login.html'
#######


db=SQLAlchemy(app)


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))
# class RolesUsers(db.Model):
#     __tablename__ = 'roles_users'
#     id = db.Column(db.Integer(), primary_key=True)
#     user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
#     role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))

####USER MODEL###
class User(UserMixin,db.Model):
  __tablename__ = 'user'
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  # username=db.Column(db.String(30),unique=True,nullable=False)
  password=db.Column(db.String(30),nullable=False)
  #Email
  email=db.Column(db.String(60),unique=True,nullable=False)
  #Token
  fs_uniquifier=db.Column(db.String(255),unique=True, nullable=False)
  #Active
  active = db.Column(db.Boolean())
  ########
  last_login_at = db.Column(db.DateTime())
  current_login_at = db.Column(db.DateTime())
  last_login_ip = db.Column(db.String(100))
  current_login_ip = db.Column(db.String(100))
  login_count = db.Column(db.Integer)
  confirmed_at = db.Column(db.DateTime())
  ########
  roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
  #Question, Content and Assessment relationships#
  questions = db.relationship('User_Question_Rel',backref='User', lazy='subquery')
  assessments = db.relationship('User_Assessment_Rel',backref='User', lazy='subquery')
  content = db.relationship('User_Content_Rel',backref='User', lazy='subquery')
#   tags = db.relationship('User_Tag_Rel',backref='User', lazy='subquery')
  # Use cascade="all,delete" 
  user_questions=db.relationship('Question',backref='User', lazy='subquery')
  user_assessments=db.relationship('Assessment', backref='User', lazy='subquery')
  user_content=db.relationship('Content',backref='User', lazy='subquery')
  user_tags = db.relationship('Tag',backref='User', lazy='subquery')
  
####ROLE MODEL###
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

####CONTENT MODEL###
class Content(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  title=db.Column(db.String(500),nullable=False)
  content_body=db.Column(db.String(5000),nullable=False)
  created_at = db.Column(db.Date)
  is_anon = db.Column(db.Boolean())
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False) #changed from owner=username 
  tags = db.relationship('Tag_Content_Rel',backref='Content')

####QUESTION MODEL###
class Question(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  question=db.Column(db.String(500),nullable=False)
  option1=db.Column(db.String(500),nullable=False)
  option2=db.Column(db.String(500),nullable=False)
  option3=db.Column(db.String(500),nullable=False)
  option4=db.Column(db.String(500),nullable=False)
  correct_option = db.Column(db.Integer(), nullable=False)
  is_anon = db.Column(db.Boolean())
  created_at = db.Column(db.Date)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False) #changed from owner=username 
  tags = db.relationship('Tag_Question_Rel',backref='Question')

####ASSESSMENT MODEL###
class Assessment(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  name=db.Column(db.String(500),nullable=False)
  created_at = db.Column(db.Date)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False) #changed from owner=username 
  tags = db.relationship('Tag_Assessment_Rel',backref='Content')
  questions = db.relationship('Assessment_Question_Rel',backref='Asessment')

####TAG MODEL###
class Tag(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  name=db.Column(db.String(500),nullable=False)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False) #changed from owner=username 
  questions = db.relationship('Tag_Question_Rel',backref='Tag')
  assessments = db.relationship('Tag_Assessment_Rel',backref='Tag')
  content = db.relationship('Tag_Content_Rel',backref='Tag')


###Assessment_Question_Rel MODEL### 
class Assessment_Question_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  assessment_id = db.Column(db.Integer,db.ForeignKey('assessment.id'),nullable=False)
  question_id = db.Column(db.Integer,db.ForeignKey('question.id'),nullable=False)

####User_Question_Rel MODEL###
class User_Question_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  question_id = db.Column(db.Integer,db.ForeignKey('question.id'),nullable=False)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

####User_Assessment_Rel MODEL###
class User_Assessment_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  assessment_id = db.Column(db.Integer,db.ForeignKey('assessment.id'),nullable=False)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

####User_Content_Rel MODEL###
class User_Content_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  content_id = db.Column(db.Integer,db.ForeignKey('content.id'),nullable=False)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

####Tag_Content_Rel MODEL###
class Tag_Content_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  content_id = db.Column(db.Integer,db.ForeignKey('content.id'),nullable=False)
  tag_id = db.Column(db.Integer,db.ForeignKey('tag.id'),nullable=False)

####Tag_Question_Rel MODEL###
class Tag_Question_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  question_id = db.Column(db.Integer,db.ForeignKey('question.id'),nullable=False)
  tag_id = db.Column(db.Integer,db.ForeignKey('tag.id'),nullable=False)

####Tag_Assessment_Rel MODEL###
class Tag_Assessment_Rel(db.Model):
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  assessment_id = db.Column(db.Integer,db.ForeignKey('assessment.id'),nullable=False)
  tag_id = db.Column(db.Integer,db.ForeignKey('tag.id'),nullable=False)

# db.create_all()
# a1 = User(username="admin",password="pass123",email="admin@dummy.in",fs_uniquifier="adminxyz")
# db.session.add(a1)
# db.session.commit()
# a1=User.query.filter_by(username='admin').first()
# a1.password="pass123"
# db.session.commit()

# sec = Security()
# sec.init_app(app,user_datastore)



    # Flask Security provides endpoint http://192.168.1.110:5000/login?include_auth_token
