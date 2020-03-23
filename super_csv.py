class Dataset:
    def __init__(self):
        self.data = []

    def top_row(self, row):
        self.column_names = row
    
    def add_row(self, row):
        self.data.append(row)
    
    def index(self, column_name, comparison=(lambda a, b: float(a) < float(b))):
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
        
        quick_sort(self.column_names.index(column_name), 0, len(self.data)-1, comparison)

    def query_one(self, query_object):
        return []
    
    def query_all(self, query_object):
        return []
    
    def delete_one(self, query_object):
        return
    
    def delete_all(self, query_object):
        return
    
    def print_data(self):
        for row in self.data:
            print(row)


def open_csv(filepath, delimiter=","):
    csv_file = open(filepath, "r")
    dataset = Dataset()
    for num, line in enumerate(csv_file):
        if line == "":
            continue
        fields = line.strip().split(delimiter)
        if num == 0:
            dataset.top_row(fields)
        else:
            dataset.add_row(fields)
    return dataset

dataset = open_csv("example_data/coronavirus_data.csv")
#dataset.index("location", lambda a, b: a < b)
#dataset.index("date", lambda a, b: a < b)
dataset.index("total_cases")
#dataset.print_data()