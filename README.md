# csvquery

## Downloading

```
pip install csvquery
```

## Package contents

### open_csv(path[, delimiter=","])
Produces a **Dataset** from a CSV file:
```python
from csvquery import open_csv

dataset = open_csv("path/to/file.csv")
```

### get_csv(url[, delimiter=","])
Produces a **Dataset** from a URL:
```python
from csvquery import get_csv

dataset = get_csv("http://example.com/api/data.csv")
```

### parse_csv(string[, delimiter=","])
Produces a **Dataset** from a string:
```python
from csvquery import parse_csv

string = "name,age\nJohn,34\nJane,33"
dataset = parse_csv(string)
```




### Operators

Stores all the valid query operator keywords. Using this class is optional as you can just use the keyword strings instead.

#### Attributes

**equal** = "eq"
**not_equal** = "neq"
**less_than** = "lt"
**greater_than** = "gt"
**less_than_or_equal** = "lte"
**greater_than_or_equal** = "gte"
**inside** = "in"
**_not** = "not"
**_and** = "and"
**_or** = "or"




### Comparisons

Stores some common comparison operators.

#### Attributes

##### integers
A lambda function to compare integer values.
```python
data.index("age", Comparisons.integers)
```

##### floats
A lambda function to compare floating-point values.
```python
data.index("rate", Comparisons.floats)
```

##### strings
A lambda function to compare strings alphabetically.
```python
data.index("name", Comparisons.strings)
```

#### Methods

##### get_date_comparison(format_string)
Returns a function that compares dates based on the format string. See https://strftime.org/ for a list of all valid date codes.
```python
data.index("date", Comparisons.get_date_comparison("%Y-%m-%d"))
```




## The Dataset object

The Dataset object is similar to an SQL table. It can be obtained with the **open_csv**, **get_csv**, and **parse_csv** methods.

### Attributes

#### data
A two-dimensional list of the data.
```python
for row in voter_dataset.data:
    print(row[0])
    ...
```

#### fields
A list of the dataset's fields, or column names.
```python
for field in voter_dataset.fields:
    print(field)
    ...
```

### Methods

#### index(field[, comparison_operation])
Sort the rows of data based on the values in a specified field. Sorting the data is optional, but doing so allows you to do binary searches which have a time complexity of just **O(log(n))**. The **comparison_operation** parameter must be a function that returns **True** when the first argument is less than the second argument, and **False** if otherwise. Import **Comparisons** for some common comparison operations. By default, the **comparison_operation** is a floating-point comparison.
```python
from csvquery import open_csv, Comparisons

dataset = open_csv("people.csv")
dataset.index("age", Comparisons.integers) # sorts people by ascending age
```
You can also make your own comparison operator.
```python
dataset.index("age", lambda a, b: a**2 < b**2)
```

#### already_indexed(field[, comparison_operation])
Specifies that the data is already sorted by a certain field, allowing binary searches without re-sorting.
```python
from csvquery import open_csv, Comparisons

dataset = open_csv("people.csv")
dataset.already_indexed("name", Comparisons.strings)
```

#### query(filter_object)
Returns all rows that match the **filter_object** as another **Dataset**.
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

#### query_one(filter_object)
Returns the first row that matches the **filter_object** as a **Dataset**:
```python
john_doe = people_dataset.query_one({"phone":"555-123-4567"})
```
You can also use the **csvquery.Operators** class instead of operator strings:
```python
from csvquery import Operators

voters_named_john = voter_dataset.query({
    "name": {
        "eq" : "John"
    }
})
```
The general structure of a **filter_object** is as follows:
```python
{
    "field_1": {
        "operator_1": "value",
        "operator_2": "value",
        "operator_3": {
            "nested_operator": "value"
        },
        ...
        "operator_n": "value_n"
    },
    "field_2": {
        ...
    },
    ...
    "field_3": {
        ...
    }
}
```
If you want to use a comparison operator like **gt** or **lte** on a column that was not indexed, you need to provide a comparison operator in the **filter_object** like so:
```python
from csvquery import open_csv, Operations, Comparisons

dataset = open_csv("people.csv")
dataset.index("citizenship") # sorts people by citizenship

voter_dataset = dataset.query({
    "citizenship": { # binary search
        "eq": "USA"
    },
    "age" {  # not a binary search
        "gte": "18"
        "comparison": Comparisons.integers
    }
})
```

#### select(fields)
Returns the a new **Dataset** object with only the specified fields.
```python
names_and_nationalities = people.select(["name", "nationality"])
```

#### select_as(fields)

#### select_unique(field)

#### add_field(field[, derivation])

#### remove_fields(fields)

#### rename_fields(fields)

#### replace(fields, function)

#### replace_derived(fields, derivation)

#### join(other_dataset, common_fields[, remove])

#### to_dictionary()
Returns a the data as a dictionary if the **Dataset** has only one row (as a result of a **query_one** operation, for example).
```python
john_doe = people.query_one({"phone":"555-123-4567"}) # dataset is one row high
print(john_doe.to_dictionary()["address"])
```

#### to_list()
Returns a the data as a list if the **Dataset** has only one column (as a result of a **select** operation, for example).
```python
texans = people.query({"state":"TX"}).select("name") # dataset is one column wide
texan_names = texans.to_list()
```

#### count([fields])
If the **fields** parameter is left blank, returns the number of rows in the **Dataset**.
```python
number_of_people = people.count()
```
If otherwise, returns the number of rows in which the all of the specified fields are not empty.
```python
number_of_with_jobs = people.count(["job"]) # assuming the "job" field is left blank for unemployed people
```

#### sum(field)
Returns a sum of all the values in that field.
```python
total_net_worth = people.sum("net_worth")
```

#### average(field)
Returns a average of all the values in that field.
```python
average_net_worth = people.average("net_worth")
```

#### print_table([fields])
Outputs your data to the console in a nice table.
```python
voter_dataset.print_table()
```
You can optionally specify which columns to print.
```python
voter_dataset.print_table(["name", "age"])
```

#### save_csv(filepath[, delimiter[, fields]])
Saves the **Dataset** to a file.
```python
voter_dataset.save_csv("output.csv", ";", ["name", "age"])
```




# More examples

## SQL translation

### Classic SQL query

```sql
SELECT name, age FROM people
WHERE age >= 18 AND citizenship = "USA";
```

### Python MongoDB-style query

```python
voters = people.query({
    "age": {
        "gte": 18
    },
    "citizenship": "USA"
}).select(["name", "age"])
```

## Printing certain columns

```python
dataset = open_csv("people.csv")
dataset.print_table(dataset.fields[2:5])
```

## Rewriting a CSV file with fewer columns and a different delimiter

```python
dataset = open_csv("people.csv")
dataset.save_csv("people.csv", ";", dataset.fields[2:5])
```

## The "eq" operator is optional

```python
dataset = csvquery.open_csv("people.csv")
dataset.query({
    "name":"John"
})
```

## Selecting one field

```python
people.select("name") # doesn't need to be a list if it's just one
```

## Chaining

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