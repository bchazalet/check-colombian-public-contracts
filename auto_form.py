#!/usr/bin/python -tt
import urllib2
import os.path
import os
import pwd
import sys
import datetime
from pymongo import Connection
from pymongo.errors import ConnectionFailure
# My own modules
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'pym'))
from processparser import Process
from processparser import HtmlProcessParser
from notification import Notification
import dictdiffer
from report import Report

# TODO
# Handle if there is more than 50 results and they are not all on the page
# Handle HTTP Error 500: internal server error
# Handle if you are running on Windows
# Solve UTF-8 and spanish accents/letters issue
# Create a conf file to edit email settings
# Update the attached file's name with the actual report name

# LOW PRIORITY
# DictDiffer should return the list of actual objets, no only the keys --> Wrapper
# A clear entities function that clears all entities folder (with a WARNING)
# The way we build the new processes filename is not bullet proof (should get the latest filename)

FILE_NAME = "processes.txt"
ENTITY_INPUT = "entities-to-check.csv"
ENTITIES_FOLDER = "entities"
REPORTS_FOLDER = "reports"
base_dir = None

def main():
	# Where is our base folder (the one containing the auto_form.py file)?
	global base_dir 
	base_dir = os.path.normpath(os.path.dirname(os.path.realpath(sys.argv[0])))
	# Parse arguments
	flags = parse_args(sys.argv)
	# We are good to go!
	try:
		connection = Connection() # Mongo db
		print "Connected to DB successfully"
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		sys.exit(1)
	db = connection["auto_form"]
	if flags["delete_all"]:
		db.processes.remove({})
		print "Deleted all data from db"
	#entities = import_entities()
	entities = {"285000001": "Gobernacion"}
	current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	if len(entities) == 0:
		print "%s:: No entities found. Are you sure the file is there?" % current_time
	elif len(entities) < 10:
		print "%s:: Will run against those entities %s" % (current_time,entities)
	else:
		print "%s:: Will run against %d entities" % (current_time,len(entities))
	total = 0;
	report = Report(os.path.join(base_dir,REPORTS_FOLDER))
	for entity_id, entity_name in entities.iteritems():
		print "\n***** Entity %s (%s) *****" % (entity_name, entity_id)
		new_processes = do_one(db, entity_id)
		if len(new_processes) > 0:
			report.append(entity_id, entity_name, new_processes)
			total += len(new_processes)
	db.connection.close()
	# Notify the result
	notif = None
	if report.created:
		text_body = "Hay %d nuevos contratos disponibles.\nAdjunto el reporte." % total
		notif = Notification(text_body, report.file_path);
	else:
		notif = Notification("No hay nada nuevo hoy.", None);
	notif.send()
	# Display summary
	print "\n"
	print "#############################################################"
	print "# Summary"
	print "# We found %d new processes" % total
	print "# Report avail. at %s" % report.file_path
	print "#############################################################"

def do_one(db, entity):
	"""Process one entity and return the list of new processes"""
	url = "http://www.contratos.gov.co/consultas/resultadosConsulta.do?entidad=%s&desdeFomulario=true&estado=1&tipoProceso=1&objeto=72000000" % entity # objecto is the Producto o Servicio field
	try:
		f = urllib2.urlopen(url)
	except IOError:
		print "Could not fetch the url. Skipping."
		return {}
	except urllib2.HTTPError, error:
		print "A HTTP error occured. Skipping."
		print error.read()
		return {}

	# Now we look for the <table> tag and retrieve all processes
	parser = HtmlProcessParser(entity)
	parser.feed(f.read())
	f.close()
	# Print all parsed processes --commented out
	print "***** %d process(es) found" % len(parser.all_processes)
	#for process in parser.all_processes.itervalues():
	#	print process
	if len(parser.all_processes) == 50:
		print "WARNING: this entity could have more than 50 results. You SHOULD check manually."
	
	# Insert or update into database
	new_processes = []
	for p in parser.all_processes.itervalues():
		res = db.processes.update({"id":p["id"]}, p, True, safe=True)
		if res.has_key("upserted"):
			# A new document was inserted, i.e process was new
			new_processes.append(p)
	# Compare fetched process with saved ones
	print "***** Processes added since last time "
	for p in new_processes:
		print p["id"]

	return new_processes

def import_entities():
	"""Read entities from file on hard drive """
	dict_of_entities = {}
	file_path = os.path.join(base_dir, ENTITY_INPUT)
	if not os.path.isfile(file_path):
		print "***** Entity file is missing"
		print "entity file path = %s" % file_path
	else:
		file_input = open(file_path, 'r')
		# First thing on the line is the id (before the first semicolumn)
		for line in file_input:
			semi_col_idx = line.find(';')
			if semi_col_idx != -1:
				entity_id = line[0:semi_col_idx]
				dict_of_entities[entity_id] = line[semi_col_idx+1:-1] #-1 is to remove the \n at the end of the line
		file_input.close()
	# In any case return the dict
	return dict_of_entities

def parse_args(argv):
	""" Parsing arguments """
	flags =  {"delete_all": False}
	if len(argv) > 2:
		print "Too many arguments"
		sys.exit(1)
	elif len(argv) == 2:
		if argv[1] == "--setup-cron":
			setup_cron()
			sys.exit(0)
		elif argv[1] == "-d":
			flags["delete_all"] = True
		elif argv[1] != "--run":
			print "invalid option: %s" % argv[0]
			sys.exit(1)
	return flags

def setup_cron():
	owner_name = retrieve_file_owner();
	if owner_name != None:
		try:
			cron_file = open("/etc/cron.d/auto_form","w")
			cron_file.write('MAILTO=""\n')
			cron_file.write("00 05 * * * %s %s/auto_form.py >> %s/log/out\n" % (owner_name, base_dir, base_dir))
			cron_file.close()
			print "Wrote in /etc/cron.d/auto_form"
			print "Cron setup to run every day at 5am."
		except IOError:
			print "Could not write in /etc/cron.d/auto_form. Try to execute using sudo."
	else:
		print "Could not get your username. Failing."

def retrieve_file_owner():
	try:
		main_file = os.path.join(base_dir, "auto_form.py")
		st = os.stat(main_file)
	except IOError:
		print "Could not retrieve file's owner name on %s" % main_file
	else:
		user_info = pwd.getpwuid(st.st_uid)
		return user_info[0]

	return None

def gen_test_processes():
	"""Generate fake processses to test some functions"""
	test = {}
	p = Process()
	p.id = "BOB-45-DI"
	test[p.id] = p
	p = Process()
	p.id = "FDLCH-LIC-006-2012"
	test[p.id] = p
	return test

if __name__ == '__main__':
	main()
