import csv_query

def usa_cases_date_range():
    dataset = csv_query.open_csv("example_data/coronavirus_data.csv")
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

def more_than_1000_cases_today_sort_before():
    dataset = csv_query.open_csv("example_data/coronavirus_data.csv")
    dataset.index("total_cases")
    result = dataset.query({
        "total_cases": {
            "gt": 1000
        },
        "date": {
            "eq": "2020-03-23"
        }
    })
    result.print_data()

def more_than_1000_cases_today_sort_after():
    dataset = csv_query.open_csv("example_data/coronavirus_data.csv")
    result = dataset.query({
        "total_cases": {
            "gt": 1000,
            "comparison": lambda a,b: int(a)<int(b)
        },
        "date": {
            "eq": "2020-03-23"
        }
    })
    result.index("total_cases")
    result.print_data()

def diversity_info():
    dataset = csv_query.open_csv("example_data/census_diversity.csv", ";")
    dataset.index("totpop10")
    dataset.print_data(dataset.column_names[2:])

more_than_1000_cases_today_sort_after()