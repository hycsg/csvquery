import super_csv

def usa_date_range():
    dataset.index("location", lambda a,b: a<b)
    result = dataset.query({
        "location": {
            "eq": "United States"
        },
        "date": {
            "gt": "2020-02-29",
            "lt": "2020-03-16",
            "comparison": lambda a,b: a<b
        }
    })
    result.print_data()

def more_than_10000_cases():
    dataset.index("total_cases")
    result = dataset.query({
        "total_cases": {
            "gt": "10000"
        }
    })
    result.print_data()

dataset = super_csv.open_csv("example_data/coronavirus_data.csv")
usa_date_range()