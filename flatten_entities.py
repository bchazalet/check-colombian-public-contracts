#!/usr/bin/python -tt

def main():
	file_in = "ePublicando.js"
	#file_in = "list-of-entities.txt"
	file_out = "list-of-entities2.txt"
	file_input = open(file_in, 'r')
	file_output = open(file_out, 'w')
	# First thing on the line is the id (before the first semicolumn)
	nb = 0
	for line in file_input:
		all_lines = line.split('"')	
		for l in all_lines:
			print l
			if (nb%2) == 1:
				print "we keep"	
				file_output.write(l)
				file_output.write("\n")
			else:
				print "we throw"
			nb += 1
	
	file_input.close()
	file_output.close()


if __name__ == '__main__':
	main()
