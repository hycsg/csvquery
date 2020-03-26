from csvquery import Operators, Comparisons, open_csv
import time, math
from datetime import datetime

today = "2020-03-23"

# benchmark util
def benchmark(func, start_func=lambda:0, times=5, digits=3):
    start = time.time()
    start_func()
    for _ in range(times):
        func()
    elapsed = round(time.time() - start, digits)
    print("elapsed time: "+str(elapsed).ljust(digits + 2, "0"))

def usa_cases_date_range():
    dataset = open_csv("example_data/coronavirus_data.csv")
    dataset.already_indexed("location", Comparisons.strings)
    result = dataset.query({
        "location": "United States",
        "date": {
            Operators.greater_than_or_equal: "2020-03-01",
            Operators.less_than_or_equal: "2020-03-15",
            Operators.comparison: Comparisons.get_date_comparison("%Y-%m-%d")
        }
    }).index("date", Comparisons.get_date_comparison("%Y-%m-%d")).select(["total_cases"])
    result.print_table()

def usa_cases_today():
    (
    open_csv("example_data/coronavirus_data.csv")
        .already_indexed("location", Comparisons.strings)
        .query({
            "location": "United States"
        })
        .already_indexed("date", Comparisons.get_date_comparison("%Y-%m-%d"))
        .query_one({
            "date": today
        })
        .select(["location", "total_cases", "total_deaths"])
        .print_table()
    )

def more_than_1000_cases_today():
    dataset = open_csv("example_data/coronavirus_data.csv")
    result = dataset.query({
        "total_cases": {
            Operators.greater_than: 1000,
            Operators.comparison: Comparisons.integers
        },
        "date": today
    })
    result.index("total_cases")
    result.print_table()
    return result

def save_more_than_1000_cases_today():
    more_than_1000_cases_today().select(["location","total_cases"]).save_csv("output.csv", ";")

def print_diversity_info():
    dataset = open_csv("example_data/census_diversity.csv", ";")
    dataset.index("asian_nh")
    dataset.print_table(dataset.column_names[2:])

def two_tables(): # get all Directors from Redwood City
    contacts = open_csv("example_data/relational/contacts.csv")
    addresses = open_csv("example_data/relational/addresses.csv")
    
    redwood_ids = addresses.query({"city":"Redwood City"}).select(["location_id"]).to_list()
    redwood_directors = contacts.query({
        "title": "Director",
        "location_id": {
            Operators.inside: redwood_ids
        }
    }).select(["name", "id"])
    redwood_directors.print_table()

def stats():
    dataset = open_csv("example_data/coronavirus_data.csv")
    cases_today = dataset.query({
        "date": today,
        "location": {
            Operators.not_equal: "World"
        }
    }).index("date", Comparisons.get_date_comparison("%Y-%m-%d")).select("total_cases")
    
    cases_today.print_table()
    print(cases_today.sum())
    print(cases_today.count())
    print(cases_today.average())

def binary_vs_sequential(times = 5000):
    dataset = open_csv("example_data/coronavirus_data.csv").query({"date":today})

    print("\nWITHOUT INDEXING:")
    benchmark(lambda: dataset.query({"total_cases":{"gt":100, "comparison":Comparisons.integers}}), lambda: 0, times)
    print("\nWITH INDEXING:")
    benchmark(lambda: dataset.query({"total_cases":{"gt":100}}), lambda: dataset.index("total_cases", Comparisons.integers), times)
    print()

    dataset.index("total_cases")

def select_as():
    dataset = open_csv("example_data/coronavirus_data.csv").query({"location":"United States"})
    dataset.select_as({"total_cases":"cases", "date":"time"}).print_table()

def rename():
    dataset = open_csv("example_data/coronavirus_data.csv").query({"location":"United States"})
    dataset.rename_fields({"total_cases":"cases"}).select(["date", "cases"]).print_table()

def usa_or_uk():
    dataset = open_csv("example_data/coronavirus_data.csv").query({
        "location": {
            "or": [
                {Operators.equal: "United Kingdom"},
                {Operators.equal: "United States"},
            ]
        },
        "date": {
            Operators.greater_than_or_equal: "2020-03-01",
            Operators.less_than_or_equal: "2020-03-2",
            Operators.comparison: Comparisons.get_date_comparison("%Y-%m-%d")
        }
    })
    dataset.print_table()

def short_date():
    (
    open_csv("example_data/coronavirus_data.csv")
        .rename_fields({"total_cases":"cases"})
        .query({"location":"United States", "cases":{"gt":10, "comparison":Comparisons.integers}})
        .select(["date", "cases"])
        .replace("date", lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%m-%d"))
        .print_table()
    )

def no_new_zealand():
    (
    open_csv("example_data/coronavirus_data.csv")
        .query({"location":{"neq":"New Zealand"}})
        .save_csv("output.csv")
    )

def new_column():
    (
    open_csv("example_data/coronavirus_data.csv")
        .rename_fields({"total_cases":"cases"})
        .query({"location":"United States", "cases":{"gt":10, "comparison":Comparisons.integers}})
        .select(["date", "cases"])
        .add_field("log(cases)", lambda row: str(round(math.log(float(row["cases"])), 3)).ljust(5, "0"))
        .print_table()
    )

def join_tables():
    contacts = open_csv("example_data/relational/contacts.csv").select(["location_id", "name", "title", "email"])
    addresses = (
    open_csv("example_data/relational/addresses.csv")
        .add_field("full_address")
        .replace_derived("full_address", lambda r: "{0} {1}, {2} {3}".format(r["address_1"], r["city"], r["state_province"], r["postal_code"]))
        .select(["location_id", "full_address"])
    )
    
    contacts.join(addresses, "location_id").print_table()
    
join_tables()