import csvquery

def usa_cases_date_range():
    dataset = csvquery.open_csv("example_data/coronavirus_data.csv")
    result = dataset.query({
        "location": {
            csvquery.Operators.equal: "United States"
        },
        "date": {
            csvquery.Operators.greater_than_or_equal: "2020-03-01",
            csvquery.Operators.less_than_or_equal: "2020-03-15",
            csvquery.Operators.comparison: csvquery.Comparisons.get_date_comparison("YYYY-MM-DD")
        }
    }).index("date", csvquery.Comparisons.get_date_comparison("YYYY-MM-DD"))
    result.print_data()

def more_than_1000_cases_today():
    dataset = csvquery.open_csv("example_data/coronavirus_data.csv")
    result = dataset.query({
        "total_cases": {
            csvquery.Operators.greater_than: 1000,
            csvquery.Operators.comparison: csvquery.Comparisons.integers
        },
        "date": {
            csvquery.Operators.equal: "2020-03-23"
        }
    })
    result.index("total_cases")
    result.print_data()
    return result

def save_more_than_1000_cases_today():
    more_than_1000_cases_today().save_csv("output.csv", ";", ["location","total_cases"])

def print_diversity_info():
    dataset = csvquery.open_csv("example_data/census_diversity.csv", ";")
    dataset.index("asian_nh")
    dataset.print_data(dataset.column_names[2:])

usa_cases_date_range()