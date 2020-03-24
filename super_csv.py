import sys
import math

class Dataset:
    def __init__(self):
        self.data = []
        self.column_names = []
        self.indexed_column = ""
        self.indexed_comparison = lambda a, b: float(a) < float(b)
    
    def index(self, column_name, comparison = lambda a, b: float(a) < float(b)):
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
        
        sys.setrecursionlimit(10000)
        quick_sort(self.column_names.index(column_name), 0, len(self.data)-1, comparison)
        self.indexed_column = column_name
        self.indexed_comparison = comparison
    
    def query(self, query_object):

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

            low_edge = lowest
            high_edge = highest
            if "eq" in conditions.keys():
                low_edge = binary_edge_search(lowest, highest, lambda a : self.indexed_comparison(a, conditions["eq"]), True)
                high_edge = binary_edge_search(lowest, highest, lambda a : self.indexed_comparison(conditions["eq"], a), False)
            else:
                if "gt" in conditions.keys():
                    low_edge = binary_edge_search(lowest, highest, lambda a : self.indexed_comparison(conditions["gt"], a), False)
                if "lt" in conditions.keys():
                    high_edge = binary_edge_search(lowest, highest, lambda a : self.indexed_comparison(a, conditions["lt"]), True)
            
            if(high_edge < low_edge):
                error_message("invalid bounds")
                return []

            return self.data[low_edge:high_edge]
        

        result_data = self.data

        if self.indexed_column in query_object:
            result_data = binary_search(self.column_names.index(self.indexed_column), query_object[self.indexed_column])
            del query_object[self.indexed_column]
        
        deletions = []
        for i, row in enumerate(result_data):
            for column_name, operations in query_object.items():
                column_id = self.column_names.index(column_name)
                for operator, value in operations.items():
                    if operator == "comparison":
                        continue
                    elif operator == "eq":
                        if not row[column_id] == value:
                            deletions.append(i)
                            break
                    elif operator == "lt":
                        if not operations["comparison"](row[column_id], value):
                            deletions.append(i)
                            break
                    elif operator == "gt":
                        if not operations["comparison"](value, row[column_id]):
                            deletions.append(i)
                            break
                if i in deletions:
                    break
        
        for i in range(len(deletions)-1, -1, -1):
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


def open_csv(filepath, delimiter=","):
    dataset = Dataset()
    csv_file = open(filepath, "r")
    for num, line in enumerate(csv_file):
        if line == "":
            continue
        row = line.strip().split(delimiter)
        if num == 0:
            dataset.column_names = row
        else:
            dataset.data.append(row)
    return dataset

def error_message(msg):
    print("[super_csv] ERROR: "+msg)