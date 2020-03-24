# CSV Query

A python package that allows you to execute NoSQL-style queries on CSV files.

## Downloading

```
pip install csvquery
```

## Usage

### Loading Data

Use **open_csv([path to file])** to produce a **Dataset** from a CSV file:
```python
import csvquery

dataset = csvquery.open_csv("path/to/file.csv")
```

### Indexing

Once you have a dataset, use **Dataset.index(column_name[, comparison_operation])** to sort the rows of data based on the values in a specified column. Sorting the data is optional, but doing so allows you to do binary searches which have a time complexity of just **O(log(n))**.
```python
import csvquery

dataset = csvquery.open_csv("people.csv")
dataset.index("age") # sorts people by ascending age
```
The default comparison operation used to sort the data is:
```python
lambda a, b: float(a) < float(b)
```
You can also specify a custom comparison operation to, for example, sort things alphabetically:
```python
import csvquery

dataset = csvquery.open_csv("people.csv")
dataset.index("name", lambda a, b: a < b) # alphabetical string comparisons are built-in in Python
```

### Queries

Use **Dataset.query(filter_object)** to fetch rows of data that pass through specified filters:
```python
import csvquery

dataset = csvquery.open_csv("people.csv")
dataset.index("age")

voter_dataset = dataset.query({
    "age": {          # this filter will run as a binary search since we indexed the data by age
        "gte": 18     # the query will only return people who's age is greater than or equal to 18
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
You can also use the **csvquery.Operators** class instead of operator strings:
```python
voters_named_john = voter_dataset.query({
    "name": {
        csvquery.Operators.equal : "John"
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
 - **eq**: equals (cannot be combined with any other operator)
 - **neq**: not equal
 - **lt**: less than
 - **gt**: greater than
 - **lte**: less than or equal
 - **gte**: greater than or equal

**NOTE:** If you want to use a comparison operator like **gt** or **lte** on a column that was not indexed, you need to provide a comparison operator in the **filter_object** like so:
```python
import csvquery

dataset = csvquery.open_csv("people.csv")
dataset.index("citizenship") # sorts people by citizenship

voter_dataset = dataset.query({
    "citizenship": { # binary search
        "eq": "USA"
    },
    "age" {  # not a binary search
        "gte": "18"
        "comparison": lambda a, b: int(a) < int(b) # you must provide a comparison lambda that returns true if a < b
    }
})
```

### Outputting Data

Use **Dataset.print_data([column_names])** to output your new data to the console:
```python
voter_dataset.print_data()
```
You can optionally specify which columns to print:
```python
voter_dataset.print_data(["name", "age"])
```
You can also save **Dataset** objects as CSV files using **Dataset.save_csv(filepath[, delimiter[, columns])**
```python
voter_dataset.save_csv("output.csv", ";", ["name", "age"])
```
To access the data as a two-dimensional array, just use the **data** attribute of the **Dataset** object:
```python
for row in voter_dataset.data:
    print(row[0])
    ...
```
