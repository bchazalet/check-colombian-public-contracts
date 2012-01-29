#!/usr/bin/python -tt
import urllib2
import os.path
import os
import sys

# My own modules
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'pym'))
import processparser
from notification import Notification
import dictdiffer

# TODO
# Handle if there is more than 50 results and they are not all on the page
# Handle HTTP Error 500: internal server error
# Handle unique file name and many running the same day. How do we name the files?
# Create a script that would setup cron to run the program every day at 5am

# LOW PRIORITY
# DictDiffer should return the list of actual objets, no only the keys --> Wrapper
# Create a script that can tar and zip the folder for distribution
# Improve email notification with MIME format
# A clear entities function that clears all entities folder (with a WARNING)

MAIN_FILE_NAME = "new-processes.csv"
FILE_NAME = "processes.txt"
ENTITY_INPUT = "entities-to-check.csv"
ENTITIES_FOLDER = "entities"
REPORTS_FOLDER = "reports"

def main():
	#POST: urllib.urlencode({"entidad" : "20589302", "tipoProceso" : "1", "estado" : "1"})
	#entities = import_entities()
	entities = {"285000001": "Gobernacion"}
	if len(entities) == 0:
		print "No entities found. Are you sure the file is there?"
	elif len(entities) < 10:
		print "Will run against those entities %s" % entities
	else:
		print "Will run against %d entities" % len(entities)

	for entity_id, entity_name in entities.iteritems():
		print "\n***** Entity %s (%s) *****" % (entity_name, entity_id)
		new_processes = do_one(entity_id)
		if len(new_processes) > 0:
			append_to_report(entity_id, entity_name, new_processes)

	# Notify the result
	notif = Notification("Nuevos contratos disponibles", "There are new processes");
	notif.send()

def do_one(entity):
	"""Process one entity and return the list of new processes"""
	url = "http://www.contratos.gov.co/consultas/resultadosConsulta.do?entidad=%s&desdeFomulario=true&estado=1&tipoProceso=1&objeto=72000000" % entity # objecto is the Producto o Servicio field
	f = urllib2.urlopen(url)
	# Now we look for the <table> tag and retrieve all processes
	parser = processparser.HtmlProcessParser()
	parser.feed(f.read())
	f.close()
	# Print all parsed processes --commented out
	print "***** %d process(es) found" % len(parser.all_processes)
	#for process in parser.all_processes.itervalues():
	#	print process
	if len(parser.all_processes) == 50:
		print "WARNING: this entity could have more than 50 results. You SHOULD check manually."
	
	# Retrieve saved processes from hard drive
	saved_processes = read_processes(entity) #gen_test_processes()
	# Compare fetched process with saved ones
	dictDiffer = dictdiffer.DictDiffer(parser.all_processes, saved_processes)
	new_processes_key = list(dictDiffer.added())
	print "***** Processes added since last time "
	for p in new_processes_key:
		print p

	result = list(dictDiffer.removed())
	print "***** Processes removed since last time"
	for p in result:
		print p

	# Write all processes fetched today to entity file
	write_processes(entity, parser.all_processes)

	new_processes = { k: parser.all_processes[k] for k in new_processes_key}

	return new_processes

def append_to_report(entity_id, entity_name, dict_of_processes):
	"""Append processes to a centralized file listing all new processes"""
	if len(dict_of_processes) > 0:
		file_path = os.path.join(os.curdir, REPORTS_FOLDER, MAIN_FILE_NAME)
		file_input = open(file_path,'a') # will append at this end of the file and will create the file if does not exist
		file_input.write(entity_id + " - " + entity_name + "\n")
		for p in dict_of_processes.itervalues():
			file_input.write(p.stringify(';'))
			file_input.write('\n')
		file_input.write('\n')
		file_input.close()

def write_processes(entity, dict_of_processes):
	"""Write the processes on the hard drive"""
	# Check the entity folder exists
	entity_path = os.path.join(os.curdir, ENTITIES_FOLDER, entity)
	if not os.path.isdir(entity_path):
		# If not, create it
		print "***** Directory for %s does not exist, creating it." % entity
		os.makedirs(entity_path)
	# Check that the processes file exists
	file_path = os.path.join(os.curdir, entity_path, FILE_NAME)
	file_input = open(file_path,'w') # will create the file if does not exist
	for p in dict_of_processes.itervalues():
		file_input.write(p.stringify(';'))
		file_input.write('\n')
	file_input.close()

def read_processes(entity):
	"""Read processes from file on hard drive """
	dict_of_processes = {}
	file_path = os.path.join(os.curdir, ENTITIES_FOLDER, entity, FILE_NAME)
	if not os.path.isfile(file_path):
		print "***** There is no file for entity %s" % entity
	else:
		file_input = open(file_path, 'r')
		# First thing on the line is the id (before the first semicolumn)
		for line in file_input:
			semi_col_idx = line.find(';')
			if semi_col_idx != -1:
				process_id = line[0:semi_col_idx]
				dict_of_processes[process_id] = "found"
		file_input.close()
	# In any case return the dict
	return dict_of_processes

def import_entities():
	"""Read entities from file on hard drive """
	dict_of_entities = {}
	file_path = os.path.join(os.curdir, ENTITY_INPUT)
	if not os.path.isfile(file_path):
		print "***** Entity file is missing"
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

def gen_test_processes():
	"""Generate fake processses to test some functions"""
	test = {}
	p = processparser.Process()
	p.id = "BOB-45-DI"
	test[p.id] = p
	p = processparser.Process()
	p.id = "FDLCH-LIC-006-2012"
	test[p.id] = p
	return test

if __name__ == '__main__':
	main()
