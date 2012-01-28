#!/usr/bin/python -tt
import urllib2
import processparser
import dictdiffer
import os.path
import os

# TODO
# Input all entities (700+) and their name
# Generate a unique file with only new processes
# Parsing still leaves weird stuffs like td>
# Handle if there is more than 50 results and they are not all on the page
# DictDiffer should return the list of actual objets, no only the keys --> Wrapper
FILE_NAME = "processes.txt"

def main():
	#POST: urllib.urlencode({"entidad" : "20589302", "tipoProceso" : "1", "estado" : "1"})
	entities = {
	     "01002034" : "Entity 1",
	     "20589302" : "Entity 2",
	     "12306900" : "Entity 3" }
	print "Will run against those entities %s" % entities
	for entity_id, entity_name in entities.iteritems():
		print "\n***** Entity %s (%s) *****" % (entity_name, entity_id)
		do_one(entity_id)

def do_one(entity):
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

	# Retrieve saved processes from hard drive
	saved_processes = read_processes(entity) #gen_test_processes()
	# Compare fetched process with saved ones
	dictDiffer = dictdiffer.DictDiffer(parser.all_processes, saved_processes)
	result = list(dictDiffer.added())
	print "***** Processes added since last time "
	for p in result:
		print p

	result = list(dictDiffer.removed())
	print "***** Processes removed since last time"
	for p in result:
		print p

	# Write all processes fetched today to file
	write_processes(entity, parser.all_processes)


def write_processes(entity, dict_of_processes):
	"""Write the processes on the hard drive"""
	# Check the entity folder exists
	if not os.path.isdir(entity):
		# If not, create it
		print "***** Directory for %s does not exist, creating it." % entity
		os.mkdir(entity)
	# Check that the processes file exists
	file_path = os.path.join(os.curdir, entity, FILE_NAME)
	file_input = open(file_path,'w') # will create the file if does not exist
	for p in dict_of_processes.itervalues():
		file_input.write(p.stringify(';'))
		file_input.write('\n')
	file_input.close()

def read_processes(entity):
	"""Read processes from file on hard drive """
	dict_of_processes = {}
	file_path = os.path.join(os.curdir, entity, FILE_NAME)
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
