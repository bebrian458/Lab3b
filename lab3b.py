import sys #For command line args

def main():
	print "The input file name is:", arg1


if __name__ == '__main__':
	try:
		arg1 = sys.argv[1]
		main()
	except IndexError:
		print "Invalid arguments. Usage: lab3b <filename.csv>"
        sys.exit(1) 
	