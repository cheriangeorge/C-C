# from flask import Flask,render_template,request,redirect

# from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from model import *
# from rest_api import *
# from backend_jobs import *
# from main import *
# from frontend import *
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore,auth_required, login_required, current_user,roles_required


def tag_validation_error(tagname_sent):
  # print("Validating : ",tagname_sent)
  message = ""
  if tagname_sent==None:
    message="Please fill in the name"
    return message
  if type(tagname_sent)==type("abc"):
    if len(tagname_sent.strip())==0 or len(tagname_sent.strip())>20:
      message="Name cannot be empty and can have at most 20 characters."
      return message
  else:
    message="Invalid inputs"
    return message
  tagname_sent=tagname_sent.lower()
  if not tagname_sent.replace(' ','').isalnum():
    message="Name can contain only alphanumeric characters and spaces"
    return message
  tags = Tag.query.filter_by(name=tagname_sent).all()
  if len(tags)>0:
    message="This tag already exists"
    return message
  return message
  #End validation

def check_tags(tag_list):
  tags = tag_list.split(',')
  message=""
  tag_ids=[]
  for tagname_sent in tags:
    tagx = Tag.query.filter_by(name=tagname_sent).first()
    if not tagx:
      message+=" "+tagname_sent+" "
    else:
      # print(tagx.id)
      tag_ids.append(tagx.id)
  if len(message)>0:
    message = "Invalid Tags : "+message
  return (message,tag_ids)

def validate_text(text_input,length_constraint,field_name):
  message = ""
  if text_input==None:
    message="Please fill in " + field_name
    return message
  if type(text_input)==type("abc"):
    if len(text_input.strip())==0 or len(text_input.strip())>length_constraint:
      message=field_name+" cannot be empty and can have at most "+str(length_constraint)+" characters."
      return message
  else:
    message="Invalid inputs"
    return message
  return message
    
def get_tagnames_from_id(tagids):
  tagnames=[]
  for i in tagids:
    tagx = Tag.query.filter_by(id=i).first()
    if tagx:
      tagnames.append(tagx.name)
  return tagnames

def get_assigned_tags(id,type):
  tag_list=[]
  if type=="content":
    related_tags = Tag_Content_Rel.query.filter_by(content_id=id).all()
    for i in related_tags:
      tag_list.append(i.tag_id)
  return tag_list

def get_username_from_id(id):
  name=""
  Userx = User.query.filter_by(id=id).first()
  if Userx:
    email = Userx.email
    name = email.split('@')[0]
  return name

def get_content_obj(i,with_body):
  id = i.id
  title = i.title
  body = i.content_body
  date = i.created_at
  is_anon = i.is_anon
  user_id = i.user_id
  tagids=get_assigned_tags(id,"content")
  tagnames=get_tagnames_from_id(tagids)
  author=get_username_from_id(user_id)
  if with_body:
    return dict(id=id,title=title,body=body,date=date,is_anon=is_anon,author=author,tags=",".join(tagnames))
  else:
    return dict(id=id,title=title,date=date,is_anon=is_anon,author=author,tags=",".join(tagnames))