from csvquery import *

today = "2020-03-23"

def stats():
    dataset = open_csv("data/coronavirus_data.csv")
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

def select_as():
    dataset = open_csv("data/coronavirus_data.csv").query({"location":"United States"})
    dataset.select_as({"total_cases":"cases", "date":"time"}).print_table()

def rename():
    dataset = open_csv("data/coronavirus_data.csv").query({"location":"United States"})
    dataset.rename_fields({"total_cases":"cases"}).select(["date", "cases"]).print_table()

def no_new_zealand():
    (
    open_csv("data/coronavirus_data.csv")
        .query({"location":{"neq":"New Zealand"}})
        .save_csv("output.csv")
    )

stats()
# select_as()
# rename()
# no_new_zealand()