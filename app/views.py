from flask import render_template ,flash, redirect , request, session, url_for
from app import app , db , models
from .forms import UserForm , SearchForm , InputForm ,ReadForm , EmailForm , UpdateForm,UpdateDataForm
from models import  Practo_doctors,Location,Doctor_location,Speciality,Doctor_speciality
from config import POSTS_PER_PAGE

@app.route('/', methods=['GET', 'POST'])
def index():
	search = SearchForm()
	return render_template("search.html",title='Search',search=search)

@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<int:page>', methods=['GET', 'POST'])
@app.route('/search/<int:page>/<string:speciality_post>/<string:locality_post>', methods=['GET', 'POST'])
def result(page=0,speciality_post=None,locality_post=None):
	form = SearchForm(request.form)
	locality = form.locality.data
	speciality = form.speciality.data
	if locality != None:
		locality = locality.upper()
	if speciality != None:
		speciality = speciality.upper()
	if speciality_post != None:
		speciality = speciality_post
	if locality_post != None:
		locality = locality_post
	speciality_post = speciality
	locality_post = locality
	doc = {}
	locationId = Location.query.filter_by(location=locality).first()
	errorMessage = "";
	if (locationId == None):
		errorMessage ="Doctors Not Available for this Location , Try Again"
		return render_template("error.html",title="errorMessage",errorMessage=errorMessage)

	specialityId = Speciality.query.filter_by(speciality=speciality).first()
	if (specialityId == None):
		errorMessage = "Doctors Not Available for this Speciality , Try Again"
		return render_template("error.html",title="errorMessage",errorMessage=errorMessage)

	locationDoctorID = Doctor_location.query.filter_by(locationId=locationId.id).all()
	specDoctorID = Doctor_speciality.query.filter_by(specialityId=specialityId.id).all()
	doctorList = []

	
	for loc_doc_id in locationDoctorID :
		for spec_doc_id in specDoctorID :
			if (loc_doc_id.doctorId == spec_doc_id.doctorId) :
				doctorList.append(loc_doc_id.doctorId)	
	
	doctors = Practo_doctors.query.all()
	doctor_locationList = Doctor_location.query.all()
	resultList =[]

	for doctor in doctors :
		for docId in doctorList :
			if(doctor.id == docId):
				doc["name"] = doctor.name
				doc["location"] = locality
				doc["degree"] = doctor.degree
				doc["experience"] = doctor.experience
				doc["speciality"] = speciality
				doc["email"] = doctor.email
				doc["imagePath"] = doctor.imagePath
				
				doc["address"] = Doctor_location.query.filter(Doctor_location.doctorId==docId)[0].address
				resultList.append(doc)
				doc={}
	result = []
	resultLength = len(resultList)
	begin = page * POSTS_PER_PAGE;
	i = 0
	while i < POSTS_PER_PAGE and begin < resultLength:
		i = i + 1
		result.append(resultList[begin])
		begin = begin + 1		
	return render_template("results.html",doctorList=result,speciality_post=speciality_post,locality_post=locality_post,resultLength=len(result))

@app.route('/insert', methods=['GET', 'POST'])
def insertData():
	inputForm = InputForm()
	return render_template("store.html",title='Admin',form=inputForm)


@app.route('/update', methods=['GET', 'POST'])
def update():
	'''Was being used for email input for edit operation'''
	form = UpdateForm()
	return render_template("update.html",title='Admin',form=form)

@app.route('/getupdate/<int:docID>', methods=['GET', 'POST'])
def updateData(docID):
	doc = {}
	specialityList = []
	doctor = Practo_doctors.query.get(docID)
	form = UpdateDataForm(obj = doctor)

	if form.validate():
		doctor = Practo_doctors.query.get(docID)
		if( doctor == None ):
			errorMessage = "Invalid Email Id , Try Again"	
			return render_template("error.html",title="errorMessage",errorMessage=errorMessage)		
		''' changed loop based selection to query filters.
		'''
		locationIdList=Doctor_location.query.filter(Doctor_location.doctorId==docId)
		SpecIdList = Doctor_speciality.query.filter(Doctor_speciality.doctorId==docId)
		
		doc["name"] = doctor.name
		doc["degree"] = doctor.degree
		doc["experience"] = doctor.experience
		doc["email"] = doctor.email
		doc["imagePath"] = doctor.imagePath
		
		
		for locid in locationIdList :
			location = Location.query.get(locid.locationID).location
			locationList.append(location)
		for spid in specialityIdList :
			speciality = Speciality.query.get(spid.specialityId).speciality
			specialityList.append(speciality)
		doc["location"] = locationList
		doc["speciality"] = specialityList
		users = Doctor_location.query.all()
		doc["address"] = Doctor_location.query.filter(Doctor_location.doctorId==docId)[0].address

	return render_template("updateData.html",title='Admin',form=form, doc=doc)

@app.route('/updateInDB', methods=['GET', 'POST'])
def updateInDB():
	form = UpdateDataForm(request.form)
	doctor = Practo_doctors.query.filter_by(email=form.email.data).first()
	if doctor == None:
		return render_template("delete.html",title='Delete Menu', success='No doctor present', email=form.email.data)
	db.session.delete(doctor)
	doctor_location = Doctor_location.query.filter_by(doctorId=doctor.id).all()
	doctor_speciality = Doctor_speciality.query.filter_by(doctorId=doctor.id).all()
	for location in doctor_location:
		db.session.delete(location)
		db.session.commit()
	for speciality in doctor_speciality:
		db.session.delete(speciality)
		db.session.commit()
	db.session.commit()
	
	query = Practo_doctors(form.name.data ,form.email.data , form.degree.data , form.experience.data   , "/static/"+form.imagePath.data)
	db.session.add(query)
	db.session.commit()
	doctor = Practo_doctors.query.filter_by(email=form.email.data).first()
	locationList = form.location.data.split(',')
	locationIdList = []

 	for loc in locationList :
		location = Location.query.filter_by(location=loc.upper()).first()
		if( location == None):
			query = Location(loc.upper())
			db.session.add(query)
			db.session.commit()
			location = Location.query.filter_by(location=loc.upper()).first()
		locationIdList.append(location.id)
	specialityList = form.speciality.data.split(',')
	specialityIdList = []
	for spec in specialityList :	
		speciality = Speciality.query.filter_by(speciality=spec.upper()).first()
		if( speciality == None):
			query = Speciality(spec.upper())
			db.session.add(query)
			db.session.commit()
			speciality = Speciality.query.filter_by(speciality=spec.upper()).first()
		specialityIdList.append(speciality.id)

	addressValue = form.address.data.split(',')

	for locationId , address in zip(locationIdList , addressValue):
		query = Doctor_location(doctor.id , locationId,address)	
		db.session.add(query)
	
	for specialityId in specialityIdList:
		query = Doctor_speciality(doctor.id , specialityId)
		db.session.add(query)
	db.session.commit() 

	successMessage = "Your Changes Have Been Saved !!!"	
	return render_template("success.html",title="successMessage",successMessage=successMessage)

@app.route('/read', methods=['GET', 'POST'])
def readDoctor():
	form = ReadForm()
	return render_template("read.html",title='Admin',form=form)

@app.route('/getuser/<int:docID>', methods=['GET', 'POST'])
def readUserData(docID):
	form = ReadForm(request.form)
	doc={}
	if form.validate():
		doctor = Practo_doctors.query.get(docID)
		print doctor
		if( doctor == None ):
			errorMessage = "Invalid Email Id , Try Again"
			return render_template("error.html",title="errorMessage",errorMessage=errorMessage)
		locationIdList = []
		users = Doctor_location.query.all()
		for doc_loc in users :
			if(doc_loc.doctorId == docID ):
				locationIdList.append(doc_loc.locationId)		
		specialityIdList = []
		users = Doctor_speciality.query.all()
		for doc_spec in users :
			if(doc_spec.doctorId == docID ):
				specialityIdList.append(doc_spec.specialityId)		
		doc["name"] = doctor.name
		doc["degree"] = doctor.degree
		doc["experience"] = doctor.experience
		doc["email"] = doctor.email
		doc["imagePath"] = doctor.imagePath
		locationList = []
		specialityList= []
		addressList = []		
		doc_loc = Doctor_location.query.all()
		for u in doc_loc:
			for loc in locationIdList :
				if (u.doctorId == doctor.id and u.locationId == loc):
					addressList.append(u.address)
		for locid in locationIdList :
			query = Location.query.filter_by(id=locid).first()
			locationList.append(query.location)		
		for spid in specialityIdList :
			query = Speciality.query.filter_by(id=spid).first()
			specialityList.append(query.speciality)		
		doc["address"] = addressList
		doc["location"] = locationList
		doc["speciality"] = specialityList		
	return render_template("showData.html",title='Admin',doc=doc)

@app.route('/store', methods=['GET', 'POST'])
def add_doctor():
    form = InputForm(request.form)
    if form.validate():
        query = Practo_doctors(form.name.data , form.email.data , form.degree.data , form.experience.data , "/static/"+form.imagePath.data)
        db.session.add(query)
        db.session.commit()
        doctor = Practo_doctors.query.filter_by(email=form.email.data).first()
        locationList = form.location.data.split(',')
        locationIdList = []
        for loc in locationList :																	#Good Feature: Location-case sensitivity
        	location = Location.query.filter_by(location=loc.upper()).first()
        	if( location == None):
        		query = Location(loc.upper())														#Saving new locations in UPPER CASE
        		db.session.add(query)
        		db.session.commit()
        		location = Location.query.filter_by(location=loc.upper()).first()
       		locationIdList.append(location.id)
       	specialityList = form.speciality.data.split(',')
       	specialityIdList = []

       	for spec in specialityList :	
        	speciality = Speciality.query.filter_by(speciality=spec.upper()).first()
        	if( speciality == None):
        		query = Speciality(spec.upper())													  #Saving new specialties in UPPER CASE
        		db.session.add(query)
        		db.session.commit()
        		speciality = Speciality.query.filter_by(speciality=spec.upper()).first()
        	specialityIdList.append(speciality.id)

        addressValue = form.address.data.split(',')

        for locationId , address in zip(locationIdList , addressValue):									#adding to association table
        	query = Doctor_location(doctor.id , locationId,address)										
        	db.session.add(query)

        for specialityId in specialityIdList:															#adding to association table
        	query = Doctor_speciality(doctor.id , specialityId)
        	db.session.add(query)
        db.session.commit() 
    	return render_template('save.html')
    
    errorMessage = "Enter Valid data in form"
    return render_template("error.html",title="errorMessage",errorMessage=errorMessage)
 
@app.route('/adminIndex', methods=['GET', 'POST'])
def adminMenu():
	deleteForm = EmailForm()
	doctors = Practo_doctors.query.all()

	return render_template("admin.html", title='Admin Menu', deleteForm=deleteForm, doctors=doctors)

@app.route('/deleteDoctor/<int:docID>', methods=['GET', 'POST'])
def deleteDcotor(docID):

	doctor = Practo_doctors.query.get(docID)
	print doctor, "Hello"
	if doctor == None:
		return render_template("delete.html",title='Delete Menu', success='No doctor present', email=doctor.email)
	db.session.delete(doctor)
	doctor_location = Doctor_location.query.filter_by(doctorId=docID).all()
	doctor_speciality = Doctor_speciality.query.filter_by(doctorId=docID).all()
	for doc_loc in doctor_location:																			#Cascade Delete doctor on doctor.location
		db.session.delete(doc_loc)
		db.session.commit()
	for doc_spec in doctor_speciality:																		#Cascade Delete doctor on doctor.specialty
		db.session.delete(doc_spec)
		db.session.commit()
	db.session.commit()
	return render_template("delete.html",title='Delete Menu', success='Deleted successfully', email=doctor.email)
