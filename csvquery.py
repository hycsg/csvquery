import sys, math, types, csv, copy, concurrent.futures
from datetime import datetime


class Operators:
    equal = "eq"
    not_equal = "neq"
    less_than = "lt"
    greater_than = "gt"
    less_than_or_equal = "lte"
    greater_than_or_equal = "gte"
    inside = "in"
    _not = "not"
    _and = "and"
    _or = "or"

    comparison = "comparison"

class Comparisons:
    integers = lambda a, b: int(a) < int(b)
    floats = lambda a, b: float(a) < float(b)
    strings = lambda a, b: a < b

    default = floats
    
    @staticmethod
    def get_date_comparison(format_string):        
        return lambda a, b: datetime.strptime(a, format_string) < datetime.strptime(b, format_string)

class Dataset:

    # UTILITY

    def __init__(self):
        self.data = []
        self.fields = []
        self.indexed_field = ""
        self.indexed_comparison = Comparisons.default

    def get_field_ids(self, field_names):
        if type(field_names) is str:
            field_names = [field_names]
        elif type(field_names) is not list and type(field_names) is not tuple:
            error_message("the supplied list of fields is not a list nor a tuple")
            return []
        
        field_ids = []
        for field in field_names:
            if not field in self.fields:
                error_message("field '{0}' does not exist, skipping".format(field))
                field_names.remove(field)
                continue
            field_ids.append(self.fields.index(field))
        field_ids.sort()
        return field_ids

    def row_to_dict(self, row):
        return {field: row[i] for i, field in enumerate(self.fields)}

    # USER

    def already_indexed(self, field, comparison = Comparisons.default):
        if type(comparison) is not types.FunctionType:
            error_message("the supplied comparison operator is not a function or lambda")
            return self
        if type(field) is not str:
            error_message("the supplied field is not a string")
            return self
        
        self.indexed_field = field
        self.indexed_comparison = comparison
        return self

    def index(self, field, comparison = Comparisons.default):
        if type(comparison) is not types.FunctionType:
            error_message("the supplied comparison operator is not a function or lambda")
            return self
        if type(field) is not str:
            error_message("the supplied field is not a string")
            return self
        if not field in self.fields:
            error_message("field '{0}' does not exist, skipping index".format(field))
            return self

        def quick_sort(field, low, high, comparison): 
            if low < high: 
                p = partition(field, low, high, comparison)
        
                quick_sort(field, low, p-1, comparison)
                quick_sort(field, p+1, high, comparison)
        
        def partition(field, low, high, comparison):
            i = low-1
            pivot = self.data[high][field]
        
            for j in range(low, high):
                if comparison(self.data[j][field], pivot):
                    i = i+1
                    self.data[i], self.data[j] = self.data[j], self.data[i]
            
            self.data[i+1], self.data[high] = self.data[high], self.data[i+1]

            return i+1
        
        if type(comparison) is not types.FunctionType:
            error_message("indexing comparison is not a function, using default comparison instead")
            comparison = Comparisons.default
        
        sys.setrecursionlimit(10000)
        quick_sort(self.fields.index(field), 0, len(self.data)-1, comparison)
        self.indexed_field = field
        self.indexed_comparison = comparison
        
        return self

    def query(self, query_object=None):
        if query_object == None:
            return self
        if type(query_object) is not dict:
            return Dataset()
        for field, operators in query_object.items():
            if type(operators) is not dict:
                query_object[field] = {Operators.equal: operators}

        def double_binary_search(key, conditions):

            def binary_search(low, high, comparison, direction):
                if low + 1 == high:
                    return high
                lower_middle_index = math.floor((high+low)/2)
                upper_middle_index = math.ceil((high+low)/2)
                median = self.data[upper_middle_index][key]
                if comparison(median) == direction:
                    return binary_search(lower_middle_index, high, comparison, direction)
                else:
                    return binary_search(low, upper_middle_index, comparison, direction)

            lowest = 0
            highest = len(self.data) - 1

            used_operators = []

            def get_edge(comparators, default):
                for operator, value in conditions.items():
                    if operator in comparators:
                        comparator = comparators[operator]
                        comparison_1 = None
                        comparison_2 = None

                        if comparator[0]:
                            comparison_1 = lambda a : self.indexed_comparison(a, value)
                        else:
                            comparison_1 = lambda a : self.indexed_comparison(value, a)
                        
                        if comparator[1]:
                            comparison_2 = lambda a : not comparison_1(a)
                        else:
                            comparison_2 = comparison_1

                        used_operators.append(operator)
                        return binary_search(lowest, highest, comparison_2, comparator[0])
                return default

            low_edge = get_edge({
                Operators.equal                 :   (True, False),
                Operators.greater_than          :   (False, False),
                Operators.greater_than_or_equal :   (True, True),
            }, lowest)

            high_edge = get_edge({
                Operators.equal                 :   (False, False),
                Operators.less_than             :   (True, False),
                Operators.less_than_or_equal    :   (False, True),
            }, highest)

            for operator in used_operators:
                if operator in conditions:
                    del conditions[operator]

            if(high_edge < low_edge or high_edge >= len(self.data) or low_edge < 0):
                error_message("invalid bounds, returning empty dataset")
                return []
            
            if low_edge == high_edge:
                return [self.data[low_edge]]

            return self.data[low_edge:high_edge]
        

        result_data = copy.deepcopy(self.data)

        if self.indexed_field in query_object.keys():
            result_data = double_binary_search(self.fields.index(self.indexed_field), query_object[self.indexed_field])

        deletions = []

        for i, row in enumerate(result_data):

            for field, operations in query_object.items():

                if not field in self.fields:
                    error_message("field '{0}' does not exist, skipping".format(field))
                    continue
                field_id = self.fields.index(field)

                for operator, value in operations.items():

                    def get_comparator(t, v):
                        if not Operators.comparison in operations:
                            error_message("comparison not specified for '{0}' filter, using default comparison".format(field))
                            query_object[field]["comparison"] = Comparisons.default # so the message doesn't appear again
                            return Comparisons.default(t, v)
                        comparator = operations[Operators.comparison]
                        if type(comparator) is not types.FunctionType:
                            error_message("comparison for '{0}' filter is not a function, using default comparison instead".format(field))
                            query_object[field]["comparison"] = Comparisons.default
                            return Comparisons.default(t, v)
                        return comparator(t, v)
                    
                    operator_functions = {
                        Operators.equal                 :   lambda t, v, c: t == v,
                        Operators.not_equal             :   lambda t, v, c: t != v,
                        Operators.less_than             :   lambda t, v, c: c(t, v),
                        Operators.greater_than          :   lambda t, v, c: c(v, t),
                        Operators.less_than_or_equal    :   lambda t, v, c: not c(v, t),
                        Operators.greater_than_or_equal :   lambda t, v, c: not c(t, v),
                        Operators.inside                :   lambda t, v, c: t in [str(x) for x in v],
                        Operators._not                  :   lambda t, v, c: not operator_functions[list(v)[0]](t, v[list(v)[0]], c),
                        Operators._and                  :   lambda t, v, c: not (False in [operator_functions[list(d)[0]](t, d[list(d)[0]], c) for d in v]),
                        Operators._or                   :   lambda t, v, c: True in [operator_functions[list(d)[0]](t, d[list(d)[0]], c) for d in v],
                    }

                    if operator == Operators.comparison:
                        continue
                    elif operator in operator_functions:
                        if not operator_functions[operator](row[field_id], value, get_comparator):
                            deletions.append(i)
                            break
                    else:
                        error_message("operator '{0}' does not exist, skipping".format(operator))

                if i in deletions:
                    break
        
        for i in reversed(range(len(deletions))):
            del result_data[deletions[i]]

        result = Dataset()
        result.data = result_data
        result.fields = self.fields
        return result

    def query_one(self, query_object=None):
        dataset = self.query(query_object)
        if len(dataset.data) == 0:
            return dataset
        else:
            dataset.data = [dataset.data[0]]
            return dataset

    def select(self, field_names=None):
        if field_names == None:
            field_names = self.fields

        field_ids = self.get_field_ids(field_names)

        selection = copy.deepcopy(self.data)

        for row in selection:
            for i in reversed(range(len(row))):
                if not i in field_ids:
                    row.pop(i)

        dataset = Dataset()
        dataset.fields = [self.fields[field_id] for field_id in field_ids]
        dataset.data = selection
        dataset.already_indexed(self.indexed_field, self.indexed_comparison)
        return dataset

    def select_as(self, field_names=None):
        if field_names == None:
            field_names = {}
        
        dataset = self.select(list(field_names)).rename_fields(field_names)

        if not dataset.indexed_field in dataset.fields:
            dataset.indexed_field = ""
            dataset.indexed_comparison = Comparisons.default

        return dataset

    def add_field(self, field, derivation=lambda r:""):
        for row in self.data:
            r = {f: row[self.fields.index(f)] for f in self.fields}
            row.append(str(derivation(r)))
        self.fields.append(field)
        return self

    def remove_fields(self, field_names):
        field_ids = self.get_field_ids(field_names)
        for x in reversed(range(len(field_ids))):
            i = field_ids[x]
            for row in self.data:
                del row[i]
            del self.fields[i]
        return self

    def rename_fields(self, field_names):
        for i, f in enumerate(self.fields):
            if f in field_names:
                if self.fields[i] == self.indexed_field:
                    self.indexed_field = field_names[f]
                self.fields[i] = field_names[f]
        return self

    def replace(self, field_names, function):
        field_ids = self.get_field_ids(field_names)

        for r, row in enumerate(self.data):
            for i in field_ids:
                row[i] = function(row[i])

        return self

    def replace_derived(self, field_names, function):
        field_ids = self.get_field_ids(field_names)

        for r, row in enumerate(self.data):
            for i in field_ids:
                row[i] = function(self.row_to_dict(row))

        return self

    def join(self, other_dataset, common_fields):
        if type(common_fields) is str:
            common_fields = [common_fields] * 2
        for field in other_dataset.fields:
            if field == common_fields[1]: continue

            def match(row):
                matched_row = other_dataset.query_one({
                    common_fields[1]: row[common_fields[0]]
                })
                if matched_row.count() > 0:
                    return matched_row.to_dictionary()[field]
                else:
                    return ""

            self.add_field(field, match)
        return self.remove_fields(common_fields[0])

    def to_dictionary(self):
        if len(self.data) > 1:
            error_message("this is not a single-row dataset, using first row")
        elif len(self.data) == 0:
            error_message("cannot convert dataset to dictionary, dataset is empty")
            return {}
        return self.row_to_dict(self.data[0])

    def to_list(self):
        if len(self.fields) > 1:
            error_message("this is not a single-field dataset, using first field")
        elif len(self.fields) == 0:
            error_message("cannot convert dataset to list, dataset is empty")
            return []
        array = []
        for row in self.data:
            array.append(row[0])
        return array

    def count(self, field_names=None):
        if field_names == None:
            return len(self.data)

        field_ids = self.get_field_ids(field_names)

        n = 0
        for row in self.data:
            null = False
            for i in field_ids:
                if row[i] == "":
                    null = True
                    break
            if not null:
                n += 1
        
        return n

    def sum(self, field_name=None):
        values = self.select(field_name).to_list()
        return sum([float(x) for x in values])

    def average(self, field_name=None):
        values = self.select(field_name).to_list()
        return sum([float(x) for x in values]) / len(values)

    def print_table(self, field_names=None):
        if field_names != None:
            self.select(field_names).print_table()
            return self

        column_widths = []
        for i, field in enumerate(self.fields):
            max_width = 0

            for row in self.data:
                width = len(row[i])
                if width > max_width:
                    max_width = width

            title_width = len(field)
            if(title_width > max_width):
                max_width = title_width
            
            column_widths.append(max_width)

        def print_bar(c="-"):
            print("+", end="")
            for i in range(len(self.fields)):
                print("".rjust(column_widths[i]+2, c), end="+")
            print()
        
        def print_row(row, title):
            if title:
                print_bar("=")
            print("|", end="")
            for i in range(len(self.fields)):
                adjusted = ""
                if title:
                    adjusted = row[i].center(column_widths[i])
                else:
                    adjusted = row[i].ljust(column_widths[i])
                print(" " + adjusted, end=" |")
            print()
            if title:
                print_bar("=")
            else:
                print_bar()
        
        print()
        print_row(self.fields, True)
        for row in self.data:
            print_row(row, False)
        print()

        return self

    def save_csv(self, filepath, delimiter=",", field_names=None):
        if field_names != None:
            self.select(field_names).save_csv(filepath, delimiter)
            return self
        
        csv_file = open(filepath, "w", newline='')
        csv_writer = csv.writer(csv_file, delimiter=delimiter)
        csv_writer.writerow(self.fields)
        csv_writer.writerows(self.data)
        csv_file.close()

        return self

def open_csv(filepath, delimiter=","):
    dataset = Dataset()
    csv_file = open(filepath, "r")
    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    for line, row in enumerate(csv_reader):
        if line == 0:
            dataset.fields = row
        else:
            dataset.data.append(row)
    csv_file.close()
    return dataset

def error_message(msg):
    print("[super_csv] ERROR: "+msg)