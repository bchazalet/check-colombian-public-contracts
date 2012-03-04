import datetime
import os

MAIN_FILE_NAME = "new_processes"

class Report(object):
	def __init__(self, folder_path):
		self.today = datetime.date.today().strftime("%Y%m%d")
		filename = self.today + "_" + MAIN_FILE_NAME
		existing_files = filter(isFileFromToday, os.listdir(folder_path))
		self.file_path = os.path.join(folder_path, (filename + "-" + str(len(existing_files)+1) + ".csv"))
		#self.folder_path = folder_path
		self.created = False

	def append(self,entity_id, entity_name, processes):
		"""Append processes to a centralized file listing all new processes"""
		if len(processes) > 0:
			#file_path = os.path.join(self.folder_path, MAIN_FILE_NAME)
			file_input = open(self.file_path,'a') # will append at this end of the file and will create the file if does not exist
			file_input.write(entity_id + " - " + entity_name + "\n")
			for p in processes:
			    file_input.write(str(p))
			    file_input.write('\n')
			file_input.write('\n')
			file_input.close()
			self.created = True


def isFileFromToday(file):
	today = datetime.date.today().strftime("%Y%m%d")
	return file.startswith(today)


