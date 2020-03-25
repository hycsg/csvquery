from csvquery import Operators, Comparisons, open_csv

today = "2020-03-23"

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

def relational_data(): # get all Directors from Redwood City
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

relational_data()