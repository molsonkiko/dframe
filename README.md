# dframe
This is my first repository on GitHub. I make no warranty as to the quality of the code, and less warranty as to the quality of the repository itself.
Because this project is essentially intended to say "look at me! I know how to do OOP and use regular expressions in Python!" and has no practical use, it will not be maintained or updated.

The primary content of this repository is the dframe class, which is my attempt to replicate the basic functionality of dataframes in R and Pandas and tables in SQL-
a set of aligned statically typed columns that enable the easy sorting, grouping and selection of data based on certain parameters.
As I am not a particularly experienced programmer, there is no reason that anyone (including myself) should want to use dframes instead of Pandas DataFrames.

The second important piece of this repository is the gsfd module, which has a motley assortment of regular expressions and functions for creating regular expressions. The gsfd module is a dependency of the dframe module.

The third and most practically useful module in this repository is binarySearch, which as the name suggests contains two important implementations of bisection search, bindex and closebin. bindex does traditional bisection search and can either return a boolean ("is this in the iterable?") or the index of an item in a sorted iterable. closebin does bisection search for the closest value in a sorted list of numbers. closebin is particularly useful to me for generating random values of a continuous random variable, because it can quickly map from a random number in [0,1] to the closest value in a lookup table. There are other functions in binarySearch, including a semi-functional implementation of the order function from the R language, but they are far less useful.

That said, any dframe object has the following attributes:
attrs, a dictionary mapping keys to lists of values. 
types, a list of types. Whenever a value is added to the i^th column, the i^th type is applied to that value.
When a dframe is printed, it will look something like how this looks when you click "Raw" for displaying the README:
nums     names    cities    date          zone    contaminated  
float    str      str       dframe.date   int     dframe.Bool   
nan      Bluds    BUS       None          1       True          
nan      Bluds    BUS       None          1       False     
0.5      dfsd     FUDG      2020-12-13... 2       True          
0.5      dfsd     FUDG      2020-12-13... 2       False        
1.2      qere     GOLAR     None          3       True          

Total rows: 12. Total cols: 6


dframe.Bool and dframe.date are just callable classes that coerce strings to datetime.datetimes and bools, respectively, while leaving anything already of that type alone.

Ways to make dframes:
0. Just making your own by specifying column names and types, then adding rows
		one at a time.
                
1. Reading a list of sublists (where each sublist will become a row in the dframe)
		with readlists.
                
2. Reading a dict (mapping keys to lists) with readdict.
       
3. Reading a string with readstring

4. Reading a csv file with readcsv (uses the built-in csv module)
	
5. Reading the contents of the clipboard with readclipboard (uses pyperclip)

Methods 1-5 of making dframes do automatic type inference based on regular expressions.

Major operations:

0. Seeing the column names with keys() and types with getTypes

1. Selecting a range of rows with the same [row_range,col_range] slicing method as a matrix or with the rows and cols methods.
	
2. Adding new columns with addcol(name,data,type) and removing columns with remove.

3. Adding rows with append.

4. Filtering data with select(column,thing_to_filter_for)

5. Setting types with setType, which automatically changes the data in that column.

6. Finding unique entries with unique and uniques_to_rows

7. sorting the dframe by the contents of one column with sort_by.

8. Splitting columns with split(column,sep,to_names)

9. Joining columns as strings with stringjoin.

10. Doing an SQL-style inner join with another dframe using join


Other subprojects related to the dframe class- 

1. Category, a class intended to replicate the data compression of categorical variables seen in Pandas and R. 
  In my implementation, a Category object is instantiated and linked to a column in a Cframe.
  The Category object is called on every entry in that column, and the Category's list of unique values is
  populated with every unique value it finds in that column. The values in the column are then replaced with
  the smallest unsigned integer type that can accommodate the number of distinct categories in that column.
  Whenever a function calls for values from that column, it finds a number, and the call is dispatched to the
  Category object, which gets the value at that index number.
  As with the dframe class itself, there is ABSOLUTELY NO REASON TO USE MY CATEGORY OBJECTS. Pandas DataFrames
  do substantially better data compression by default. I would be very interested to learn how.

2. Cframe, a simpler relative of the dframe that can have categories applied to its columns.
