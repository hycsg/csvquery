# csvquery

A versatile Python package that allows you to execute MongoDB-style queries on CSV files and interact with them like SQL tables.

## Downloading

```
pip install csvquery
```

## Package contents

### open_csv(str path[, str delimiter = ","])
Produces a **Dataset** from a CSV file:
```python
from csvquery import open_csv

dataset = open_csv("path/to/file.csv")
```

### get_csv(str url[, str delimiter = ","])
Produces a **Dataset** from a URL:
```python
from csvquery import get_csv

dataset = get_csv("http://example.com/api/data.csv")
```

### parse_csv(str string[, str delimiter = ","])
Produces a **Dataset** from a string:
```python
from csvquery import parse_csv

string = "name,age\nJohn,34\nJane,33"
dataset = parse_csv(string)
```




### Operators

Stores all the valid query operator keywords as attributes. Using this class is optional as you can just use the keyword strings instead.

- **equal** = "eq"
- **not_equal** = "neq"
- **less_than** = "lt"
- **greater_than** = "gt"
- **less_than_or_equal** = "lte"
- **greater_than_or_equal** = "gte"
- **inside** = "in"
- **_not** = "not"
- **_and** = "and"
- **_or** = "or"




### Comparisons

Stores some common comparison operators.

#### integers
A lambda function to compare integer values.
```python
data.index("age", Comparisons.integers)
```

#### floats
A lambda function to compare floating-point values.
```python
data.index("rate", Comparisons.floats)
```

#### strings
A lambda function to compare strings alphabetically.
```python
data.index("name", Comparisons.strings)
```

#### default
An alias for the **floats** comparison.

#### get_date_comparison(str format_string)
Returns a function that compares dates based on the format string. See https://strftime.org/ for a list of all valid date codes.
```python
data.index("date", Comparisons.get_date_comparison("%Y-%m-%d"))
```




## The Dataset object

The Dataset object is similar to an SQL table. It can be obtained with the **open_csv**, **get_csv**, and **parse_csv** methods.

### data
A two-dimensional list of the data.
```python
for row in voter_dataset.data:
    print(row[0])
    ...
```

### fields
A list of the dataset's fields, or column names.
```python
for field in voter_dataset.fields:
    print(field)
    ...
```

### index(str field[, func comparison_operation = Comparisons.default])
Sort the rows of data based on the values in a specified field. Sorting the data is optional, but doing so allows you to do binary searches which have a time complexity of just **O(log(n))**. The **comparison_operation** argument must be a function that returns **True** when the first argument is less than the second argument, and **False** if otherwise. Import **Comparisons** for some common comparison operations. By default, the **comparison_operation** is a floating-point comparison.
```python
from csvquery import open_csv, Comparisons

dataset = open_csv("people.csv")
dataset.index("age", Comparisons.integers) # sorts people by ascending age
```
You can also make your own comparison operator.
```python
dataset.index("age", lambda a, b: a**2 < b**2)
```

### already_indexed(str field[, func comparison_operation = Comparisons.default])
Specifies that the data is already sorted by a certain field, allowing binary searches without re-sorting.
```python
from csvquery import open_csv, Comparisons

dataset = open_csv("people.csv")
dataset.already_indexed("name", Comparisons.strings)
```

### query(dict filter_object)
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
You can also use the **csvquery.Operators** class instead of operator strings:
```python
from csvquery import Operators

voters_named_john = voter_dataset.query({
    "name": {
        Operators.equal : "John"
    }
})
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

### query_one(dict filter_object)
Returns the first row that matches the **filter_object** as a **Dataset**:
```python
john_doe = people_dataset.query_one({"phone":"555-123-4567"})
```

### select(list fields)
Returns the a new **Dataset** object with only the specified fields.
```python
names_and_ages = people.select(["name", "age"])
```

### select_as(dict fields)
Returns the a new **Dataset** object with only the specified fields, except the fields are renamed according to the **fields** dictionary.
```python
names_and_ages = people.select_as({
    "first_and_last_name": "name",
    "years_of_oldness": "age"
})
```

### select_unique(str field)
Returns a new **Dataset** object with only the specified field, and removes any duplicate values so that each value is unique.
```python
names = people.select_unique("name")
```

### add_field(str field[, func derivation = lambda r:""])
Adds another field with the specified name. By default, the field will be filled with blank values.
```python
people.add_field("status")
```
You can optionally specify a function that takes the data in that row as a dictionary and outputs the new derived value per row.
```python
people.add_field("full_name", lambda row: row["first_name"] + " " + row["last_name"]])
```

### remove_fields(list fields)
Removes the specified fields from the **Dataset**.
```python
people.remove_fields(["status", "full_name"])
```

### rename_fields(dict fields)
Renames fields according to the **fields** dictionary argument.
```python
people.rename_fields({
    "first_and_last_name": "name",
    "years_of_oldness": "age"
})
```

### replace(list fields, func function)
Replaces the values in the specified **fields** list argument using the **function** argument, which takes the current value as input and outputs the new value.
```python
people.replace(["first name", "last name"], lambda v: v.lower()) # makes all "first name" and "last name" values lower case
```

### replace_derived(list fields, func derivation)
Replaces the values in the specified **fields** list argument using the **function** argument, which takes the row as a dictionary as input and outputs the new value.
```python
def birthday_to_age(row):
    bday = datetime.strptime(row["date_of_birth"], "%Y-%m-%d")
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

people.replace_derived(["age"], birthday_to_age)
```

### join(Dataset other_dataset, list common_fields[, bool remove = True])
Adds fields from **other_dataset** to this **Dataset** and matches the rows by referencing the **common_fields** list argument. The **common_fields** list must have the field from the current **Dataset** and the field from the other **Dataset** in that order. By default, this method will remove the common field after the operation, but you can prevent this by setting the **remove** argument to **False**.
```python
locations = open_csv("locations.csv") # has an id field
people = open_csv("people.csv") # has a location_id field that matches people to locations

people.join(locations, ["location_id", "id"])
```

### to_dictionary()
Returns a the data as a dictionary if the **Dataset** has only one row (as a result of a **query_one** operation, for example).
```python
john_doe = people.query_one({"phone":"555-123-4567"}) # dataset is one row high
print(john_doe.to_dictionary()["address"])
```

### to_list()
Returns a the data as a list if the **Dataset** has only one column (as a result of a **select** operation, for example).
```python
texans = people.query({"state":"TX"}).select("name") # dataset is one column wide
texan_names = texans.to_list()
```

### count([list fields])
If the **fields** argument is left blank, returns the number of rows in the **Dataset**.
```python
number_of_people = people.count()
```
If otherwise, returns the number of rows in which the all of the specified fields are not empty.
```python
number_of_with_jobs = people.count(["job"]) # assuming the "job" field is left blank for unemployed people
```

### sum(str field)
Returns a sum of all the values in that field.
```python
total_net_worth = people.sum("net_worth")
```

### average(str field)
Returns a average of all the values in that field.
```python
average_net_worth = people.average("net_worth")
```

### print_table([list fields])
Outputs your data to the console in a nice table.
```python
voter_dataset.print_table()
```
You can optionally specify which columns to print.
```python
voter_dataset.print_table(["name", "age"])
```

### save_csv(str filepath[, str delimiter = ","[, fields = <all>]])
Saves the **Dataset** to a file. If no fields are specified, all fields will be saved.
```python
voter_dataset.save_csv("output.csv", ";", ["name", "age"])
```


## More examples

### SQL equivalent

#### Classic SQL query

```sql
SELECT name, age FROM people
WHERE age >= 18 AND citizenship = "USA";
```

#### Python MongoDB-style query

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

### The "eq" operator is optional in the top level of the dictionary

```python
dataset = csvquery.open_csv("people.csv")
dataset.query({
    "name":"John"
})
```

### Selecting one field

```python
people.select("name") # doesn't need to be a list if it's just one
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