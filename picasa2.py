import json
import re
import sqlite3

conn = sqlite3.connect('picasadb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Albums;
DROP TABLE IF EXISTS Contacts;
DROP TABLE IF EXISTS Starred;
DROP TABLE IF EXISTS Albums_Files;
DROP TABLE IF EXISTS Faces_Files;

CREATE TABLE Albums (
    id  TEXT UNIQUE,
    name   TEXT UNIQUE
);

CREATE TABLE Contacts (
    id  TEXT UNIQUE,
    name   TEXT UNIQUE
);


CREATE TABLE Starred (
    file  TEXT,
    folder  TEXT,
    year  TEXT
);

CREATE TABLE Albums_Files (
    file  TEXT,
    folder  TEXT,
    year  TEXT ,
    id  TEXT 
);

CREATE TABLE Faces_Files (
    file  TEXT,
    folder  TEXT,
    year  TEXT ,
    id  TEXT 
);
''')


with open('picasa.ini.json') as data_file:    
    data = json.load(data_file)

unique_header = list()
unique_album_ids = list()
unique_contacts = list()
albums = list()
starredfiles = list()
file_albums = list()
file_faces = list()
contacts = list()

for row in data:
	if re.search('album', row['header'], re.IGNORECASE) and re.search('name', row['action'], re.IGNORECASE): 
		ID = row['header'].split(':')[1]
		name = row['action'].split('=')[1]
		if ID not in unique_album_ids:
			#print "Album ID & Name:",ID, name
			album = dict()
			album['id'] = ID
			album['name'] = name
			unique_album_ids.append(ID)
			albums.append(album)
	
	elif re.search('Contacts2', row['header'], re.IGNORECASE): 
		id = row['action'].split('=')[0]
		name = row['action'].split('=')[1].split(';')[0]
		#print row['action']
		if id not in unique_contacts:
			#print "Contact ID & Name:",id, name
			contact = dict()
			contact['id'] = id
			contact['name'] = name
			unique_contacts.append(id)
			contacts.append(contact)
		
		
	elif re.search('jpe*g', row['header'], re.IGNORECASE) and re.search('star=yes', row['action'], re.IGNORECASE):
		#print "Starred File:", row['year'], row['folder'], row['header']
		starred = dict()
		starred['file'] = row['header']
		starred['folder'] = row['folder']
		starred['year'] = row['year']
		starredfiles.append(starred)
	
	elif re.search('jpe*g', row['header'], re.IGNORECASE) and re.search('albums', row['action'], re.IGNORECASE):
		ids = row['action'].split('=')[1].split(',')
		for id in ids:
			#print row['year'], row['folder'], row['header'], id
			file_album = dict()
			file_album['file'] = row['header']
			file_album['folder'] = row['folder']
			file_album['year'] = row['year']
			file_album['id'] = id
			file_albums.append(file_album)

	elif re.search('jpe*g', row['header'], re.IGNORECASE) and re.search('faces', row['action'], re.IGNORECASE):
		faces = row['action'].split('=')[1].split(';')
		#print faces
		for face in faces:
			#print row['year'], row['folder'], row['header'], face.split(',')[1]
			file_face = dict()
			file_face['file'] = row['header']
			file_face['folder'] = row['folder']
			file_face['year'] = row['year']
			file_face['id'] = face.split(',')[1]
			file_faces.append(file_face)

print "Inserting Albums..."			
for i in albums:
	#print "album:", i['id'], i['name']
	cur.execute('''INSERT INTO Albums (id, name) 
		VALUES ( ?, ? )''', (i['id'], i['name'] ) )
	conn.commit()

print "Inserting Contacts..."	
for i in contacts:
	#print "contact:", i['id'], i['name']
	cur.execute('''INSERT INTO Contacts (id, name) 
		VALUES ( ?, ? )''', (i['id'], i['name'] ) )
	conn.commit()

	
print "Inserting Starred Files..."
for i in starredfiles:
	#print "starred:", i['year'], i['folder'], i['file']
	cur.execute('''INSERT INTO Starred (file, folder, year) 
		VALUES ( ?, ?, ?)''',( i['file'], i['folder'], i['year'] ) )
	conn.commit()

print "Inserting Album Content..."
for i in file_albums:
	#print "file_album:", i['year'], i['folder'], i['file'], i['id']
	cur.execute('''INSERT INTO Albums_Files (file, folder, year, id) 
		VALUES ( ?, ?, ?, ?)''',( i['file'], i['folder'], i['year'] , i['id'] ) )
	conn.commit()

	
print "Inserting Face Content..."
for i in file_faces:
	#print "file_face:", i['year'], i['folder'], i['file'], i['id']
	cur.execute('''INSERT INTO Faces_Files (file, folder, year, id) 
		VALUES ( ?, ?, ?, ?)''',( i['file'], i['folder'], i['year'] , i['id'] ) )
	conn.commit()

