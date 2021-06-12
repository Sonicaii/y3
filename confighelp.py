import sys, os, ctypes

thisdir = os.path.dirname(sys.argv[0])
arged = [not len(sys.argv) < i for i in range(2, 5)]
mode = (False if sys.argv[1] == "-" else True) if arged[0] else (False if input("Add or remove prefix (+/-)\n") == "-" else True)
pre = (sys.argv[2] if sys.argv[2][-1] == "_" else sys.argv[2] + "_") if arged[1] else input(("Module prefix (try to keep under 3 letters)" if mode else "Prefix to remove")+" don't include underscore\n") + "_"
arg = " ".join(sys.argv[3:]) if arged[2] else input("Path or name of cfg file:\n")
original = ""

# os.path.splitext()[1] == ".cfg"
# [-4:] == ".cfg"

# print(os.path.isfile(arg), os.path.splitext(arg), arg)

def checkfile(file, manual_input=False, printing=False):

	if os.path.isfile(file) and file[-4:] == ".cfg":
		return file
	elif os.path.isfile(file + ".cfg"):
		return file + ".cfg"
	elif not manual_input:
		files = [0] # 0th value is saved for "exit" option
		
		for entry in os.scandir():
			if entry.is_file() and entry.name[-4:] == ".cfg":
				files.append(entry.name)
		
		if files == [0]:
			print("No .cfg files in", __file__)
			return False
		
		print(file, "not found\nWhich cfg to edit?\n0 : Exit")
		i = 1
		for file in files[1:]:
			print(i, ":", file)
			i += 1
		
		answer = input()
		
		checked = checkfile(answer, True)
		
		if answer == "0" or answer == "":
			return False
		elif checked:
			return checked
		elif answer.isnumeric():
			if int(answer) < len(files):
				if int(answer) < 0:
					print("Invalid option")
					return False

				return checkfile(files[int(answer)])
		return False
	else:
		if printing: print("Not a valid file")
		return False


def cut_front(line):
	for i in range(len(line)):
		letter = line[i]
		if letter == "/":
			if line[i+1] == "/":
				return (line[:i], line[i:].replace("\n", ""), False) #  tuple
		elif not(letter.isspace() or letter == ";"):
			# break
			return [line[:i], line[i:], True] # list
	return ("","",False)


def cut_mid(line):
	last_split_point = 0
	new = []

	j = 0
	for i in range(len(line)):

		if i >= j and (line[i].isspace() or line[i] == ";"):
			if i+1 == len(line):
				last_split_point = j
				continue
			new.append(line[last_split_point:i])
			spaces = line[i]
			j = i+1
			
			while line[j].isspace() or line[j] == ";":
				spaces += line[j]
				j += 1

			new.append(spaces)
			last_split_point = j
	
	new.append(line[last_split_point:])
	return new



def deobfuscate(text, re=False):

	for i in range(len(text)):
		if "\"" in text[i]:
			text[i] = [text[i][:text[i].find("\"")],text[i][
				text[i].find("\"")+1:
				text[i].find("\"", text[i].find("\"")+1)
			]]
			
		else:
			text[i] = text[i].split(";")

	if not re:
		for i in text:
			print(deobfuscate(i, re=True))
	else:
		return text

def get_aliases(text):
	cleaned = []
	for line in text:
		cleaned.append(cut_front(line))

	alias_list = []
	for left, right, line_type in cleaned:
		if line_type and right[:5] == "alias":
			pure_alias = cut_mid(right)[2]
			if pure_alias[0] in ["+", "-"]:
				pure_alias = pure_alias[1:]
			alias_list.append(pure_alias)

	return set(alias_list)


def quick_alias(text):
	for line in text:
		if "alias" in line:
			pos = line.find("alias")
			while pos != -1:
				if (
					(line[pos-1].isspace() or line[pos-1] in [";", "\""])
					and
					(line[pos+5].isspace())
				):

					pos+=5
					while line[pos].isspace() or line[pos] in [";", "\""]:
						pos+=1
					startname = pos
					while not (line[pos].isspace() or line[pos] in [";", "\""]):
						pos+=1
					endname = pos

					if line[startname] in ["+","-"]:
						yield line[startname+1:endname]
					else:
						yield line[startname:endname]

				pos = line.find("alias", pos+1)
				


if __name__ == "__main__":
	original = checkfile(arg, printing=True)
	
	if not original:
		exit()

	original_file = open(original, "r")
	original_text = original_file.readlines()
	new_text = "".join(original_text)

	for i in set(quick_alias([line.replace("\n", "") for line in original_text])):
		pos = new_text.find(i)

		while pos != -1:
			
			show = False
			if (
				(new_text[pos-1].isspace() or new_text[pos-1] in [";", "\"", "+", "-"])
				and
				(new_text[pos+len(i)].isspace() or new_text[pos+len(i)] in [";", "\""])
			):
				if mode:
					new_text = new_text[:pos]+pre+i+new_text[pos+len(i):]
				else:
					new_text = new_text[:pos]+i[len(pre):]+new_text[pos+len(i):]

			pos = new_text.find(i, pos+1)

ask_text = """Output options:\n(can take multiple inputs separated by spaces)\n0 : Exit\n""" \
"""1 : Output into console\n2 : Output to separate file\n""" \
"""3 : Rewrite original file""" + "\n4 : Copy to clipboard (Windows only)\n" if os.name == "nt" else "\n"

inputs = input(ask_text).split()
opts = {"1", "2", "3", "4"}

# while False not in [o in opts for o in option]:
for option in inputs:
	if option == "1":
		print(new_text)
	elif option == "2":
		if arged:
			filename = input("Name of new file?")
			while checkfile(filename, True):
				print("File already exists")
				filename = input("Name of new file?")

			filename += ".cfg" if filename[:-4] != ".cfg" else ""
			f = open(filename, "x")
			f.write(new_text)
			f.close()

		else:
			if sys.version_info.major == 2:
				from Tkinter.tkFileDialog import asksaveasfile
			else:
				from tkinter.filedialog import asksaveasfile

			f = asksaveasfile(mode="x", defaultextension=".cfg")
			f.write(new_text)
			f.close()
	elif option == "3":
		if args:
			if input("Are you sure? yes/no") != "yes":
				print("did not Rewrite")
				break
		f = open(original, "w")
		f.write(new_text)
		f.close()
		print("overwrote")
	elif option == "4" and os.name == "nt":

		GMEM_DDESHARE = 0x2000
		CF_UNICODETEXT = 13
		d = ctypes.windll # cdll expects 4 more bytes in user32.OpenClipboard(None)
		if sys.version_info.major == 2:  # Python 2
			if not isinstance(new_text, unicode):
				new_text = new_text.decode('mbcs')
		else:
			if not isinstance(new_text, str):
				new_text = new_text.decode('mbcs')
		d.user32.OpenClipboard(0)
		d.user32.EmptyClipboard()
		hCd = d.kernel32.GlobalAlloc(GMEM_DDESHARE, len(new_text.encode('utf-16-le')) + 2)
		pchData = d.kernel32.GlobalLock(hCd)
		ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(pchData), new_text)
		d.kernel32.GlobalUnlock(hCd)
		d.user32.SetClipboardData(CF_UNICODETEXT, hCd)
		d.user32.CloseClipboard()

		print("copied to clipboard")

	if len(inputs) <= 1:
		break

	inputs = input().split()
	if not option:
		inputs = input(ask_text).split()
	
	original_file.close()
