import sys
import math
import types
import csv

class Operators:
    equal = "eq"
    not_equal = "neq"
    less_than = "lt"
    greater_than = "gt"
    less_than_or_equal = "lte"
    greater_than_or_equal = "gte"

    comparison = "comparison"

class Comparisons:
    integers = lambda a, b: int(a) < int(b)
    floats = lambda a, b: float(a) < float(b)
    strings = lambda a, b: a < b

    @staticmethod
    def get_date_comparison(format_string):
        def compare_dates(format_string, a, b):
            
            #
            # TODO
            # 
            # based on format_string, return True if a is earlier than b
            #
            # format_string examples:
            # "YYYY-MM-DD"
            # "MM/DD/YY"
            # "YYYYYY::MM::DD::hh::mm::ss"
            # 

            return a < b
        return lambda a, b: compare_dates(format_string, a, b)


    default = floats

class Dataset:
    def __init__(self):
        self.data = []
        self.column_names = []
        self.indexed_column = ""
        self.indexed_comparison = Comparisons.default
    
    def index(self, column_name, comparison = Comparisons.default):
        if not column_name in self.column_names:
            error_message("column '{0}' does not exist, skipping index".format(column_name))
            return self

        def quick_sort(column, low, high, comparison): 
            if low < high: 
                p = partition(column, low, high, comparison)
        
                quick_sort(column, low, p-1, comparison)
                quick_sort(column, p+1, high, comparison)
        
        def partition(column, low, high, comparison):
            i = low-1
            pivot = self.data[high][column]
        
            for j in range(low, high):
                if comparison(self.data[j][column], pivot):
                    i = i+1
                    self.data[i], self.data[j] = self.data[j], self.data[i]
            
            self.data[i+1], self.data[high] = self.data[high], self.data[i+1]

            return i+1
        
        if type(comparison) is not types.FunctionType:
            error_message("indexing comparison is not a function, using default comparison instead")
            comparison = Comparisons.default
        
        sys.setrecursionlimit(10000)
        quick_sort(self.column_names.index(column_name), 0, len(self.data)-1, comparison)
        self.indexed_column = column_name
        self.indexed_comparison = comparison
        
        return self
    
    def query(self, query_object=None):

        if query_object == None:
            return self
        
        if type(query_object) is not dict:
            return Dataset()
        
        for column_name, operators in query_object.items():
            if type(operators) is not dict:
                query_object[column_name] = {Operators.equal: operators}

        def binary_search(key, conditions):

            def binary_edge_search(low, high, comparison, direction):
                if low + 1 == high:
                    return high
                lower_middle_index = math.floor((high+low)/2)
                upper_middle_index = math.ceil((high+low)/2)
                median = self.data[upper_middle_index][key]
                if comparison(median) == direction:
                    return binary_edge_search(lower_middle_index, high, comparison, direction)
                else:
                    return binary_edge_search(low, upper_middle_index, comparison, direction)

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

                        return_val = binary_edge_search(lowest, highest, comparison_2, comparator[0])
                        used_operators.append(operator)
                        return return_val
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

            return self.data[low_edge:high_edge]
        

        result_data = self.data

        if self.indexed_column in query_object.keys():
            result_data = binary_search(self.column_names.index(self.indexed_column), query_object[self.indexed_column])

        deletions = []

        for i, row in enumerate(result_data):

            for column_name, operations in query_object.items():

                if not column_name in self.column_names:
                    error_message("column '{0}' does not exist, skipping".format(column_name))
                    continue
                column_id = self.column_names.index(column_name)

                for operator, value in operations.items():

                    def get_comparator():
                        if not Operators.comparison in operations:
                            error_message("comparison not specified for '{0}' filter, using default comparison".format(column_name))
                            query_object[column_name]["comparison"] = Comparisons.default # so the message doesn't appear again
                            return Comparisons.default
                        comparator = operations[Operators.comparison]
                        if type(comparator) is not types.FunctionType:
                            error_message("comparison for '{0}' filter is not a function, using default comparison instead".format(column_name))
                            query_object[column_name]["comparison"] = Comparisons.default
                            return Comparisons.default
                        return comparator

                    comparators = {
                        Operators.equal                 :   lambda t, v: t == v,
                        Operators.not_equal             :   lambda t, v: t != v,
                        Operators.less_than             :   lambda t, v: get_comparator()(t, v),
                        Operators.greater_than          :   lambda t, v: get_comparator()(v, t),
                        Operators.less_than_or_equal    :   lambda t, v: not get_comparator()(v, t),
                        Operators.greater_than_or_equal :   lambda t, v: not get_comparator()(t, v),
                    }

                    if operator == Operators.comparison:
                        continue
                    elif operator in comparators:
                        if not comparators[operator](row[column_id], value):
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
        result.column_names = self.column_names
        return result
    
    def print_data(self, columns=None):
        if columns == None:
            columns = self.column_names
        
        column_ids = []
        for column_name in columns:
            if not column_name in self.column_names:
                error_message("column '{0}' does not exist, skipping".format(column_name))
                continue
            column_ids.append(self.column_names.index(column_name))
        
        column_widths = {}
        for i in column_ids:
            max_width = 0

            for row in self.data:
                width = len(row[i])
                if width > max_width:
                    max_width = width

            title_width = len(self.column_names[i])
            if(title_width > max_width):
                max_width = title_width
            
            column_widths[i] = max_width

        def print_bar(c="-"):
            print("+", end="")
            for i in column_ids:
                print("".rjust(column_widths[i]+2, c), end="+")
            print()
        
        def print_row(row, title):
            if title:
                print_bar("=")
            print("|", end="")
            for i in column_ids:
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
        print_row(self.column_names, True)
        for row in self.data:
            print_row(row, False)
        print()
    
    def save_csv(self, filepath, delimiter=",", columns=None):
        if columns == None:
            columns = self.column_names
        
        column_ids = []
        for column_name in columns:
            if not column_name in self.column_names:
                error_message("column '{0}' does not exist, skipping".format(column_name))
                continue
            column_ids.append(self.column_names.index(column_name))
        
        csv_file = open(filepath, "w")
        print(delimiter.join(columns), file=csv_file)
        for row in self.data:
            for i in column_ids:
                if i == column_ids[-1]:
                    print(row[i], file=csv_file)
                else:
                    print(row[i], file=csv_file, end=delimiter)
        csv_file.close()


def open_csv(filepath, delimiter=","):
    dataset = Dataset()
    csv_file = open(filepath, "r")
    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    for line, row in enumerate(csv_reader):
        if line == 0:
            dataset.column_names = row
        else:
            dataset.data.append(row)
    csv_file.close()
    return dataset

def error_message(msg):
    print("[super_csv] ERROR: "+msg)