import sys, math, types, csv, copy
from datetime import datetime


class Operators:
    equal = "eq"
    not_equal = "neq"
    less_than = "lt"
    greater_than = "gt"
    less_than_or_equal = "lte"
    greater_than_or_equal = "gte"
    inside = "in"

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
    def __init__(self):
        self.data = []
        self.fields = []
        self.indexed_field = ""
        self.indexed_comparison = Comparisons.default
    
    def already_indexed(self, field, comparison = Comparisons.default):
        self.indexed_field = field
        self.indexed_comparison = comparison
        return self
    
    def index(self, field, comparison = Comparisons.default):
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

            def double_binary_search_edge(low, high, comparison, direction):
                if low + 1 == high:
                    return high
                lower_middle_index = math.floor((high+low)/2)
                upper_middle_index = math.ceil((high+low)/2)
                median = self.data[upper_middle_index][key]
                if comparison(median) == direction:
                    return double_binary_search_edge(lower_middle_index, high, comparison, direction)
                else:
                    return double_binary_search_edge(low, upper_middle_index, comparison, direction)

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
                        return double_binary_search_edge(lowest, highest, comparison_2, comparator[0])
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

                    def get_comparator():
                        if not Operators.comparison in operations:
                            error_message("comparison not specified for '{0}' filter, using default comparison".format(field))
                            query_object[field]["comparison"] = Comparisons.default # so the message doesn't appear again
                            return Comparisons.default
                        comparator = operations[Operators.comparison]
                        if type(comparator) is not types.FunctionType:
                            error_message("comparison for '{0}' filter is not a function, using default comparison instead".format(field))
                            query_object[field]["comparison"] = Comparisons.default
                            return Comparisons.default
                        return comparator

                    comparators = {
                        Operators.equal                 :   lambda t, v: t == v,
                        Operators.not_equal             :   lambda t, v: t != v,
                        Operators.less_than             :   lambda t, v: get_comparator()(t, v),
                        Operators.greater_than          :   lambda t, v: get_comparator()(v, t),
                        Operators.less_than_or_equal    :   lambda t, v: not get_comparator()(v, t),
                        Operators.greater_than_or_equal :   lambda t, v: not get_comparator()(t, v),
                        Operators.inside                :   lambda t, v: t in [str(x) for x in v],
                    }

                    if operator == Operators.comparison:
                        continue
                    elif operator in comparators:
                        if not comparators[operator](row[field_id], value):
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

        if type(field_names) is str:
            field_names = [field_names]
        
        field_ids = []
        for field in field_names:
            if not field in self.fields:
                error_message("field '{0}' does not exist, skipping".format(field))
                field_names.remove(field)
                continue
            field_ids.append(self.fields.index(field))
        field_ids.sort()

        selection = copy.deepcopy(self.data)

        for row in selection:
            for i in reversed(range(len(row))):
                if not i in field_ids:
                    row.pop(i)

        dataset = Dataset()
        dataset.fields = [self.fields[field_id] for field_id in field_ids]
        dataset.data = selection
        return dataset

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

    def to_dictionary(self):
        if len(self.data) > 1:
            error_message("this is not a single-row dataset, using first row")
        elif len(self.data) == 0:
            error_message("cannot convert dataset to dictionary, dataset is empty")
            return {}
        row = self.data[0]
        return {field: row[i] for i, field in enumerate(self.fields)}
    
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