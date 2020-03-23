# Super CSV
A python library that allows you to use NoSQL-style queries on CSV files.
## Downloading
Just download **super_csv.py**.
## Usage
### Loading Data
Use **open_csv(path)** to produce a **Dataset** from a CSV file:
```python
import super_csv

dataset = super_csv.open_csv("path/to/file.csv")
```
### Indexing
Once you have a dataset, use **index(column_name[, comparison_operation])** to sort the rows of data based on the values in a specified column. Sorting the data is optional, but doing so allows you to do binary searches which have a time complexity of just **O(log(n))**.
```python
import super_csv

dataset = super_csv.open_csv("people.csv")
dataset.index("age") # sorts people by ascending age
```
The default comparison operation used to sort the data is:
```python
lambda a, b: float(a) < float(b)
```
You can also specify a custom comparison operation to, for example, sort things alphabetically:
```python
import super_csv

dataset = super_csv.open_csv("people.csv")
dataset.index("name", lambda a, b: a < b) # alphabetical string comparisons are built-in in Python
```
### Queries
Use **query(query_object)** to query certain rows of your data.
