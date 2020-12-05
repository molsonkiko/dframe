pizzabeer="1!! Bob bought 2.34 pizzas, and I have 76 beers now.\n HODOR\n 55. I am 10\n I eat many fro8l a8 8b 9"
from collections import Counter as count
import random
def allsame(list1,list2):
	'''
Returns True if list1 and list2 are elementwise identical, else False.
	'''
	length=min(len(list1),len(list2))
	for i in range(length):
		if list1[i]!=list2[i]:
			return False
	return True

def anysame(list1,list2):
	'''
Returns True if any element in list1 is identical to the corresponding element in list2, else False.
	'''
	length=min(len(list1),len(list2))
	for i in range(length):
		if list1[i]==list2[i]:
			return True
	return False

def bindex(n, List,asc=True,get_index=True):
	"""n: a string or numeric.
	List: a SORTED list or tuple containing only strings or numerics
	asc: True if the iterable is sorted ascending, false if descending.
	get_index: If True, returns the index where n was found in List, else None if it's not there.
	If not get_index, bindex returns True if n is in the List, else False.
	"""
	low=0
	high=len(List)
	Indx=(high+low)//2
	while List[Indx]!=n: #do binary search for the index of the closest entry.
		if Indx>=len(List)-1 or Indx==0 or high-low<=1:
			break
		elif (List[Indx] > n and asc) or (List[Indx] < n and not asc):
			high=Indx
			Indx=(high+low)//2
		elif (List[Indx] < n and asc) or (List[Indx] > n and not asc):
			low=Indx
			Indx=(high+low)//2
		assert not (str(List[Indx])=='nan' and type(List[Indx])==float), 'Cannot do binary search on a list with float(\'nan\') because it does not support comparisons.'
	
	for i in [Indx-1,Indx,Indx+1]:
		if i<0 or i>=len(List):
			continue
		assert not (str(List[i])=='nan' and type(List[i])==float), 'Cannot do binary search on a list with float(\'nan\') because it does not support comparisons.'
		if List[i]==n:
			if get_index:
				return i
			else:
				return True
	if not get_index:
		return False
	return None

def closebin(n,List,asc=True,epsilon=0,get_index=False): #also aliased as binclose
	'''n: a number
List: a SORTED iterable containing only numbers
Returns: the closest entry in List to n, or the first entry found within epsilon.
asc: True if List are sorted ascending, False otherwise.
epsilon: The maximum distance from n at which the search will terminate.
If epsilon is 0, the search will continue until it reaches the final branch
of the binary search tree.
get_index: If true, return a tuple (closest number, index of closest number)
	'''
	low=0
	high=len(List)
	Indx=(high+low)//2
	while abs(List[Indx]-n)>epsilon: #do binary search for the index
					#of the closest entry.
		if Indx>=len(List)-1 or Indx==0 or high-low<=1:
			break
		elif (List[Indx]-n > epsilon and asc) or (List[Indx]-n < -epsilon and not asc):
			high=Indx
			Indx=(high+low)//2
		elif (List[Indx]-n < -epsilon and asc) or (List[Indx]-n > epsilon and not asc):
			low=Indx
			Indx=(high+low)//2
		assert not (str(List[Indx])=='nan' and type(List[Indx])==float), 'Cannot do binary search on a list with float(\'nan\') because it does not support comparisons.'
	#Get as many of Indx, Indx-1, and Indx+1 as are in the list.
	near_inds=[]
	for x in [Indx-1,Indx,Indx+1]:
		if x >=0 and x<len(List):
			assert not (str(List[x])=='nan' and type(List[x])==float), 'Cannot do binary search on a list with float(\'nan\') because it does not support comparisons.'
			near_inds.append(x)
	#sort the indices of the 1-3 closest entries by their distance from n.
	near_inds = sorted(near_inds, key=lambda x: abs(List[x]-n))
	if not get_index:
		return List[near_inds[0]] #get closest entry
	else:
		return List[near_inds[0]],near_inds[0] #get closest entry and its index
binclose=closebin

def closest(iterable, threshold,above=False,get_value=True,sort=None):
	'''Finds the closest value (or the index thereof if get_value is False)
in the iterable above or below a threshold value.
For faster performance, you can specify that the iterable is sorted 'asc' or 'desc'.'''
	try:
		if type(iterable)==dict:
			iterable=list(iterable.keys())
		best=iterable[0]
	except:
		best=iterable.iloc[0] #Works if iterable is a pd.Series. If not, you're out of luck.
	ind=0
	for i in iterable:
		if (above and abs(threshold-i)<abs(threshold-best) and i>=threshold) or (not above and abs(threshold-i)<abs(threshold-best) and i<=threshold):
			best=i
			best_ind=ind
			if (i>threshold and sort=='asc' and not above) or (i<threshold and sort=="desc" and above):
				return [best if get_value else best_ind][0]
		ind+=1
	return [best if get_value else best_ind][0]

def order(iterable, desc=False):
	'''
Returns a function that sorts a list or tuple in the same way that the iterable
passed into this function would be sorted. If desc is True, it will sort descending.
Example: z=('a','i','c','e','d','g','h','f','b')
The sorting list of z is [0, 8, 2, 4, 3, 6, 7, 5, 1] because the nth element
of the sorting list is the position of the nth element of z in the sorted
version of z (ascending).
So let's say we write zord=order(z).
Now if we say zord([10,11,12,13,14,15,16,17,18]),
it will return [10,18,12,14,13,17,15,16,11].
Trivially, if you do zord(z), it will return z sorted ascending.
This is an approximate workalike of the eponymous function in R.
Passes the sortTester test shown below.
NOTE: 
THIS FUNCTION ONLY WORKS IF THERE ARE NO REPEATED VALUES IN ITERABLE.
	'''
	z=iterable
	sortz=sorted(z,reverse=desc)
	sortvec=[]
	Sorted=[]
	for elem in z:
		Sorted.append(None)
		sortvec.append(sortz.index(elem))
	def orderBy(toSort):
		elemct=count(toSort) 
		#returns dict mapping each elem in toSort to the number of instances in toSort.
		for i in range(len(sortvec)):
			for e in range(elemct[toSort[i]]):
				Sorted[sortvec[i]+e]=toSort[i]
		return Sorted
	return orderBy

def sortTester():
	'''
	Can be used to make sure that a sorting or element-getting function always gets everything
	as it should. If it's not foolproof, it should eventually fail on this gauntlet.
	'''
	for i in range(4000):
		randlist=[]
		for j in range(30):
			rando=random.randint(0,20000)
			for k in range(random.randint(1,4)):
				randlist.append(rando)
			random.shuffle(randlist)
		if not (allsame(sorted(randlist),order(randlist)(randlist)) and allsame(sorted(randlist,reverse=True),order(randlist,True)(randlist))):
			return False
	return True
	
def alnumToInt(string):
	'''string: a string OF LENGTH 15 OR LESS
CONTAINING ONLY UPPER AND LOWER CASE ASCII CHARS, DIGITS, AND ' '.
Returns: A number, such that numbers and words are sorted in the same way they
	would be in a dictionary.
	Well, almost. 'z'*15 has a greater value than ' ', even though it's lexicographically earlier.
	There are probably other deviations of this nature too. For the most part the lexicographic ordering
	seems to be correct.
If the string is empty or contains non-conforming chars, returns None.'''
	if len(string)==0 or len(string)>15:
		return None
	chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
	out=0
	L=len(string)
	for i in range(L):
		if string[i] not in chars:
			return None
		out+=(1+chars.index(string[i]))*53**(16-i-1)
	return out