from confighelp import *

if __name__ == "__main__":
	thisdir = os.path.dirname(sys.argv[0])
	arged = [not len(sys.argv) < i for i in range(2, 5)]
	mode = (False if sys.argv[1] == "-" else True) if arged[0] else (False if input("Append or remove command (+/-)\n") == "-" else True)
	arg = " ".join(sys.argv[3:]) if arged[2] else input("Path or name of cfg file:\n")
	
	original = checkfile(arg, printing=False)
	
print(locals())
