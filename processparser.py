#!/usr/bin/python -tt

from sgmllib import SGMLParser

class HtmlProcessParser(SGMLParser):
	def reset(self):
		SGMLParser.reset(self)
		self.tableTagFound = False
		self.tableHeaderPassed = False #first <tr></tr>
		self.weAreInTd = False
		self.curColumnNb = 0
		self.all_processes = {}

	def start_table(self, attrs):
		#print "in start_table"
		self.tableTagFound = True;

	def start_tr(self, attrs):
		#print "start_tr"
		self.curColumnNb = 0
		if self.tableHeaderPassed:
			#This is an actual line of table content
			#print "This is an actual line of table content"	
			self.idParsed = False
			self.currentProcess = Process()

	def end_tr(self):
		#print "in end_tr"
		if not self.tableHeaderPassed:
			#This is only the header
			self.tableHeaderPassed = True
			#print "This was only the header"
		else:
			#print self.currentProcess
			#self.allProcesses.append(self.currentProcess)
			self.currentProcess.date = fix_date(self.currentProcess.date)
			self.all_processes[self.currentProcess.id] = self.currentProcess
	def start_td(self, attrs):
		self.weAreInTd = True
			
	def end_td(self):
		self.weAreInTd = False
		self.curColumnNb += 1

	def handle_data(self, data):
		if self.tableHeaderPassed and self.weAreInTd:
			#print data
			# still having issue with <td class='tablaslistOdd'><b>Bogota D.C.</b> : Bogota D.C.</td>
			# and this <td class='tablaslistOdd'><b>Fecha de apertura</b><br/>24-12-2012</td>
			if self.curColumnNb == 0:
				#do nothing with that
				useless = 0
			elif self.curColumnNb == 1: #Id LP001-2011
				if not self.idParsed:				
					self.currentProcess.id = data.strip()
					self.idParsed = True
			elif self.curColumnNb == 2: # Licitacion Publica
				self.currentProcess.type = remove_special_chars(data)
			elif self.curColumnNb == 3: # Borrador
				self.currentProcess.state = remove_special_chars(data)
			elif self.curColumnNb == 4: # ADPOSTAL - ADMINISTRACION POSTAL NACIONAL E INTERNACIONAL
				self.currentProcess.entity = remove_special_chars(data)
			elif self.curColumnNb == 5: # 
				self.currentProcess.subject = remove_special_chars(data)
			elif self.curColumnNb == 6: #
				self.currentProcess.place += remove_special_chars(data) 
			elif self.curColumnNb == 7: # 
				self.currentProcess.price = remove_special_chars(data)
			elif self.curColumnNb == 8: # 
				self.currentProcess.date += remove_special_chars(data)

def remove_special_chars(string):
	string = string.replace(';','')
	string = string.replace('\n','')
	string = string.replace('\r','')
	return string.strip()

def fix_date(wrongly_parsed_date):
	# I usually get that as a result:  Fecha de apertura>18-01-2012<td>
	wrongly_parsed_date = wrongly_parsed_date.replace("<td>","")
	wrongly_parsed_date = wrongly_parsed_date.replace(">"," ")
	return wrongly_parsed_date

class Process():
	# Numero de proceso 
	# id - tipo de processo
	# estado
	# Entidad
	# Objecto
	# Departamento y Municipio de ejecucion
	# Cuantia
	# Fecha (dd-mm-aaaa)
	def __init__(self):
		self.id = ""
		self.type = ""
		self.state = ""
		self.entity = ""
		self.subject = ""
		self.place = ""
		self.price = ""
		self.date = ""

	def stringify(self, delim):
		return "%s%c %s%c %s%c %s%c %s%c %s%c %s%c %s" % (self.id, delim, self.type, delim, self.state, delim, self.entity, delim, self.subject, delim, self.place, delim, self.price, delim, self.date)

	def __str__(self):
		return self.stringify(',')


