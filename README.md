# CSV Query

A versatile python package that allows you to execute MongoDB-style queries on CSV files.

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
Use **Dataset.query_one(filter_object)** if you're just looking for one result:
```python
john_doe = people_dataset.query_one({"phone":"555-123-4567"})
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
 - **in**: inside the provided array

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
### Selecting fields
You can use **Dataset.select([fields])** to receive a new dataset with only the specified fields:
```python
names_and_nationalities = people.select(["name", "nationality"])
```

If the **Dataset** is effectively one-dimensional either horizontally or vertically as a result of using **Dataset.query_one([filter_object])** or **Dataset.select([fields])**, you can use **Dataset.to_dictionary()** or **Dataset.to_list()**:
```python
texans = people.query({"state":"TX"}).select("name") # dataset is one column wide
texan_names = texans.to_list()
```
```python
john_doe = people.query_one({"phone":"555-123-4567"}) # dataset is one row high
print(john_doe.to_dictionary()["address"])
```

### Outputting data

Use **Dataset.print_table([column_names])** to output your new data to the console:
```python
voter_dataset.print_table()
```
You can optionally specify which columns to print:
```python
voter_dataset.print_table(["name", "age"])
```
You can also save **Dataset** objects as CSV files using **Dataset.save_csv(filepath[, delimiter[, columns])**
```python
voter_dataset.save_csv("output.csv", ";", ["name", "age"])
```
To access the data directly as a two-dimensional array, just use the **data** attribute of the **Dataset** object:
```python
for row in voter_dataset.data:
    print(row[0])
    ...
```

## More examples

### SQL translation

**Classic SQL query**

```sql
SELECT name, age FROM people
WHERE age >= 18 AND citizenship = "USA";
```

**Python MongoDB-style query**

```python
voters = people.query({
    "age": {
        "gte": 18
    },
    "citizenship": "USA"
}).select(["name", "age"])
```

### Printing certain columns

```python
dataset = open_csv("people.csv")
dataset.print_table(dataset.fields[2:5])
```

### Rewriting a CSV file with fewer columns and a different delimiter

```python
dataset = open_csv("people.csv")
dataset.save_csv("people.csv", ";", dataset.fields[2:5])
```

### The "eq" operator is optional

```python
dataset = csvquery.open_csv("people.csv")
dataset.query({
    "name":"John"
})
```

### Selecting one field

```python
people.select("name") # doesn't need to be an array
```

### Chaining

```python
(
open_csv("people.csv")
    .index("age")
    .query({"age":{"gte":18}, "citizenship":"USA"})
    .select(["name", "id"])
    .save_csv("voters.csv", ",")
    .print_table()
)
```

### Already sorted CSV

```python
people = open_csv("people_sorted_by_age.csv")

people.already_indexed("age", Comparisons.integer) # this allows you to do binary searches
babies = people.query({"age": 0}).print_table(["name"])
```

### Relational data
```python
from csvquery import open_csv
import statistics

houses = open_csv("houses.csv")
people = open_csv("people.csv")

texas_homes = houses.query({"state":"TX"})
texas_homeowner_ids = texas_homes.select("id").to_list()
texas_homeowners = people.query({
    "id": {
        "in": texas_homeowner_ids
    }
})
texas_homeowner_ages = texas_homeowners.select("age").to_list()
average_texas_homeowner_age = statistics.mean(texas_homeowner_ages)
```
