# from flask import Flask,jsonify

# app = Flask(__name__)

# result = ["shadrul","gupta"]
# @app.route('/')
# def index():
#     return jsonify({"name":result})

# if __name__ == '__main__':
#     app.run(debug=True)

import os
import urllib.request
from app import app
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import docx2txt
import spacy
from spacy.matcher import Matcher
import re
from docx2python import docx2python
from docx import Document

nlp = spacy.load('en_core_web_sm')

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extraction(resume):
	temp = docx2txt.process(resume)
	text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
	return '\n'.join(text)

def extract_image(resume):
	result = docx2python(resume)
	count =0
	for name, image in result.images.items():
		count+=1
	return count
# def extract_table(resume):
# 	doc = Document(resume)
# 	table = doc.tables
# 	count =0
# 	for t in table:
# 		count+=1
# 	return count

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', [pattern])
    
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

def extract_mobile_number(text):
    # phone = re.findall(re.compile(r'((\+*)((0[ -]+)*|(91 )*)(\d{12}+|\d{10}+))|\d{5}([- ]*)\d{6}'),text)
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number
    else:
        return "NA"

def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return none
    else:
    	return "NA"

def extract_link(text):
    link = re.findall(re.compile(r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'),text)
    if link:
        try:
            return link[0][0]
        except:
            return "NA"
    else:
    	return "NA"

@app.route('/api/demo', methods =['GET','POST'])
def demo():
	return "hello"

@app.route('/file-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		st = os.path.join(app.config['UPLOAD_FOLDER']) + '/' + filename
		text = extraction(st)
		images = extract_image(st)
		name = extract_name(text)
		number = extract_mobile_number(text)
		email = extract_email(text)
		link = extract_link(text)
		# tables = extract_table(st)
		resp = jsonify({'Name' : name, 'Mobile Number':number, 'Email':email, 'Linkedin Profile':link, 'Number Of Images':images})
		resp.status_code = 201

		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp

if __name__ == "__main__":
    app.run(debug=True)