import re,csv,collections, datetime, pyperclip,math, sys
import pandas as pd, matplotlib.pyplot as plt, numpy as np
import binarySearch as bis #my module, has some useful binary search functions
from dateutil import parser #for parsing dates, duh
import gsfd	#my module, has various regular expressions and things for parsing regular expressions

def bool_parse(entry):
	'''Tests if something is a bool or a common string representation of a bool'''
	try:
		if type(entry)==bool:
			return True
		if type(entry)==str:
			return re.fullmatch('true|false|yes|no|y|n|T|F',entry,re.I)
	except:
		pass
	return False

class Bool(object):
	'''A callable class that returns true if something is equal to the bool True, or is a common
string representation for the boolean True, (yes, true,t,y, and the other cases of those words.)
truth_names is an optional iterable containing strings that represent the boolean value True.
If truth_names is not null, instead tests if entry is equal to one of those strings
	or if it already has the boolean value True'''
	truth_names=[]
	casefold=False
	def __new__(self,entry): 
		#this is the method that returns a new instance, as opposed to __init__, which sets up the
		#attributes of a new instance that's already been created.
		if type(entry) in [int, bool]:
			return (entry==True)
		if type(entry)==str:
			if not self.truth_names:
				return (re.fullmatch('true|yes|y|t',entry,re.I) is not None)
			else:
				for name in Bool.truth_names:
					if Bool.casefold and entry.casefold()==name.casefold():
						return True
					if not Bool.casefold and entry==name:
						return True
				return False
		else:
			return False
	def setTruthNames(names=[],casefold=True):
		'''Select which keywords are interpreted by the Bool class as corresponding to the
	boolean value True.
casefold: If True, will match any word that has the same sequence of letters as a keyword, 
	regardless of the cases of those letters.
By default, those keywords are yes, true, t, y, and all other cases of those words.
		'''
		Bool.truth_names=names
		Bool.casefold=casefold

class dframe(object):
	'''A bare-bones implementation of a data-frame, intended to preserve
as much dictionary functionality as possible.
Assumes colnames a list of strings (keys), types a list of data types (e.g., int, str)

The dframe attempts to coerce new entries for a given attribute into
	the type defined for that attribute at the dframe's creation.
	If the type for a column is None, the dframe coerces all entries to strings.

Ways to make dframes:
	0. Just making your own by specifying column names and types, then adding rows
		one at a time.
	1. Reading a list of sublists (where each sublist will become a row in the dframe)
		with readlists.
	2. Reading a dict (mapping keys to lists) with readdict.
	3. Reading a string with readstring
	4. Reading a csv file with readcsv
	5. Reading the contents of the clipboard with readclipboard

Major operations:
	0. Seeing the column names with keys() and types with getTypes
	1. Selecting a range of rows with the same [row_range,col_range] slicing method
		as a matrix or with the rows and cols methods.
	2. Adding new columns with addcol(name,data,type) and removing columns with remove.
	3. Adding rows with append.
	4. Filtering data with select(column,thing_to_filter_for)
	4. Setting types with setType, which automatically changes the data in that column.
	5. Finding unique entries with unique and uniques_to_rows
	6. sorting the dframe by the contents of one column with sort_by.
	7. Splitting columns with split(column,sep,to_names)
	8. Joining columns as strings with stringjoin.
	9. Doing an SQL-style inner join with another dframe using join.
	'''
	def __init__(self, colnames=[],types=[]):
		self.attrs={}
		self.types=types
		for a in range(len(colnames)):
			self.attrs[colnames[a]]=[]
			if len(types)<=a:
				self.types.append(str)
	def __getitem__(self,tup):
		#This lets you access columns i:j, rows m:n of dframe blah by saying blah[m:n,i:j]
		if type(tup)==str:
			return self.attrs[tup]
		row_slice=tup[0]
		col_slice=tup[1]
		if type(col_slice)==str:
			col_slice=self.keys().index(col_slice)
		if type(row_slice)==None:
			row_slice=slice(0,len(self))
		if type(col_slice)==None:
			col_slice=slice(0,len(self))
		if type(row_slice)==int and type(col_slice)==int:
			return self.attrs[self.keys()[col_slice]][row_slice]
		if type(row_slice)==int:
			row_slice=slice(row_slice,row_slice+1)
		if type(col_slice)==int:
			col_slice=slice(col_slice,col_slice+1)
		new=dframe(self.keys()[col_slice],self.types[col_slice])
		for c in new.keys():
			new.attrs[c]=self.attrs[c][row_slice]
		return new
	def getTypes(self,i=None):
		'''Returns the list of types for this dframe, or a string of the
		class name of the i_th type in this dframe, 
		or the type corresponding to the named column.'''
		if i is not None:
			if type(i)!=int:
				i=self.keys().index(i)
			if self.types[i]==None:
				return 'str'
			try:
				out = re.findall(gsfd.classnameregex,str(self.types[i]))
				if len(out)==0:
					out = re.findall(gsfd.classnameregex, str(type(self.types[i])))
				return out[0]
			except:
				return 'unknown'
		else:
			return self.types
	def keys(self):
		'''Returns a list of the attribute names of this dframe'''
		return list(self.attrs.keys())
	def cols(self,names, as_dict=False):
		'''Asssumes names a list/tuple of attribute names or column numbers
		Returns a dframe or dict containing just those attributes.'''
		if type(names[0])!=str: #get columns by numbers if desired
			chosen=list([self.keys()[i] for i in names])
			cho_types=list([self.types[i] for i in names])
		else: #get columns by names
			chosen=names
			cho_types=list([self.types[self.keys().index(i)] for i in names])
		if as_dict:
			return dict(zip(chosen,list([self.attrs[name] for name in chosen])))
		else:
			nu=dframe(chosen,cho_types)
			for name in nu.keys():
				nu.attrs[name]=self.attrs[name]
			return nu
	def append(self,row,na_incl=True,verbose=False):
		'''Assumes row a list, tuple, dict, or single-row dframe with the appropriate keys'''
		if type(row)==type(self):
			row=row.attrs
			for i in row:
				row[i]=row[i][0]
		if len(row)<len(self.keys()):
			if verbose:
				print("Cannot add new row with fewer attributes than dframe")
			return None
		row_incomplete=False
		og_len=len(self)
		if type(row)!=dict:
			for i in range(len(row)):
				try:
					if self.types[i] is not None:
						self.attrs[self.keys()[i]].append(self.types[i](row[i]))
					else:
						self.attrs[self.keys()[i]].append(str(row[i]))
				except (ValueError,TypeError):
					#print(ex)
					if na_incl:
						self.attrs[self.keys()[i]].append(float('NaN'))
						continue
					if verbose:
						print(str(row[i]),"is not appropriate for column",self.keys()[i],"of type",self.getTypes(i)+".")
					row_incomplete=True
					break
		if type(row)==dict:
			k=list(row.keys())
			for i in range(len(row)):
				if k[i] != self.keys()[i]:
					if verbose:
						print("Key "+k[i]+" in row's keys does not match the corresponding key in the dframe, "+self.keys()[i]+".")
					row_incomplete=True
					break
				try:
					if self.types[i] is not None:
						self.attrs[self.keys()[i]].append(self.types[i](row[k[i]]))
					else:
						self.attrs[self.keys()[i]].append(str(row[k[i]]))
				except (ValueError,TypeError):
					#print(ex)
					if na_incl:
						self.attrs[self.keys()[i]].append(float('NaN'))
						continue
					if verbose:
						print(str(row[k[i]]),"is not appropriate for column",self.keys()[i],"of type",self.getTypes(i)+".")
					row_incomplete=True
					break
		if row_incomplete:
			for key in self.keys():
				if len(self.attrs[key])>og_len:
					del self.attrs[key][-1]
	def rows(self,start=None,end=None):
		'''Return a list of dicts if no start or end defined.
		If start is a list of numbers, returns all rows with those index numbers.
		If only start is defined, returns that row as a dframe.
		If start and end are defined, returns a new dframe containing
		all rows from start to end, inclusive.'''
		if type(start) in [list,tuple] and end is None:
			nu=dframe(self.keys(),self.getTypes())
			for ind in start:
				nu.append(self[ind,:])
			return nu
		elif start is None and end is None:
			return list([dict(zip(self.keys(),list([self.attrs[a][i] for a in self.keys()]))) for i in range(len(self))])
		elif end is None and start is not None:
			return self[start,:]
		elif start is not None and end is not None:
			nu=dframe(self.keys(),self.getTypes())
			for i in range(start,end+1):
				nu.append(dict(zip(self.keys(),list([self.attrs[a][start] for a in self.keys()]))))
			return nu
		
	def addcol(self,name,vals=[],type_=None,convert_bools=False):#,truth_names=[]):
		'''Add a column to the dframe.
name: A string to serve as the column's key.
vals: A list of values to add to the column. If vals is empty or shorter than the dframe,
	the rest of the column will be populated with None.
type_: A type to apply to the column. If type_ is None, the column's data type will be inferred.
convert_bools: If True, and the column appears to contain only strings commonly used to represent
	truth or falsehood (yes, no, t, f, y, n, True, False, and other cases of those words),
	everything in the column will be coerced to a bool.
To define which words are treated as meaning True by Bool, use Bool.setTruthNames(new_names).
DEPRECATED ARG BELOW:
truth_names: An iterable, if not []. If convert_bools is True and this is not [], 
	any string matching a string in this iterable will be coerced to True, and all other entries in the
	column will be coerced to False.
		'''
		if name in self.keys():
			self.remove(name)
		if type_ is None:
			for i in range(min(len(vals),12)): #Do automatic type inference by scanning the first 12 rows
				if type_ is not str: #Once a value that doesn't seem boolean, numeric, or date-like is observed,
									 #stop doing automatic type inference and assign type=string.
					if gsfd.nanregex.fullmatch(str(vals[i])):
						continue
					elif re.fullmatch('\-?\d+',str(vals[i])):
						type_=int
					elif re.fullmatch(gsfd.numstr,str(vals[i])):
						type_=float
					elif convert_bools and bool_parse(str(vals[i])):
						type_ = Bool
					else:
						type_=str
		self.attrs[name]=[]
		for val in vals:
			try:
				self.attrs[name].append(type_(val))
			except:
				self.attrs[name].append(float('nan'))
		self.types.append(type_)
		v,b=len(vals),len(self)
		if v<b:
			for i in range(b-v):
				self.attrs[name].append(None)
		elif b<v: #cut off all values past the end of the dframe
			self.attrs[name]=self.attrs[name][:b]
	def __str__(self):
		out=''
		longest=[]
		#Find the longest string in each column, including types, column names, and entries.
		#Base the width of each column off of the length of the longest entry, but make it
		#so that each column is between 8 and 14 characters wide. Very long entries are cut off
		#with '... '.
		for i in range(len(self.attrs)):
			c=self.keys()[i]
			longest_this_row=0 #find the longest column name
			if len(c)>longest_this_row:
				longest_this_row=len(c)
			if len(self.getTypes(i))>longest_this_row: #find longest type name
				longest_this_row=len(self.getTypes(i))
			for r in self.attrs[c]:
				if len(str(r))>longest_this_row: #find longest entry in each column
					longest_this_row=len(str(r))
			longest.append(longest_this_row)
		for i in range(len(self.keys())):
			a=self.keys()[i]
			L=min(longest[i]+4,max(80//len(self.keys()),14))
			if len(a)>L-2:
				out+=a[:L-4]+'... ' #cut off long entries.
			else:
				out+=a.ljust(L) #use ljust to normalize column width.
		out+='\n'
		for i in range(len(self.types)):
			L=min(longest[i]+4,max(80//len(self.keys()),14))
			t=self.getTypes(i)
			if len(t)>L-2:
				out+=t[:L-4]+'... '
			else:
				out+=t.ljust(L)
		out+="\n"
		for i in range(len(self)):
			for j in range(len(self.keys())):
				L=min(longest[j]+4,max(80//len(self.keys()),14))
				a=self.keys()[j]
				if len(str(self.attrs[a][i]))>L-2:
					out+=str(self.attrs[a][i])[:L-4]+'... '
				else:
					out+=str(self.attrs[a][i]).ljust(L)
			out+='\n'
		return out
	def __repr__(self):
		return str(self[:8,:6]) + "\nTotal rows: "+str(len(self))+\
			". Total cols: "+str(len(self.keys()))
	def __len__(self):
		return len(self.attrs[self.keys()[0]])
	def select(self,key,func,warn_error=False):
		'''key: a column name (string) or number (int).
func: Either:
	1. a function that applies a test to each entry in that column.
	2. A value that you want to filter for (default)
	3. A list/tuple of values you want to filter for.
So if you wanted to select all rows in dframe 'blah' for which the
attribute 'name' (3rd column) had length less than 5, you'd say
blah.select('name',lambda x: len(x)<5)
or blah.select(3,lambda x: len(x)<5)
and if you wanted to select all rows in dframe 'blah' where
'name' had the value 'Bojack Horseman', you'd enter
blah.select('name','Bojack Horseman')'''
		if not callable(func):
			temp=func
			if str(func)=='nan':
				#have to include 'nan' separately.
				#float('nan') has the horrible, pathological
				#property that float('nan') != float('nan').
				#Try it if you don't believe me!
				func=lambda x: str(x)=='nan'
			elif type(func) in [tuple,list,set]:
				func=lambda x: x in temp
			else:
				func=lambda x: x==temp
		nu=dframe(self.keys(),self.getTypes())
		badrows=[]
		if type(key)!=str:
			key=self.keys()[key]
		for i in range(len(self)):
			try:
				if func(self[i,key]):
						nu.append(self[i,:])
			except: #usually exceptions happen due to a None or some other null value in the column.
				if warn_error:
					badrows.append(i)
				continue
		if warn_error and len(badrows)>0:
			print("{0} rows with invalid entries were detected. The first {1} rows with invalid entries are {2}".format(len(badrows),min(15,len(badrows)),badrows[:15]))
		return nu
	def rename(self,key,new_name):
		'''key: a name or number of an attribute
		Renames the appropriate attribute, without changing the associated data in any way.
		Warning: this will reorder the columns in the dframe. The renamed column will be at the end.'''
		if type(key)==str:
			old_name=key
		else:
			old_name=self.keys()[key]
		old_type=self.types[self.keys().index(old_name)]
		self.addcol(new_name,self.attrs[old_name],old_type)
		self.remove(old_name)
	def copy(self):
		'''Create a new dframe with the same contents. Can also make a copy with
copy_frame = this_frame[:,:]'''
		return self.cols(self.keys())
	def readlists(lists,header=None,parse_dates=False,convert_bools=False):#,truth_names=[]):
		'''Read a list of lists as a data frame. Each sublist is treated as a new row.
header: a list of column names, at least as long as each of the sublists.
If parse_dates is True, any column that is inferred by dateutil to include dates will be
	converted into datetime.datetime objects.
convert_bools: If True, and the column appears to contain only strings commonly used to represent
	truth or falsehood (yes, no, t, f, y, n, True, False, and other cases of those words),
	everything in the column will be coerced to a bool.
To define which words are treated as meaning True by Bool, use Bool.setTruthNames(new_names).
DEPRECATED ARG BELOW:
truth_names: An iterable, if not []. If convert_bools is True and this is not [], 
	any string matching a string in this iterable will be coerced to True, and all other entries in the
	column will be coerced to False.'''
		#Bool.setTruthNames(truth_names)
		reader=iter(lists)
		first6=[]
		datecols=[]
		types,maxlen=[],0
		first_truth_name_found=False
		for i in range(12):
			try:
				col=reader.__next__()
			except StopIteration:
				break
			if len(col)>len(types):
				maxlen=len(col)
				types+=[None for z in range(maxlen-len(types))]
			first6.append(col)
			for i in range(len(col)):
				if types[i] is not str: #See addcol comments for discussion on how automatic type inference is done
					if re.fullmatch(gsfd.nanregex,str(col[i])):
						continue
					elif re.fullmatch(gsfd.datestr,str(col[i])):
						if i not in datecols:
							datecols.append(i)
					elif re.fullmatch('\-?\d+',str(col[i])):
						types[i]=int
					elif re.fullmatch(gsfd.numstr,str(col[i])):
						types[i]=float
					elif convert_bools and bool_parse(str(col[i])):
						#x=bool_parse(str(col[i]))
						types[i] = Bool
						# if not truth_names:
							# if Bool(x.string):
								# if not first_truth_name_found:
									# Bool.truth_names=[]
								# first_truth_name_found=True
								# Bool.truth_names.append(x.string)
						# else:
							# Bool.truth_names=truth_names
					else:
						types[i]=str
		if not header:
			header=[str(i) for i in range(maxlen)]
		else:
			header=[str(i) for i in header]
		for c in range(maxlen):
			if re.search('\Wdate[s]?\W|^date[s]?$|^date[s]?\W|\Wdate[s]?$',header[c],re.I):
				if i not in datecols:
					datecols.append(c)
		new=dframe(header,types)
		for row in first6:
			new.append(row)
		for row in reader:
			new.append(row)
		datecols=[new.keys()[i] for i in datecols]
		if parse_dates:
			for i in datecols:
				new.setType(i,date)
				# datenames=['year','month','day']
				# if len(datecols)>1:
					# datenames=[s+str(i) for s in datenames]
				# stop=3
				# if not sep_month_and_day:
					# datenames=['year','day']
					# stop=2
				# new=new.split(i,lambda x: crackdate(x,sep_month_and_day),datenames,stop)
			#crackdate is from gsfd. It tries to find year, month, day, but will
			#settle for year,month or just year if the previous attempts fail.
		return new
	def readcsv(fname,has_header=True,parse_dates=False,convert_bools=False):#,truth_names=[]):
		'''Read a csv file and return a dframe.
If parse_dates is True, any column that is inferred by dateutil to include dates will be
	converted into datetime.datetime objects.
convert_bools: If True, and the column appears to contain only strings commonly used to represent
	truth or falsehood (yes, no, t, f, y, n, True, False, and other cases of those words),
	everything in the column will be coerced to a bool.
To define which words are treated as meaning True by Bool, use Bool.setTruthNames(new_names).
DEPRECATED ARG BELOW:
truth_names: An iterable, if not None. If convert_bools is True and this is not None, 
	any string matching a string in this iterable will be coerced to True, and all other entries in the
	column will be coerced to False.
		'''
		with open(fname) as f:
			reader=csv.reader(f)
			header=[reader.__next__() if has_header else None][0]
			return dframe.readlists(reader,header,parse_dates,convert_bools)#, truth_names)
	def readdict(Dict,parse_dates=False,convert_bools=False):#,truth_names=[]):
		'''Read a dictionary with list keys and return a dframe.
If parse_dates is True, any column that is inferred by dateutil to include dates will be
	converted into datetime.datetime objects.
convert_bools: If True, and the column appears to contain only strings commonly used to represent
	truth or falsehood (yes, no, t, f, y, n, True, False, and other cases of those words),
	everything in the column will be coerced to a bool.
To define which words are treated as meaning True by Bool, use Bool.setTruthNames(new_names).
DEPRECATED ARG BELOW:
truth_names: An iterable, if not None. If convert_bools is True and this is not None, 
	any string matching a string in this iterable will be coerced to True, and all other entries in the
	column will be coerced to False.
		'''
		new=dframe({},[])
		datecols=[]
		maxlen=0
		for key in Dict:
			if re.search('\Wdate[s]?\W|^date[s]?$|^date[s]?\W|\Wdate[s]?$',str(key),re.I):
				datecols.append(key)
			new.addcol(str(key),Dict[key],None,convert_bools)#,truth_names)
			maxlen=max(maxlen,len(Dict[key]))
		for i in range(min(maxlen,6)):
			for key in Dict:
				entry=Dict[key][i]
				if re.fullmatch(gsfd.datestr,str(entry)) and i not in datecols:
					datecols.append(key)
		if parse_dates:
			for i in datecols:
				new.setType(i,date)
				# datenames=['year','month','day']
				# if len(datecols)>1:
					# datenames=[s+str(i) for s in datenames]
				# stop=3
				# if not sep_month_and_day:
					# datenames=['year','day']
					# stop=2
				# new=new.split(str(i),lambda x: crackdate(x,sep_month_and_day),datenames,stop)
		return new
	def readstring(string,sep=' ',header=None,ignore_lines=[],parse_dates=True,parse_bools=True):#,truth_names=[]):
		'''Split a string by the separator sep, and convert it into a dframe.
header: the line number of the header, OR a list of names for the columns.
ignore_lines: a list of line numbers to ignore.
parse_dates: If true, coerce all cols containing strings that appear to be 
	YYYYMMDD dates into datetime.datetime objects.
parse_bools: Any column that contains only strings representing bools
	(e.g. True, t, f, yes, no, y, n), will be coerced to bools.
To define which words are treated as meaning True by Bool, use Bool.setTruthNames(new_names).
		'''
		lines=string.split('\n')
		rows=[line.split(sep) for line in lines]
		if header is None:
			included = [rows[i] for i in range(len(rows)) if i not in ignore_lines]
			return dframe.readlists(included,None,parse_dates,parse_bools)#,truth_names)
		elif type(header)==int:
			included = [rows[i] for i in range(len(rows)) if i not in ignore_lines and i>header]
			return dframe.readlists(included,rows[header],parse_dates,parse_bools)#,truth_names)
		elif type(header) in [tuple,list]:
			included = [rows[i] for i in range(len(rows)) if i not in ignore_lines]
			return dframe.readlists(included,header,parse_dates,parse_bools)#,truth_names)
	def readclipboard(sep=' ',header=None,ignore_lines=[],parse_dates=True,parse_bools=True):#,truth_names=[]):
		'''Read the current contents of the clipboard as a string, and convert to a dframe.
See documentation for dframe.readstring.'''
		return dframe.readstring(pyperclip.paste(),sep,header,ignore_lines,parse_dates,parse_bools)#,truth_names)
	def readpandas(pd_DataFrame,parse_dates=True):
		'''Read data from a pandas DataFrame. In practice, you will almost never want to do this,
because DataFrames are just more powerful than dframes.
parse_dates: If true, parse strings that look like dates as datetime.datetime objects.
		'''
		cols=list(pd_DataFrame.columns)
		Dict=pd_DataFrame.to_dict()
		vals=[list(x.values()) for x in Dict.values()] 
		#the rows returned by pd.DataFrame.to_dict are themselves dictionaries.
		return dframe.readdict(dict(zip(cols, vals)),parse_dates=parse_dates)
	def split(df,col,sep,to_names=None,max_split=10000):
		'''col: a number or name of a column.
sep: One of the following:
	1. a string at which to split the col's entries
	2. a function that splits the col's entries.
	3. a list of locations in each of the col's entries after which to introduce cuts.
to_names: names of the columns that will be produced.
max_split: the maximum number of splits to make.
	Returns: a new dframe with the indicated split made.
Example: If blah is a dframe, blah.split('a', ' ') will split column 'a' of blah at all spaces.
	blah.split('a',[2,5]) will split column 'a' of blah after the 2nd and 5th characters in each entry.
	blah.split('a',lambda x: re.split('\s?-\s?',x)) will split every entry in column 'a' of blah 
		wherever the regex pattern '\s?-\s?' is found.
		'''
		if type(col)==int:
			col=df.keys()[col]
		if type(sep)==str:
			new=[str(x).split(sep) for x in df.attrs[col]] #split at each instance of sep
		elif type(sep) in [set,tuple,list]: #break after each index number in sep
			new = []
			for x in df.attrs[col]:
				y=str(x)
				last=0
				entry=[]
				for i in sep:
					entry.append(y[last:i+1])
					last=i+1
				entry.append(y[last:])
				new.append(entry)
		else: #Use the function (usually re.split(separator,x) to split each entry in the column
			new=[sep(str(x)) for x in df.attrs[col]]
		most_splits=len(max(new,key=len))
		if max_split<most_splits:
			most_splits=max_split
			for i in range(len(new)):
				if len(new[i])>max_split:
					first=new[i][:max_split-1]
					last=' '.join(new[i][max_split-1:])
					new[i]=first+(last,)
		if to_names is None:
			to_names=['new_'+str(i) for i in range(most_splits)]
		if len(to_names) > most_splits:
			print("Warning: to_names is longer than maximum number of splits. to_names is being cut off.")
			to_names=to_names[:most_splits]
		if len(to_names) < most_splits:
			for i in range(most_splits-len(to_names)):
				to_names.append('new_'+str(i))
		new_cols=list([[] for i in range(most_splits)])
		newframe=df[:,:]
		for i in range(most_splits):
			for row in new:
				if i<len(row):
					new_cols[i].append(row[i])
				else:
					new_cols[i].append('')
			newframe.addcol(to_names[i],new_cols[i],str)
		newframe.remove(col)
		return newframe
	def remove(self,col):
		'''Remove a column and its corresponding type from the dframe.'''
		start_types = dict(zip(self.keys(),self.types))
		if type(col)==int:
			col=self.keys()[col]
		ind=self.keys().index(col)
		del self.attrs[col]
		del self.types[ind]
		if len(self.types) != len(self.keys()): #Sometimes the list of types gets longer than the list of keys. Not sure why.
			for key in self.keys():
				if key not in start_types:
					break
				if self.types[self.keys().index(key)] != start_types[key]:
					self.types[self.keys().index(key)] = start_types[key]
			self.types=self.types[:len(self.keys())] #Make the types and keys lists the same length.
		
	def setType(self,col,new_type):
		'''Change the data type of a given column to new_type. Also coerces all
entries already in that column to new_type.'''
		if type(col)==int:
			col=self.keys()[col]
		self.types[self.keys().index(col)]=new_type
		Col=self.attrs[col]
		for i in range(len(self)):
			try:
				Col[i]=new_type(Col[i])
			except:
				if new_type in [int,float]:
					Col[i]=float('NaN')
				else:
					Col[i]=None
	def unique(self,col,get_count=False,characteristic=None):
		'''Return all unique entries in the chosen col of the dframe.
If get_count is True, also shows the count of each unique entry.
characteristic: the value of a function that acts on each entry, for
	example, len or int. If characteristic is not None, returns all the 
	unique values of that function in col.
Note: value returned by characteristic must be hashable, 
	because it will become a dict key.'''
		if type(col)==int:
			col=self.keys()[col]
		counter={}
		C=self.attrs[col]
		if characteristic is None:
			for i in range(len(C)):
					counter.setdefault(C[i],0)
					counter[C[i]]+=1
		else: #Find each unique value of the characteristic in the column.
			for i in range(len(C)):
				try:
					thing=characteristic(C[i])
					counter.setdefault(thing,0)
					counter[thing]+=1
				except:
					counter.setdefault(None,0)
					counter[None]+=1
		if get_count:
			return counter
		else:
			return list(counter.keys())
	def uniques_to_rows(self,col,characteristic=None):
		'''Return a dict mapping the unique entries in the chosen col of the dframe to the row numbers
on which that unique entry is found.
characteristic: the value of a function that acts on each entry, for
	example, len or int. If characteristic is not None, returns all the 
	unique values of that function in col.
Note: value returned by characteristic must be hashable, 
	because it will become a dict key.'''
		if type(col)!=str:
			col=self.keys()[col]
		out={}
		C=self.attrs[col]
		if characteristic is None:
			for i in range(len(C)):
				out.setdefault(C[i],[])
				out[C[i]].append(i)
		else:
			for i in range(len(C)):
				try:
					thing=characteristic(C[i])
					out.setdefault(thing, [])
					out[thing].append(i)
				except:
					out.setdefault(None,[])
					out[None].append(i)
		return out
	def stringjoin(self,cols,sep='',name=None,keep_old=False):
		'''cols: a list of cols to string-join.
sep: the separator to interpolate between the cols to be joined.
name: the name of the new column.
keep_old: If true, keep the old columns that were stringjoined.
	Else, keep only the result of stringjoining.
returns: a dframe with the new string joined column added.
		'''
		for i in range(len(cols)):
			if type(cols[i])!=str:
				cols[i]=self.keys()[cols[i]]
		new=self[:,:]
		if not name:
			name=sep.join(cols)
		newcol=[sep.join([str(self.attrs[col][x]) for col in cols]) for x in range(len(new))]
		if not keep_old:
			for col in cols:
				new.remove(col)
		new.addcol(name,newcol)
		return new
	def sort_by(self,by_col,asc=True,func=None,has_nans=False,na_include=True):
		'''Return a copy of the original dframe, sorted (ascending by default) by the values in by_col.
If func is not none, sort by func(val) for val in by_col.
asc: If false, sort descending instead of ascending.
has_nans: If true, scan the column for 'nan' and None before sorting. 
	float('nan') has the unfortunate property of not being equal to, less than, or greater than 
	any int or float (including itself!), and None does not support comparisons,
	so they both cause even Python's built-in sorted() function to screw up.
na_include: If False, don't return any rows in which the by_col has float('nan').
E.g., self.sort_by('names',False,len) will sort the dframe descending by the length of values in the 'names' column.
		'''
		if type(by_col)!=int:
			by_col=self.keys().index(by_col)
		if not has_nans:
			rows=[list(self.rows(i).attrs.values()) for i in range(len(self))]
		else: #remove 'nan' and None from the list before sorting or everything will be horrible.
			not_nans=self.select(by_col,lambda x: str(x)!='nan').select(by_col, lambda x: x is not None)
			rows=[list(not_nans.rows(i).attrs.values()) for i in range(len(not_nans))]
			if na_include:
				nanframe=self.select(by_col,lambda x: str(x)=='nan' or x is None)
				nan_rows=[list(nanframe.rows(i).attrs.values()) for i in range(len(nanframe))]
		if func is not None:
			rows=sorted(rows,key=lambda x: func(x[by_col][0]),reverse=not asc)
		else:
			rows=sorted(rows,key=lambda x: x[by_col],reverse=not asc)
		new=dframe(self.keys(),self.types)
		for row in rows:
			new.append([x[0] for x in row]) #each row is a list of one-element sublists
		if na_include and has_nans:
			for row in nan_rows: #now insert the rows with nan's at the end.
				new.append([x[0] for x in row])
		return new
	def pivot_wider(self,key_col,vals_col):
		'''key_col: a column with multiple unique values, ALL OF WHICH HAVE THE SAME NUMBER OF CORRESPONDING ROWS.
		vals_col: the column containing the values that will populate the new columns created.
		returns: a new dframe with the key_col unique names pivoted out as separate columns with values from vals_col.
		Once again, THIS ONLY WORKS IF ALL KEYS IN KEY_COL HAVE THE SAME NUMBER OF CORRESPONDING ROWS.
		IF THAT'S NOT TRUE, THIS WILL FAIL!!!
		TODO: Make this work in a non-stupid way.
		'''
		if type(vals_col)!=int:
			vals_col=self.keys().index(vals_col)
		if type(key_col)!=str:
			key_col=self.keys()[key_col]
		others=[col for col in self.keys() if col not in [self.keys()[vals_col],key_col]]
		names=self.unique(key_col)
		val_type=self.types[vals_col]
		new=dframe([str(x) for x in names],[val_type for x in names])
		for name in names:
			new.attrs[str(name)]=self.select(key_col,lambda x: x==name).attrs[self.keys()[vals_col]]
		for col in others:
			new.addcol(col,self.attrs[col],self.types[self.keys().index(col)])
		return new
	def dollarsToFloat(df,start=0,end=None):
		'''Return a new dframe in which all columns 
		(from col number start to col number end)
	with dollar amounts are converted to floats.'''
		moneycols=[]
		if end is None:
			end=len(df.keys())
		for col in df.keys()[start:end]:
			if df.getTypes(df.keys().index(col))=='str':
				for i in range(min(len(df),5)):
					if len(df[i,col])>0:
						if df[i,col][0]=="$" and col not in moneycols:
							moneycols.append(col)
		new=df[:,:]
		for col in moneycols:
			for i in range(len(df.attrs[col])):
				new.attrs[col][i]=new.attrs[col][i][1:]
		for col in moneycols:
			new.setType(col,float)
		return new
	def join(self,other,self_col,other_col,self_has_nans=True,other_has_nans=True,compare_as_strings=False):
		'''Returns all pairs of rows in self and other that satisfy the condition 
	"self[this_row,self_col] is equal to other[other_row,other_col]".
If (self/other)_has_nans is True, will search through (self/other) for nan's and filter those out
	before joining.
If compare_as_strings is True, the values in the two cols will be compared based on their string values.
	You should do this if you have two data types that don't support the >, <, >=, or <= operators,
	like datetimes.
Excludes rows in both self and other where self_col or other_col has 'nan', because 'nan' screws with
	sorting and comparison.
Perform a simple SQL-style inner join of two dframes that excludes rows with "nan"'s, as in
"SELECT * FROM self 
	JOIN other ON self.self_col = other.other_col
	WHERE self.self_col IS NOT NULL AND other.other_col IS NOT NULL"
Seriously, though, if you're going to be joining two dataframes or whatever, just
convert them into pandas.DataFrames and use pd.merge to join them. pandas is guaranteed to have
a much better and faster solution than I came up with.

TODO:
	1. Make sure that compare_as_strings doesn't have any unintended consequences.
	2. Figure out how to handle duplicate column names in the two dframes.
	3. Generally make sure that it works even outside of compare_as_strings.
		'''
		if type(self_col)!=str:
			self_col=self.keys()[self_col]
		if type(other_col) != str:
			other_col=other.keys()[other_col]
		if self_has_nans:
			self_no_nan=self.select(self_col,lambda x:str(x)!='nan' and x is not None)
		else:
			self_no_nan = self
		if other_has_nans:
			other_no_nan=other.select(other_col,lambda x: str(x)!='nan' and x is not None)
		else:
			other_no_nan = other
		
		if compare_as_strings: #do this when the original join columns are not amenable to binary search or sorting.
			#Create temporary dframes containing stringified data from the columns of interest
			#with names that are very unlikely to occur naturally
			new_self_colname, new_other_colname = str(hash(self_col)), str(hash(other_col))+'_'
			self_new_comparison_col=dframe()
			self_new_comparison_col.addcol(new_self_colname,[x for x in self_no_nan[self_col]],str)
			other_new_comparison_col=dframe()
			other_new_comparison_col.addcol(new_other_colname,[x for x in other_no_nan[other_col]],str)
			# self_no_nan.addcol(new_self_colname,[x for x in self[self_col]],str)
			# other_no_nan.addcol(new_other_colname, [x for x in other[other_col]],str)
			#og_selfname, og_othername = self_col, other_col
			L_uniques = self_new_comparison_col.uniques_to_rows(new_self_colname)
			R_uniques = other_new_comparison_col.uniques_to_rows(new_other_colname)
		else:
			L_uniques=self_no_nan.uniques_to_rows(self_col)
			R_uniques=other_no_nan.uniques_to_rows(other_col)
		lkeys,rkeys=list(L_uniques.keys()),list(R_uniques.keys())
		if len(L_uniques) > len(R_uniques): #self[self_col] has more unique entries than other[other_col]
			shortest,longest=rkeys.copy(),lkeys.copy()
			L_short=False #indicate that the dframe with fewer unique entries is the right one.
		else: #other[other_col] has at least as many unique entries as self[self_col]
			shortest,longest=lkeys.copy(),rkeys.copy()
			L_short=True
		# print("shortest="+str(['self','other'][not L_short]))
		# print("Unique entries and corresponding rows of shortest are: "+str([R_uniques,L_uniques][L_short]))
		# print("Unique entries and corresponding rows of longest are: "+str([L_uniques,R_uniques][L_short]))
		
		shortest=sorted(shortest) #sort the unique entries of the dframe with fewer unique entries
		join_map=dict()
		#For a given entry, X, in self_col that is also in other_col, this dictionary maps between the
		#row numbers in self_col where X is found to the row numbers in other_col where X is found.
		#After all such mappings have been found, all pairs of rows in which self_col and other_col
		#both contain X (so for example, 12 pairs of rows if 3 rows in self and 4 rows in other both
		#contain X) will be added to the new dframe.
		for i in range(len(longest)):
			#Iterate through UNIQUE keys in the column with more unique entries (longest),
			#using bisection search to find where in the unique entries of the other dframe (shortest)
			#each key in longest can be found. If it is found that a matching entry exists in shortest,
			#map the corresponding row numbers in longest to the matching row numbers in shortest.
			other_key=bis.bindex(longest[i],shortest,asc=True,get_index=True)
			if other_key is not None:
				if L_short:
					join_map[tuple(R_uniques[longest[i]])] = L_uniques[shortest[other_key]]
				else:
					join_map[tuple(L_uniques[longest[i]])] = R_uniques[shortest[other_key]]
		map_keys=list(join_map.keys())
		#return join_map
		newframe=dframe(self_no_nan.keys()+other_no_nan.keys(),self_no_nan.types+other_no_nan.types)
		for i in range(len(map_keys)):
			cur_key=map_keys[i]
			for l_row in cur_key:
				for s_row in join_map[cur_key]:
					if L_short: #self has fewer unique entries
						join_row_left = self_no_nan[s_row,:].attrs
						join_row_left.update(other_no_nan[l_row,:].attrs)
					else: #self has more unique entries.
						join_row_left = self_no_nan[l_row,:].attrs
						join_row_left.update(other_no_nan[s_row,:].attrs)
					for k in join_row_left:
						#a single row from a dframe is by default a list with one element.
						#need to unpack that element.
						join_row_left[k]=join_row_left[k][0]
					newframe.append(join_row_left)
		# if compare_as_strings: #get rid of the temporary cols made for joining purposes.
			# newframe.remove(new_other_colname)
			# newframe.remove(new_self_colname)
			# try:
				# self.remove(new_self_colname)
				# other.remove(new_other_colname)
			# except:
				# pass
		# #joining seems to have the effect of sometimes leaving extra types in the dframes used.
		# #this should remove any extra types without affecting any of the data.
		# other.types=other.types[:len(other.keys())]
		# self.types=self.types[:len(self.keys())]
		# newframe.types=newframe.types[:len(newframe.keys())]
		return newframe
	def antijoin(self,other,self_col,other_col,self_has_nans=True,other_has_nans=True,compare_as_strings=False):
		'''Find rows of of this dframe (self) such that the entries in those rows
	of self_col are NOT IN other_col of other. See documentation on join.'''
		entries_in_join=self.join(other,self_col,other_col,self_has_nans,other_has_nans,compare_as_strings).unique(self_col)
		return self.select(self_col,lambda x: x not in entries_in_join)
	
	def topandas(self):
		'''Convert this dframe into a pandas.DataFrame.
When you're tired of mucking around with my Project Euler-style attempt at a 
data frame and you want to get some actual work done, do this.'''
		return pd.DataFrame(self.attrs)
	def fitPolynom(self,x_col,y_col,degree=1, plot=True,title=None,legend=None):
		'''Do linear least squares to get a best fit polynomial of the chosen degree
relating the data in y_col to the data in the independent RV x_col. 
Plots the data with matplotlib.
Returns: {'parms': best fit parameters,'R^2': best fit R-squared value, 'fit': best fit data points}.
plot: If true, make a plot of the data with matplotlib. You will have to show it or save it yourself.
title: The title of the plot.
legend: The description of the data that will appear in the legend.
		'''
		if type(x_col) != str:
			x_col = self.keys()[x_col]
		if type(y_col) != str:
			y_col = self.keys()[y_col]
		#llsq_mat=np.array([[self[i,x_col]**(degree-j) for j in range(degree)] for i in range(len(self))])
		#Each row in the llsq_mat contains each of the variables that will be used to solve the
		#underdetermined system of equations.
		#In this case, the variables are the x-value raised to powers ranging from 0 to degree.
		#Go to "def linearLeastSquaresNotes" in linalg_stuff to understand how the fit is obtained.
		#params, fitCurve = lin.llsq(llsq_mat, self[y_col]) #that's how to get a best fit line
		#Use np.polyfit to get relationship between x_col and y_col, because it's more efficient
		#and powerful than using my implementation, and it also gives much better fits for degree > 2.
		params = np.polyfit(self[x_col], self[y_col], degree)
		fitCurve = np.polyval(params, self[x_col]) #polyval automatically unpacks the parameters
			#and raises the data to the correct powers. Useful for high-dimensional fits.
		#e.g., np.polyfit(self[x_col],self[y_col],2) would return the params of the least-squares
		#degree 2 (quadratic) approximation for the data in the format
		#np.array([a,b,c]) where y = a*x**2 + b*x + c.
		var=sum([(self[i,y_col] - fitCurve[i])**2 for i in range(len(self))]) / len(self)
		mu = np.mean(self[y_col])
		var_from_mu = np.mean([(self[i,y_col] - mu)**2 for i in range(len(self))])
		rsquare = 1 - var / var_from_mu #the technical term for R^2 is the "coefficient of determination."
		#for a best fit line, R^2 must be in (0,1].
		if not legend:
			plt.scatter(self[x_col],self[y_col], label="Actual data {0} vs {1}".format(x_col,y_col))
		else:
			plt.scatter(self[x_col],self[y_col], label = legend)
		if degree == 1:
			plt.plot(self[x_col], fitCurve, label="Best fit line: y = {0:1.3e}*x + {1:2.3e}\nR^2 = {2:3.6}".format(params[0],params[1],rsquare))
		else:
			plt.plot(self[x_col],fitCurve, label = "Best fit curve with degree {0}.\nR^2 = {1:2.6}".format(degree,rsquare))
		plt.legend(loc='best')
		plt.xlabel(x_col)
		plt.ylabel(y_col)
		if not title:
			plt.title('Linear least squares for {0} vs. {1}'.format(x_col,y_col))
		else:
			plt.title(title)
		print("Created a plot of {0} vs {1}".format(x_col,y_col))
		return {'parms':params, 'R^2':rsquare, 'fit': fitCurve}
	def memoryUsage(self):
		'''Get the approximate memory usage of this dframe.
data_size+=sys.getsizeof(List_of_stuff)
You would think that the above line would give you the memory usage of a list, but it doesn't!
THE MEMORY USAGE OF A LIST IS ALWAYS 4 BYTES PER ITEM PLUS 28, NO MATTER WHAT'S INSIDE IT!
What you want is the sum of the memory usage of each object inside the list.

Note: pandas DataFrames save memory by storing strings and numbers as just
the values themselves, rather than as objects.
If you convert a dframe to a pandas DataFrame, you will find that DataFrames use significantly
less memory.
For example, a normal list of numbers in Python uses like 28 bytes per number,
because numbers are objects and objects have memory overhead associated with
class attributes, while numpy arrays store numbers as just numbers, so there's no such overhead.'''
		out= {'tot':0}
		for a in self.attrs:
			out[a]=sum([sys.getsizeof(x) for x in self[a]]) + 4*len(self) + 28 
			#the list itself takes up 28 bytes minimum, plus 4 bytes per element.
			out['tot'] += out[a]
		return out
	
class date(object):
	'''A callable class that, when called on a string,
	hands it over to dateutil to try and parse it, and if called
	on a datetime.datetime or datetime.date, returns the
	input.'''
	def __new__(self,string_or_datetime):
		if type(string_or_datetime) in [datetime.date,datetime.datetime]:
			return string_or_datetime #leave it alone if it's already good
		else:
			return parser.parse(string_or_datetime) 
			#convert it to a date if it's not already.

blahdict={'a': ['nan', 1, 5, 16, -1], 'b': ['1', 'a', 'hi', 'hello, bob', '5 pizzas, 15 beers. Yo!'], 'c': [12.0, 1.2, 5.6, -153.0, 0.0], 'd': ['b', '5', '7', 'you', 'eat'],'e':['y','t','Tree','b','c']}
def makeBlah():
	'''Makes a simple dframe to test the readdict method.'''
	blah=dframe.readdict(blahdict,True,True)#,truth_names=['Tree','c'])
	return blah
#####SOME SAMPLE DFRAMES#####
blah=makeBlah()
#sil=dframe.readcsv('silly_example.csv',has_header=True,parse_dates=True,convert_bools=True) #uncomment this once you've downloaded silly_example.csv from this commit.
#sil.append([7,'Unyir','MOKJI','2017/05/11',6,'i',True])
#pdts=dframe.readcsv('Products.csv',True,True,True) #uncomment this once you've downloaded Products.csv. Products.csv was created by Jon Acampora for the Elevate Excel course.
#sil.split(-1,lambda x:[x[:2],x[2:]],['date','month'] 
#how to split a string column at a specified index.

test_bools=['t','f','True','False','Ti','Fo','T',1,0,'1','yes','No',True,False,'fasle','fhdfkj',2,3,4,'',[],tuple(),{},str]
		
jul = dframe.readstring('Boston July Temperatures\r\n-------------------------\r\n\r\nDay High Low\r\n------------\r\n\r\n1 91 70\r\n2 84 69\r\n3 86 68\r\n4 84 68\r\n5 83 70\r\n6 80 68\r\n7 86 73\r\n8 89 71\r\n9 84 67\r\n10 83 65\r\n11 80 66\r\n12 86 63\r\n13 90 69\r\n14 91 72\r\n15 91 72\r\n16 88 72\r\n17 97 76\r\n18 89 70\r\n19 74 66\r\n20 71 64\r\n21 74 61\r\n22 84 61\r\n23 86 66\r\n24 91 68\r\n25 83 65\r\n26 84 66\r\n27 79 64\r\n28 72 63\r\n29 73 64\r\n30 81 63\r\n31 73 63', sep=' ', header=3, ignore_lines=[4,5],parse_dates=True,parse_bools=True)

spring = dframe.readstring('Distance (m) Mass (kg)\n0.0865 0.1\n0.1015 0.15\n0.1106 0.2\n0.1279 0.25\n0.1892 0.3\n0.2695 0.35\n0.2888 0.4\n0.2425 0.45\n0.3465 0.5\n0.3225 0.55\n0.3764 0.6\n0.4263 0.65\n0.4562 0.7\n0.4502 0.75\n0.4499 0.8\n0.4534 0.85\n0.4416 0.9\n0.4304 0.95\n0.437 1.0\n', sep = ' ',header=['distance','mass'],ignore_lines=[0])
#squr = spring.fitPolynom(1,0,1) #this will create a plot with a first-degree polynomial fit.
####END OF SAMPLE DFRAMES####

def joinops(left_len,right_len,left_uniques,right_uniques,matches):
	'''Gives the approximate number of operations required to join two dframes
	with the given specifications using my algorithm.
left_len,right_len: the number of rows in each dframe
left_uniques,right_uniques: the number of rows with unique entries in the join column
	in each dframe.
matches: The number of rows in the new dframe that will be created by the join.
	'''
	get_uniques=left_len+right_len 
	print("If both dframes had nan's to remove, it would take "+str(get_uniques)+" ops to remove them.")
	print ('unique row find: '+str(get_uniques))
	short_uniques=min([left_uniques,right_uniques])
	long_uniques=max([left_uniques,right_uniques])
	sort_short=short_uniques*max(math.log(short_uniques,2),1)
	print("sort uniques of column with fewer uniques: "+str(sort_short))
	search_for_matches = long_uniques*max(math.log(short_uniques,2),1)
	print("Find matches between short and long: "+str(search_for_matches))
	make_dframe=matches*4
	print("Make new dframe: "+str(make_dframe))
	return get_uniques + sort_short + search_for_matches + make_dframe


####MY IMPLEMENTATION OF THE CATEGORICAL DATA TYPE####
class Cframe(object):
	'''A class I made to test out the Category class, in preparation for adding it to the dframe class.'''
	def __init__(self):
		self.stuff=[]
		self.categories={}
	def addcol(self,col=[]):
		self.stuff.append([])
		for i in col:
			self.stuff[len(self.stuff)-1].append(i)
	def getCategories(self):
		return self.categories
	def addCategory(self,colnum):
		assert colnum < len(self.stuff), 'Cannot add category to a nonexistent column'
		assert not self.hasCategory(colnum), 'That column already has a category.'
		self.categories[colnum] = Category()
		for i in range(len(self.stuff[colnum])):
			self.stuff[colnum][i]=self.categories[colnum](self.stuff[colnum][i])
	def hasCategory(self,colnum):
		return colnum in self.categories
	def append(self,colnum,thing):
		if self.hasCategory(colnum):
			#calling the Category object on thing adds thing to the Category's list of 
			#uniques if it's not already there, and then returns the index of thing
			#in its list of uniques.
			self.stuff[colnum].append(self.categories[colnum](thing))
		else:
			self.stuff[colnum].append(thing)
	def __str__(self):
		#For each entry in a column, displays the entry itself if there is no category for that column,
		#or if there is a category, looks up the value in the category's cats attribute corresponding to
		#the entry.
		out = "Cframe(\n"
		for i in range(len(self.stuff)):
			out+="["
			if not self.stuff[i]:
				out+="],\n"
				continue
			cat=self.hasCategory(i)
			for j in range(len(self.stuff[i])-1):
				item=self.stuff[i][j]
				if cat:
					out+=str(self.categories[i].cats[item])
				else:
					out+=str(item)
				out+=", "
			item=self.stuff[i][len(self.stuff[i])-1]
			if cat:
				out+=str(self.categories[i].cats[item])
			else:
				out+=str(item)
			out+="],\n"
		out+="category columns = "+str(list(self.categories.keys()))+")"
		return out
	def __repr__(self):
		return str(self)
	def __getitem__(self,tup):
		colnum=tup[1]
		rownum=tup[0]
		item=self.stuff[colnum][rownum]
		if self.hasCategory(colnum):
			return self.categories[colnum].cats[item]
		else:
			return item
	def memoryUsage(self):
		sizes=[]
		for i in range(len(self.stuff)):
			list_size=sys.getsizeof(self.stuff[i])
			contents_size=sum(sys.getsizeof(x) for x in self.stuff[i])
			cats_size = sum(sys.getsizeof(x) for x in self.categories[i].cats) + sys.getsizeof(self.categories[i])
			sizes.append(list_size+contents_size+cats_size)
		return sizes
			
		 
class Category(object):
	'''My implemetation of a categorical dtype that enables compression of data
	by linking each unique entry in a column to a number (which is the number of unique entries just
	before that unique entry was added.
The actual entries in the dataframe will be unsigned integers of the smallest unsigned integer type
	that can fit all the categories (np.uint8 for less than 256 categories, 
	np.uint16 for 256-65536 categories)
Whenever a call is made to the dataframe for the number at index iin a column with an associated category,
	the dataframe dispatches the call to its category and the category fetches the value associated
	with the number at index i.
In this way, data associated with storage of long repeated strings can be greatly reduced, at the cost
	of increased time to look up data.
	'''
	def __init__(self):#,df,colnum):
		self.cats=[]
		#self.colnum=colnum
		self.dtype=np.uint8 #the whole point of this class is compression of data
	def __call__(self,thing):
		'''Calling this object on a thing will add the thing to this object's list
		of uniques if it's not already there and return the index of the thing
		as an integer of the smallest dtype possible.'''
		if thing not in self.cats:
			if len(self.cats)>254:
				if len(self.cats)>65534:
					self.dtype=np.uint32
				else:
					self.dtype=np.uint16
			self.cats.append(thing)
		return self.dtype(self.cats.index(thing))
	def __str__(self):
		out="Category:\n"
		#out+="colnum="+str(self.colnum)
		out+="cats="+str(self.cats)
		return out+",\ndtype="+re.findall(gsfd.classnameregex,str(self.dtype))[0]
	def __repr__(self):
		return str(self)
			
def makeCframe():
	bjo=Cframe()
	bjo.addcol()
	bjo.addCategory(0)
	bjo.append(0,'abc')
	bjo.append(0,'a')
	bjo.addcol()
	bjo.append(1,'b')
	bjo.append(0,'abc')
	bjo.append(0,'b')
	bjo.append(0,'a')
	bjo.append(0,'abc')
	bjo.append(1,'d')
	bjo.addcol()
	bjo.addCategory(1)
	return bjo
#names=sil['cities'][:]*2000 # a very long list of names of about 4.5 chars each with only 6 unique values
# sys.getsizeof(names) #760 kb
# bjo=makeCframe()
# bjo.addCategory(2)
# for i in names:
	# bjo.append(2,i)
# sys.getsizeof(bjo.stuff[2]) #338 kb- a savings of more than 50%
# sys.getsizeof(bjo.categories[2].cats) #178 bytes
#As another example, the temperature_data.csv file has three columns, CITY, TEMP, and DATE,
#each with 421,848 entries, with types str, float, and datetime.datetime, respectively.
#I loaded this csv file with dframe.readcsv, and the memory usage was
#{'tot': 37,705,260, 'CITY': 15,769,108, 'TEMP': 8,436,988, 'DATE': 13,499,164}
#I put the data into a Cframe and added categories and the resulting memory usage was
#{'tot': 28,279,913, 'CITY': 7,179,525, 'TEMP': 7,590,025, 'DATE': 13,510,363}
#Notice that applying a category to the DATE data in the Cframe actually increased the memory consumption.
#This is because there are 20088 different days in this data set, so the integer type used
#to alias for the dates has to be an np.int16 and the dates are only 8 bytes each to begin with.
#There are 588 distinct floats in TEMP, so the compression of the 421848 rows in the Cframe makes up
#for the storage required for the category itself. 
#The CITY column only has 21 different cities, which all have names that are about 10 Unicode characters,
#so the compression is quite impressive for this column, as expected.
#OF COURSE, A PANDAS DATAFRAME IS MUCH BETTER AT REDUCING MEMORY CONSUMPTION.
#When you convert the temperatures data to a pandas DataFrame, you get
# Index			  66
# CITY	   1,687,392
# TEMP	   3,374,784
# DATE	   3,374,784
# TOTAL	   8,437,026
#So even the best compression algorithm I can come up with pales in comparison to the compression that
#DataFrames do EVEN BEFORE YOU TRY TO COMPRESS THE DATA.
