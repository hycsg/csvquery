from csvquery import *

def usa_cases_date_range():
    dataset = open_csv("data/coronavirus_data.csv")
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
    open_csv("data/coronavirus_data.csv")
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
    dataset = open_csv("data/coronavirus_data.csv")
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

def usa_or_uk():
    dataset = open_csv("data/coronavirus_data.csv").query({
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
    open_csv("data/coronavirus_data.csv")
        .rename_fields({"total_cases":"cases"})
        .query({"location":"United States", "cases":{"gt":10, "comparison":Comparisons.integers}})
        .select(["date", "cases"])
        .replace("date", lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%m-%d"))
        .print_table()
    )


def new_column():
    (
    open_csv("data/coronavirus_data.csv")
        .rename_fields({"total_cases":"cases"})
        .query({"location":"United States", "cases":{"gt":10, "comparison":Comparisons.integers}})
        .select(["date", "cases"])
        .add_field("log(cases)", lambda row: str(round(math.log(float(row["cases"])), 3)).ljust(5, "0"))
        .print_table()
    )

def country_count():
    data = open_csv("data/coronavirus_data.csv")
    countries = data.select_unique("location")
    print(countries.count())
