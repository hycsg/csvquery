# CSV Query

A python package that allows you to execute NoSQL-style queries on CSV files.

## Downloading

```
pip install csvquery
```

## Usage

### Loading data

Use **open_csv(path)** to produce a **Dataset** from a CSV file:
```python
from csvquery import open_csv

dataset = open_csv("path/to/file.csv")
```

### Indexing

Once you have a dataset, use **Dataset.index(column_name[, comparison_operation])** to sort the rows of data based on the values in a specified column. Sorting the data is optional, but doing so allows you to do binary searches which have a time complexity of just **O(log(n))**.
```python
from csvquery import open_csv

dataset = open_csv("people.csv")
dataset.index("age") # sorts people by ascending age
```
The default comparison operation used to sort the data is a float comparison. You can import the **csvquery.Comparisons** class to use other common comparison operations:
```python
from csvquery import open_csv, Comparisons

dataset = open_csv("people.csv")
dataset.index("name", Comparisons.strings)
```
```python
Comparisons.integers    >> lambda a, b: int(a) < int(b)
Comparisons.floats      >> lambda a, b: float(a) < float(b)
Comparisons.strings     >> lambda a, b: a < b
```
The **csvquery.Comparisons** class also has a static method called **get_date_comparison(format_string)** which returns a custom date comparison function (based on the specified format) that you can pass as the comparison operation:
```python
from csvquery import open_csv, Comparisons

dataset = open_csv("people.csv")
data.index("date_of_birth", Comparisons.get_date_comparison("YYYY-MM-DD"))
```
You can also specify your own custom comparison operation:
```python
from csvquery import open_csv

dataset = open_csv("people.csv")
dataset.index("name", lambda a, b: a**2 < b**2)
```

### Queries

Use **Dataset.query(filter_object)** to fetch rows of data that pass through specified filters:
```python
from csvquery import open_csv

dataset = open_csv("people.csv")
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
from csvquery import Operators

voters_named_john = voter_dataset.query({
    "name": {
        Operators.equal : "John"
    }
})
```
The general structure of a **filter_object** is as follows:
```python
{
    "column_name_1": {
        Operators.a: "value_1",
        Operators.b: "value_2",
        ...
        Operators.x: "value_x"
    },
    "column_name_2": {
        ...
    },
    ...
    "column_name_x": {
        ...
    }
}
```
**Valid operators**
 - **eq**: equals (cannot be combined with any other operator, including itself)
 - **neq**: not equal
 - **lt**: less than
 - **gt**: greater than
 - **lte**: less than or equal
 - **gte**: greater than or equal

**NOTE:** If you want to use a comparison operator like **gt** or **lte** on a column that was not indexed, you need to provide a comparison operator in the **filter_object** like so:
```python
from csvquery import open_csv, Operations, Comparisons

dataset = open_csv("people.csv")
dataset.index("citizenship") # sorts people by citizenship

voter_dataset = dataset.query({
    "citizenship": { # binary search
        Operations.equal: "USA"
    },
    "age" {  # not a binary search
        Operations.greater_than_or_equal: "18"
        Operations.comparison: Comparisons.integers
    }
})
```

### Outputting data

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

## More examples

### SQL equivalent

**SQL query**

```sql
SELECT name, age FROM people
WHERE age >= 18 AND citizenship = "USA";
```

**Python NoSQL query**

```python
voters = people.query({
    "age": {
        "gte": 18
    },
    "citizenship": "USA"
})
voters.print_data(["name", "age"])
```

### Printing certain columns

```python
dataset = open_csv("people.csv")
dataset.print_data(dataset.column_names[2:5])
```

### Rewriting a CSV file with fewer columns and a different delimiter

```python
dataset = open_csv("people.csv")
dataset.save_csv("people.csv", ";", dataset.column_names[2:5])
```

### The "eq" operator is optional

```python
dataset = csvquery.open_csv("people.csv")
dataset.query({
    "name":"John"
})
```

### Chaining

```python
(
open_csv("people.csv")
    .index("age")
    .query({"age":{"gte":18}, "citizenship":"USA"})
    .print_data(["name", "id"])
    .save_csv("voters.csv", ",", ["name", "id"])
)
```

### Already sorted CSV

```python
people = open_csv("people_sorted_by_age.csv")

people.already_indexed("age", Comparisons.integer) # this allows you to do binary searches
babies = people.query({"age": 0}).print_data(["name"])
```
