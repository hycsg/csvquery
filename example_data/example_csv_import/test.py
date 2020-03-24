import csvquery

dataset = csvquery.open_csv("SalesJan2009.csv")
dataset.index("Name", lambda a, b: a < b)

data = dataset.query({
    "Name": {
        "eq": "apartment"   
    }
})

data.print_data()

