from csvquery import Operators, Comparisons, open_csv

def usa_cases_date_range():
    dataset = open_csv("example_data/coronavirus_data.csv")
    dataset.already_indexed("location", Comparisons.strings)
    result = dataset.query({
        "location": "United States",
        "date": {
            Operators.greater_than_or_equal: "2020-03-01",
            Operators.less_than_or_equal: "2020-03-15",
            Operators.comparison: Comparisons.get_date_comparison("YYYY-MM-DD")
        }
    }).index("date", Comparisons.get_date_comparison("YYYY-MM-DD"))
    result.print_data()

def more_than_1000_cases_today():
    dataset = open_csv("example_data/coronavirus_data.csv")
    result = dataset.query({
        "total_cases": {
            Operators.greater_than: 1000,
            Operators.comparison: csvquery.Comparisons.integers
        },
        "date": "2020-03-23"
    })
    result.index("total_cases")
    result.print_data()
    return result

def save_more_than_1000_cases_today():
    more_than_1000_cases_today().save_csv("output.csv", ";", ["location","total_cases"])

def print_diversity_info():
    dataset = open_csv("example_data/census_diversity.csv", ";")
    dataset.index("asian_nh")
    dataset.print_data(dataset.column_names[2:])

usa_cases_date_range()