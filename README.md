# Super CSV

A python library that allows you to use NoSQL-style queries on CSV files.

## Downloading

Download **super_csv.py** and add it to your project folder (WIP).

## Usage

### Loading Data

Use **open_csv(path)** to produce a **Dataset** from a CSV file:
```python
import super_csv

dataset = super_csv.open_csv("path/to/file.csv")
```

### Indexing

Once you have a dataset, use **Dataset.index(column_name[, comparison_operation])** to sort the rows of data based on the values in a specified column. Sorting the data is optional, but doing so allows you to do binary searches which have a time complexity of just **O(log(n))**.
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

Use **Dataset.query(filter_object)** to fetch rows of data that pass through specified filters:
```python
import super_csv

dataset = super_csv.open_csv("people.csv")
dataset.index("age")

voter_dataset = dataset.query({
    "age": {          # this filter will run as a binary search since we indexed the data by age
        "gt": "17"    # the query will only return people who's age is greater than 17
    },
    "citizenship" {   # this will run after the binary search to filter the narrowed-down data
        "eq": "USA"   # people will only pass this filter if their "citizenship" field is equal to "USA"
    }
})
```
Since **Dataset.query(filter_object)** returns another **Dataset**, you can query the resulting dataset as well:
```python
voters_named_john = voter_dataset.query({
    "name": {
        "eq": "John"
    }
})
```
The general structure of a **filter_object** is as follows:
```python
{
    "column_name_1": {
        "operator_1": "value_1",
        "operator_2": "value_2",
        ...
        "operator_N": "value_N"
    },
    "column_name_2": {
        ...
    },
    ...
    "column_name_N": {
        ...
    }
}
```


**Valid Operators**
 - **eq**: equals (cannot be combined with **lt** or **gt**)
 - **lt**: less than (can be combined with **gt**)
 - **gt**: greater than (can be combined with **lt**)


**NOTE:** If you want to use a non-**eq** operator in a filter that uses a column that was not indexed, you need to provide a comparison operator like so:
```python
import super_csv

dataset = super_csv.open_csv("people.csv")
dataset.index("citizenship") # sorts people by citizenship

voter_dataset = dataset.query({
    "citizenship": { # binary search
        "eq": "USA"
    },
    "age" {  # not a binary search
        "gt": "17"
        "comparison": lambda a, b: int(a) < int(b) # you must provide a comparison lambda that returns true if argument 1 is less than argument 2
    }
})
```

### Outputing Data

Finally, use **Dataset.print_data()** to output your new data to the console:
```python
voter_dataset.print_data()
```
Or, to access the data as a two-dimensional array, just access the **data** attribute of the **Dataset** object:
```python
for row in voter_dataset.data:
    print(row[0])
    ...
```

More output options are coming soon.
