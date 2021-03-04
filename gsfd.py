'''
Contains various functions for parsing strings and files with regex, as well as regexes I made and other utility stuff. The name of this module stands for "Grep Sed Find Duplicates".

grep: a semi-functional workalike of the grep function in Linux for finding regex and
	other strings in files. Just use Notepad ++ to do this- it's easier.
timeit: a function for easily timing other functions and comparing their outputs. Can choose how many loops to run. This doesn't work very well.
regex_by_groups and regex_shrinker: These try to use a re module function to find a regex pattern in a string.
	If they fail, they iteratively shrink the regex until they find a match or the regex vanishes.
crackdate: an implementation of regex_by_groups with a regex that tries to match valid dates in the 21st and 20th century, and matches only the year or only the year and month if a full match fails.

nanregex: a regular expression that finds strings commonly used as standins for "NaN" (not a number)

datestr: a regular expression that finds dates in the 20th and 21st century and rejects most invalid dates.

numstr: Matches all real numbers.

splitBefore: splits a string before each index in a list of indices.
insertBefore: inserts another string into a string before each index in a list of indices.
'''
import re, os, time
pizzabeer="1!! Bob bought -2.34 pizzas, and I have -76 beers now\n. HODOR 55. I am 10\n I eat many fro8l a8 8b 9" #pizzabeer exists for testing regular expressions
timeregex=re.compile('(\d{1,2}):(\d\d) ([ap]m)\s?',re.I)
def timeTo24hr(tstring):
	'''Converts an AM/PM time to a 24hr time'''
	try:
		parts=re.findall(timeregex, tstring)[0]
	except:
		return tstring+" is not an AM/PM formatted time."
	if re.match('am',parts[2], re.I):
		return parts[0].zfill(2)+':'+parts[1]
	elif re.match('pm',parts[2],re.I):
		return str(int(parts[0])+12)+':'+parts[1]

def getCurDateStr():
	t=time.localtime()
	return str(t[1]).zfill(2)+str(t[2])+str(t[0])[2:]

def splitBefore(string,locations):
	'''Creates a list of substrings of string, cut before each of the indices in the
iterable locations.
Example: splitBefore('20150412',[4,6]) would return ['2015','04','12']'''
	last=0
	new=[]
	for loc in locations:
		new.append(string[last:loc])
		last=loc
	return new+[string[loc:]]

def insertBefore(sep,string,locations):
	'''Inserts the string sep into string before each of the index numbers in the iterable locations.
Example: insertBefore('/','20150412',[4,6]) would return '2015/04/12' '''
	return sep.join(splitBefore(string,locations))

regex_cracker=re.compile("(\(.+?\)|\[.+?\]|\{\d*\,\d*\}|\+)")
#the regex_cracker breaks other regexes into pieces enclosed by [], (), or {}, and also
#cuts off + signs
textTypeFiles = "\.(txt|js|htm[l]?|py|css|csv)$"
numstr='\-?\d+\.?\d*' #match all numbers, both integers and floats, negative and positive
emailPattern='[\w\.|\w]*\w@(?:[\w\.|\w]*\w\.)[a-z]{2,4}'
emailSplit='([\w\.|\w]*\w)@((?:[\w\.|\w]*\w\.)[a-z]{2,4})'
datestr=re.compile("(19\d\d|20\d\d)" #year in 20th or 21st century
	"[/\-\\\]?" #\, |, or - separator
	"(0[1-9]|1[012])" #month
	"[/\-\\\]?(0[1-9]|[12]\d|3[01])") #Another separator and the day.
test_dates=['2015-02-34','-13','2000-14-15','1995\\04/03','2014-10-17',
'1910-00-15','2020/05/00']
nanregex=re.compile('(?:^$|\-|na[n]?|none)',re.I) #^$ matches the empty string
#The nanregex should be used with re.fullmatch to find things that are commonly used
#to indicate missing numeric data.
classnameregex="\<class \'?([\w\.]+)\'?\>" #that's the basic format of the string form of class names.

thousands="[\D+|^]([1-9](?:\d){1,2})(\.)?(?(2)\d*|$)" #match numbers with a thousands separator.
#the thousands regex does not currently work as intended- it's a work in progress.
['13423.324', 'a13.92', 'dsdfs', '03423.43', '353254545', '132']
def funcname(func):
	'''Mostly useful for running functions on arbitrary inputs with the eval(string) function.'''
	return re.findall("function <?(\w+)>?",str(func),re.I)[0]

def timeit(func,Input,loops=1,verbose=False):
	'''func: a function.
Input: a tuple of args for func.
returns: a tuple(average_time, time_std_dev, output of func(Input)
loops: How many times you want to evaluate func(Input). The time returned is the sum of the time required for all the
	loops.
verbose: Whether you want to print out a short description of the outcome.

TODO: Figure out why timeit is acting weird and refusing to use most functions when it's imported from here. 
You may have to actually paste the code directly into the IDE for this function to work
	'''
	name=funcname(func)
	try:
		arg=name+str(tuple(Input)) #convert input to tuple if it's already an iterable
	except TypeError: #Input is not an iterable, put it inside a tuple
		arg = name+"("+str(Input)+")"
	times=[]
	for i in range(loops):
		t1=time.time()
		out=eval(arg)
		times+=[time.time()-t1]
	t_mu=sum(times)/loops
	t_sd=sum([(t-t_mu)**2/loops for t in times])**0.5
	if verbose:
		print("{0:1.3e} +/- {1:2.1e} seconds per loop required for {2} to process input over {3} loops.".format(t_mu,t_sd,name,loops))
	#the {0:1.3e} means to take args 0:1 (the first arg from the format args, and format it in scientific notation (e)
	#with three sigfigs after the decimal point.
	return t_mu,t_sd,out

#encodings taken from https://stackoverflow.com/users/1709587/mark-amery's 
#answer to the question at https://stackoverflow.com/questions/1728376/get-a-list-of-all-the-encodings-python-can-encode-to

encodings = [None, #just use the default encoding method of Python's open() function.
	'utf_8',
	'utf_8_sig',
	'utf_32',
	'latin_1',
	'utf_32_be',
	'utf_32_le',
	'utf_16',
	'utf_16_be',
	'utf_16_le',
	'utf_7',
    'ascii',
  'big5',
 'big5hkscs',
 'cp037',
 'cp273',
 'cp424',
 'cp437',
 'cp500',
 'cp720',
 'cp737',
 'cp775',
 'cp850',
 'cp852',
 'cp855',
 'cp856',
 'cp857',
 'cp858',
 'cp860',
 'cp861',
 'cp862',
 'cp863',
 'cp864',
 'cp865',
 'cp866',
 'cp869',
 'cp874',
 'cp875',
 'cp932',
 'cp949',
 'cp950',
 'cp1006',
 'cp1026',
 'cp1125',
 'cp1140',
 'cp1250',
 'cp1251',
 'cp1252',
 'cp1253',
 'cp1254',
 'cp1255',
 'cp1256',
 'cp1257',
 'cp1258',
 'cp65001',
 'euc_jp',
 'euc_jis_2004',
 'euc_jisx0213',
 'euc_kr',
 'gb2312',
 'gbk',
 'gb18030',
 'hz',
 'iso2022_jp',
 'iso2022_jp_1',
 'iso2022_jp_2',
 'iso2022_jp_2004',
 'iso2022_jp_3',
 'iso2022_jp_ext',
 'iso2022_kr',
 'iso8859_2',
 'iso8859_3',
 'iso8859_4',
 'iso8859_5',
 'iso8859_6',
 'iso8859_7',
 'iso8859_8',
 'iso8859_9',
 'iso8859_10',
 'iso8859_11',
 'iso8859_13',
 'iso8859_14',
 'iso8859_15',
 'iso8859_16',
 'johab',
 'koi8_r',
 'koi8_t',
 'koi8_u',
 'kz1048',
 'mac_cyrillic',
 'mac_greek',
 'mac_iceland',
 'mac_latin2',
 'mac_roman',
 'mac_turkish',
 'ptcp154',
 'shift_jis',
 'shift_jis_2004',
 'shift_jisx0213',
 "idna",
 "mbcs",
 "oem",
 "palmos",
 "punycode",
 "raw_unicode_escape",
 "rot_13",
 "undefined",
 "unicode_escape",
 "unicode_internal",
 "base64_codec",
 "bz2_codec",
 "hex_codec",
 "quopri_codec",
 "uu_codec",
 "zlib_codec",
 'undefined' #always raises an exception
 ]
def get_lines_best_encoding(fname, print_on_exception = False):
	for enc_num,encoding in enumerate(encodings):
		try:
			with open(fname,'r', encoding = encoding) as f:
				#print(encoding,end=', ')
				return f.readlines() #we found a good encoding, stop trying new ones.
		except:
			pass #keep trying other encodings
	if enc_num >= len(encodings)-1:
		if not print_on_exception:
			raise UnicodeDecodeError("Could not find the encoding for this file.")
		print("Could not find the encoding for this file.")

def grep(Input):
	"""
The grep filter searches a .txt file for a particular pattern of characters,
and displays all lines that contain that pattern. The pattern that is searched
in the file is referred to as the regular expression
(grep stands for globally search for regular expression and print out).

Format for Input:
[options] 'pattern' /[filename or containing directory]

By default, returns a dict mapping filenames to a list of lines in that file
	where the regex is matched. Some options change the return type.

IMPORTANT: You NEED to have exactly one space between the options block and
the pattern block, the pattern block MUST be enclosed by '', there MUST
be exactly one space between the pattern block and the filename block, and
the filename block must be preceded by /.

Options Description
-f : Searches only the filenames of text-type files for matches to the regex. 
	(returns list)
-a : Special case of -f. Matches regex in filenames of all files, not just 
	text-type files.
-c : This prints only a count of the lines that match a pattern 
	(returns dict)
-h : Display the matched lines, but do not display the filenames. 
	(returns list)
-i : case-insensitive match
	(does not affect return type)
-l : Displays list of a filenames only. 
	(returns list)
-n : Display the matched lines and their line numbers. 
	(returns dict mapping to tuples)
-v : Matches all the lines that DO NOT match the pattern
	(does not affect return type)
-w (NOT IMPLEMENTED): Match whole word
-o (NOT IMPLEMENTED): Print only the matched parts of a matching line,
	 with each such part on a separate output line.
-r : Recursively searches through the entire directory tree beneath a given
	directory (all subdirectories within that directory as well as the 
	directory itself)
	(does not affect return type)
	"""
	grepParser = re.compile(("(?P<options>(?:-[a-z]\s+)*)"
						  "'(?P<regex>.+)' "
						  "(?P<File_or_containing_directory>/.+)"))
	parsedInput = re.findall(grepParser, Input)[0]
	options = list(map(lambda x: x.lower().strip(),
					filter(lambda x: len(x)>0,
						   re.split("(?:\s+|^)-",parsedInput[0])
						   ))) 
	#split the options substring into letters, convert to lower-case
	
	regex = parsedInput[1]
	dirName = os.path.abspath(str.join("\\", parsedInput[2].split('/')[1:]))
	
	#print(options,regex,dirName)

	c = ('c' in options)
	h = ('h' in options)
	i = ('i' in options)
	l = ('l' in options)
	n = ('n' in options)
	v = ('v' in options)
	w = ('w' in options)
	o = ('o' in options)
	r = ('r' in options)
	f = ('f' in options)
	a = ('a' in options)

	goodFiles = {}
	badFiles = {}
	goodFilesLineNums = {}
	badFilesLineNums = {}
	
	if i:
		goodness_condition = lambda x: re.search(regex,x,re.I)
	else:
		goodness_condition = lambda x: re.search(regex,x)
	
	dirIsFile = (re.search("\.[a-z]{2,5}$", dirName,re.I) is not None)
	if not dirIsFile:
		if r:
			filesToSearch=[]
			for root, dirs, files in os.walk(dirName):
				for file in files:
					filesToSearch.append(os.path.join(root, file))
		else:
			filesToSearch = os.listdir(dirName)
		textTypeFiles = "\.(txt|py|ipynb|json|js|htm[l]?|css|[ct]sv|r|Rmd|sql|fwf)$"
		for file in filesToSearch:
			file = os.path.join(dirName,file)
			if f and a:
				if goodness_condition(file):
					goodFiles.setdefault(file,0)
				else:
					badFiles.setdefault(file,0)
			elif (re.search(textTypeFiles, file)):
				if f:
					if goodness_condition(file):
						goodFiles.setdefault(file,0)
					else:
						badFiles.setdefault(file,0)
					continue
				lines = get_lines_best_encoding(file,print_on_exception=True)
				for ind in range(len(lines)):
					line=lines[ind]
					if goodness_condition(line):
						goodFiles.setdefault(file, [])
						goodFiles[file].append(line)
						goodFilesLineNums.setdefault(file, [])
						goodFilesLineNums[file].append((ind, line))
					else:
						badFiles.setdefault(file, [])
						badFiles[file].append(line)
						badFilesLineNums.setdefault(file, [])
						badFilesLineNums[file].append((ind, line))

	if dirIsFile:
		if f:
			if goodness_condition(file):
				goodFiles.setdefault(file,0)
			else:
				badFiles.setdefault(file,0)
		file=dirName
		lines = get_lines_best_encoding(file,print_on_exception=True)
		for ind in range(len(lines)):
			line = lines[ind]
			if goodness_condition(line):
				goodFiles.setdefault(dirName, [])
				goodFiles[dirName].append(line)
				goodFilesLineNums.setdefault(dirName, [])
				goodFilesLineNums[dirName].append((ind, line))
			else:
				badFiles.setdefault(file, [])
				badFiles[file].append(line)
				badFilesLineNums.setdefault(file, [])
				badFilesLineNums[file].append((ind, line))
	
	if f:
		if v:
			return list(badFiles.keys())
		return list(goodFiles.keys())
	if v:
		if n:
			return badFilesLineNums
		return badFiles
	if c:
		fileLineCounts={}
		for key in goodFiles:
			fileLineCounts[key] = len(goodFiles[key])
		return fileLineCounts
	if h:
		linelist=[]
		linelistWithNums=[]
		for key in goodFiles:
			for ind in range(len(goodFiles[key])):
				line = goodFiles[key][ind]
				linelist.append(line)
				linelistWithNums.append((ind, line))
		if n: 
			return linelistWithNums
		return linelist
	if n:
		return goodFilesLineNums
	if l:
		return list(goodFiles.keys())
	return goodFiles

def sed(pattern, replacement, fileIn, fileOut='', recursive=False):
	"""
Reads fileIn and writes to fileOut (creating it if necessary).
fileOut is just fileIn, except every instance of the pattern string is replaced
by the replacement string.
If an error occurs while opening, reading, writing or closing files,
your program should catch the exception, print an error message, and exit.
Solution: http://thinkpython2.com/code/sed.py.
If "recursive" is True, fileIn should be a folder name, and sed will use os.walk
to search the folder's dir and attempt to apply the substitution to every
plaintext file it finds.
meat=re.compile('meat', flags=re.I)
Test for non-recursive form: gsfd.sed('ludd', 'eehive', './/delicious//bluddText inc15.txt')
Test for recursive form: gsfd.sed(meat, 'tofu', './/delicious', recursive=True)
Test for non-recursive form with name choice: gsfd.sed('ludd', 'eehive', 'bluddNew.txt', './/delicious//bluddText inc15.txt')
Test for error handling in recursive form: gsfd.sed('dfd', '23rer', '33254223432', recursive=True)
Test for error handling in non-recursive form: gsfd.sed('dfd', '23rer', '33254223432')
zargothrax=gsfd.grep("-i -r 'argothrax' /C:/Users/molso/Documents/html stuff")
	"""
	if not isinstance(pattern, re.Pattern):
		pattern = re.compile(pattern, flags=re.MULTILINE)
		print("""gsfd.sed works better if you feed it patterns made by re.compile with the
			re.MULTILINE flag.""")
	if not fileOut:
		fname_type=re.findall('(.+)(\.(?:txt|js|htm(?:l)?|py|css|csv)$)',fileIn)
		if not fname_type:
			return None
		fname=fname_type[0][0]
		type=fname_type[0][1]
		fname_out=fname+"_sed"+getCurDateStr()
		fileOut=fname_out+type
	try:
		with open(fileIn) as fin:
			lines=fin.readlines()
			finStr=str.join('', lines)
			foutStr=re.sub(pattern, replacement, finStr)
	except FileNotFoundError:
		print("Could not find the file", fileIn)
		return None
	with open(fileOut, 'w') as fout:
		fout.write(foutStr)
	try:
		if recursive:
			for (root, subdirs, files) in os.walk(fileIn):
				for file in files:
					sed(pattern, replacement, file)
	except:
		print("Could not find the folder", fileIn)
		return None

def md5(string, is_filename=True):
				"""
				Returns the md5 checksum of a file. If two files have the same md5
				checksum, their contents are almost certainly the same.
				"""
				import hashlib
				hash_md5 = hashlib.md5()
				if is_filename:
						with open(string, "rb") as f:
								for chunk in iter(lambda: f.read(4096), b""):
										hash_md5.update(chunk)

				else:
						hash_md5.update(string.encode())
				return hash_md5.hexdigest()

def find_duplicates(Dir, file_type='.+'):
	"""
Recursively searches the directory Dir for all files with '.file_type' as
suffix, and calculates their md5 hash values. Returns a dictionary in which
the keys are duplicated files and the values are the copies of those files.
	"""
	if not os.path.isdir(Dir):
				print("There is no directory named " + Dir)
				return {}
	tree=os.walk(Dir)
	hashList = []
	fileList = []
	for subdir, dirs, files in tree:
		for filename in files:
			if re.search('\.'+file_type+'$', filename):
				absfilename = os.path.join(subdir, filename)
				fileList.append(absfilename)
				hashList.append(md5(absfilename))
	dupDict={}
	goodInds=[] #Contains indices of duplicates already checked, to ensure
	#that each set of duplicate files has only one list of duplicates.
	for ind in range(len(fileList)-1):
		for ind2 in range(ind+1,len(hashList)):
			if hashList[ind2] == hashList[ind] and ind not in goodInds:
								relpathInd = ".\\" + os.path.relpath(fileList[ind], Dir)
								relpathInd2 = ".\\" + os.path.relpath(fileList[ind2], Dir)
								dupDict.setdefault(relpathInd, [])
								dupDict[relpathInd].append(relpathInd2)
								goodInds.append(ind2)
	return dupDict		

quantifiedWord = re.compile(r'(-?\d*\.?\d+)\s{0,2}([a-zA-Z]+)')
def wordNumExtractor(string):
	"""
	Finds every instance in a string in which a word follows a number
	with two or fewer interceding blankspace characters (tab, newline or
	space). Makes a list of lists, in which every entry in the list is
	a list where the first entry is the number (expressed as a float)
	and the second entry is the associated word.
	Example:
	string = "I have -9.43 pizzas and 23 beers and 56.223 avocados and
	90.76 artichokes and -68 bokt"
	Output = [[-9.43, 'pizzas'], [23.0, 'beers'], [56.223, 'avocados'],
	[90.76, 'artichokes'], [-68.0, 'bokt']]
	"""
	wordNums = re.findall(quantifiedWord, string)
	wordNumsFloat = []
	for Tuple in wordNums: #re.findall outputs a tuple of tuples, in which
#each member of the tuple is a ()-enclosed string called a "group. That's why
#I enclosed the number regex and the word regex in their own sets of parens.
		newWordNum = [float(Tuple[0]), Tuple[1]]
		wordNumsFloat.append(newWordNum)
	return wordNumsFloat

def numlister(string):
	"""
	Input: a string
	Output: A list of the distinct numbers in that string. Based on whether
	a given number has a "." in it, the number in the list will be either
	an int or a float.
	This implementation of the function uses regular expressions to achieve
	the same thing in 9 lines of code that took 73 lines for the version
	without regex.
	"""
	numlist_stringform=re.findall("-?\d*\.?\d+", string)
	numlist=[]
	
	for num in numlist_stringform:
		if "." in num:
			numlist.append(float(num))
		else:
			numlist.append(int(num))
	return numlist

phoneNumRegex = re.compile(r'\D(\(?\d{3})(\) |-|\.)(\d{3})(\.|-)(\d{4})')
def phoneNumFinder(string):
	"""Given a string "string", outputs a list of every phone number in the
	string that matches the regex '\D(\(?\d{3})(\) |-|\.)(\d{3})(\.|-)(\d{4})'
	"""
	#Recall that the "pipe" character "|" acts as an "or" operator to choose
	#between options like ") " or "-" or ".". Technically | is the bitwise
	#"or" operator.
	#\d is any digit.
	#{n} after any group lets you choose a number of repititions of that
	#group.
	#\D is any character OTHER THAN a numeric digit 0-9.
	#Alternatively you can use the "^" character, which indicates that anything
	#OTHER THAN the following pattern should be matched. So ^[a-zA-Z] would
	#match anything that's not a letter of the alphabet.
	#Remember you must use the escape character "\" before any special char
	#like a paren or . or *.
	phoneNumTupleList = phoneNumRegex.findall(string)
	phoneNumList = []
	for Tuple in phoneNumTupleList:
		currentPhoneNum = ""
		for group in Tuple:
			currentPhoneNum += group
		phoneNumList.append(currentPhoneNum)
	return phoneNumList

def addToAllInts(string, increment=1, is_filename=True, change_Floats=False):
	'''
	Finds all blankspace-surrounded integers in a file or string
	and adds a chosen number to each of them. If the input was a
	string, returns the altered string.
	If the input was a filename, creates a new file with an
	appropriate ascension number appended to the original filename.
	If change_Floats is True, this function will also increase most floating
	point numbers in the file by the chosen increment.
	'''
	words=[]
	if is_filename:
		with open(string) as f:
			lines=f.readlines()
			for line in lines:
				words+=line.split()
	else:
		words=string.split()
	newWords=words.copy()
	if change_Floats:
		for n in range(len(words)):
			w=words[n]
			nums=re.findall('\d+', w)
			if len(nums) > 0:
				wordNoNum=w[len(nums[0]):]
				num= w[:len(nums[0])]
				if not re.fullmatch('\d+',num): continue
				if len(num)>0:
					newnum=str(int(num)+increment)
					w=newnum+wordNoNum
					newWords[n]=w

	else: #Change only integers
		for n in range(len(words)):
			w=words[n]
			if re.fullmatch('\d+',w):
				newWords[n]=(str(int(w)+increment))

	output=''
	for n in range(len(newWords)-1):
		output+= newWords[n]+' '
	output+=newWords[-1]
	if is_filename:
		new_filename=string[:-4]+' inc'+str(increment)+'.txt'
		with open(new_filename, 'w') as f:
			f.write(output)
		print("Successfully wrote a new file, " + new_filename +" with most nums of the appropriate type changed by the chosen increment.")
	else:
		return output

def regex_split(regex,flags=0):
	'''Create a sorted list of progressively smaller regexes derived from regex,
broken at + signs and enclosing (), [], and {}. 
You can also include flags if you want.'''
	if type(regex)==re.Pattern:
		regex=regex.pattern
	parts=regex_cracker.split(regex)
	seq=[''.join(parts[:i]) for i in range(len(parts))]
	return [regex]+sorted(seq,key=len,reverse=True)
	# if type(regex)==re.Pattern:
		# regex=regex.pattern
	# parts=regex_cracker.split(regex)
	# seq=[re.compile(regex)]
	# for i in range(len(parts)):
		# try:
			# pat=re.compile(parts[:i+1],flags=flags)
		# except:
			# continue
		# seq.append(pat)
	# return sorted(seq,key=lambda x: len(x.pattern),reverse=True)

def regex_by_groups(regex,string,re_func=re.findall,flags=0):
	'''Given a regex with one of more groups, create a list of successively
smaller regexes, starting with the original regex and removing groups
one by one.
After creating this list, try using the chosen re_func (from re module) on the
string with each of the regexes in the sequence until it finds one that works.
The idea of this function is to make it easy to implement reasonably quick
partial matching of complex regexes, so that you can get the best one.
This is generally faster than regex_shrinker, and it tends to produce more useful matches as well
based on some of the limited testing I've done.
	'''
	seq=regex_split(regex)
	i=0
	while seq[i]:
		reg=seq[i]
		try:
			if flags:
				match=re_func(reg,string,flags)
			else:
				match=re_func(reg,string)
		except re.error:
			i+=1
			continue
		i+=1
		if not match:
			continue
		else:
			return match

def regex_shrinker(regex,string,re_func=re.findall,flags=0):
	'''Tries to find match(es) in string with regex, then iteratively shrinks the regex
until the diminished regex matches something or the regex shrinks to length 1.
Compare to regex_by_groups, which is faster under some circumstances (like with the datestr regex)
but also slower under some circumstances.'''
	if type(regex)==re.Pattern:
		L=len(regex.pattern)
		reg=regex.pattern
	else:
		L=len(regex)
		reg=regex[:]
	for i in range(1,L-1):
		try:
			match=re_func(reg,string,flags)
			reg=reg[:-i]
			if match:
				return match
		except:
			reg=reg[:-i]
			pass

def crackdate(string, sep_month_and_day=True):
	'''string: a string encoding a date
Attempts to return a tuple (year,month, and day). 
If any part is invalid, that part and all subsequent parts are replaced with ''.
sep_month_and_day: instead tries to return a 2-tuple (year, month+day)
Example:
	crackdate("1952\\02-30") returns ('1952','02','30') but crackdate("20561235")
	returns ('2056','12',''), crackdate('20251523') returns ('2025','',''),
	and crackdate('-234') returns ('','','')
	'''
	match=regex_by_groups(datestr,string,re.findall)
	if not match:
		return '','',''
	elif type(match[0])==str:
		return (match[0],'','')
	else:
		if len(match[0])==3 and not sep_month_and_day:
			match[0]=(match[0][0],)+(''.join(match[0][1:]),)
			return match[0]
		return match[0]+tuple(['' for i in range(3-len(match[0]))])
