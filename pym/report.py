import datetime
import os

MAIN_FILE_NAME = "new-processes.csv"

class Report(object):
	def __init__(self, folder_path):
		today = datetime.date.today()
		filename = today.strftime("%Y%m%d") + "-" + MAIN_FILE_NAME
		self.file_path = os.path.join(folder_path, filename)
		#self.folder_path = folder_path
	def append(self,entity_id, entity_name, dict_of_processes):
		"""Append processes to a centralized file listing all new processes"""
		if len(dict_of_processes) > 0:
			#file_path = os.path.join(self.folder_path, MAIN_FILE_NAME)
			file_input = open(self.file_path,'a') # will append at this end of the file and will create the file if does not exist
			file_input.write(entity_id + " - " + entity_name + "\n")
			for p in dict_of_processes.itervalues():
			    file_input.write(p.stringify(';'))
			    file_input.write('\n')
			file_input.write('\n')
			file_input.close()


