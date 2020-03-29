from csvquery import *

def two_tables(): # get all Directors from Redwood City
    contacts = open_csv("data/relational/contacts.csv")
    addresses = open_csv("data/relational/addresses.csv")
    
    redwood_ids = addresses.query({"city":"Redwood City"}).select(["location_id"]).to_list()
    redwood_directors = contacts.query({
        "title": "Director",
        "location_id": {
            Operators.inside: redwood_ids
        }
    }).select(["name", "id"])
    redwood_directors.print_table()

def join_tables():
    contacts = open_csv("data/relational/contacts.csv").select(["location_id", "name", "title", "email"])
    addresses = (
    open_csv("data/relational/addresses.csv")
        .add_field("full_address")
        .replace_derived("full_address", lambda r: "{0} {1}, {2} {3}".format(r["address_1"], r["city"], r["state_province"], r["postal_code"]))
        .select(["location_id", "full_address"])
    )
    
    contacts.join(addresses, "location_id").print_table()

join_tables()