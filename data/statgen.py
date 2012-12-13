import fileinput
from collections import Counter
import simplejson
import re
from sets import Set
import csv
from math import floor
import ast


def match(expr, evt):
    #for now assume single tuples        
    for i, sub_expr in enumerate(expr):
        if sub_expr == "*": continue
#        if (re.match("^"+sub_expr+"$", evt[i])) is None:
        elif sub_expr != evt[i]:
            return False
    return True 

def filter_by_expr(filter, filename):
    lines = open(filename)
    return (line for line in lines if match(filter, simplejson.loads(line.strip())[1]))

def filter_users_by_expr(user_filter, filename):
    lines = open(filename)
    filtered_users = []
    filtered_lines = list((line for line in lines if match(user_filter, simplejson.loads(line.strip())[1])))
    for l in filtered_lines:
        person,evt,timestr = simplejson.loads(l.strip())
        filtered_users.append(person)
    filtered_users = Set(filtered_users)
    return filtered_users
    
def summary(counts):
    if len(counts) == 0:
        return 0,0,0
    n = sum(counts.values())
    p = len(counts)
    mean = n / float(p) if p> 0 else 0
    indices = [int(floor(k * p)) for k in (.05,.25,.50,.75,.95)]
    reexpanded = sorted(counts.itervalues())
    qs = [reexpanded[i] for i in indices]

    return n,mean,qs

class StatGenerator:
    stats = ["percent", "summary"]
    
    def __init__(self, fn, expr, filter = None, user_filter=None):
        self.filename = fn
        self.lines = open(fn)
        self.expr = expr
        self.filter = filter
        self.filtered_lines = None 
        self.user_filter = user_filter 
        self.filtered_users = None 
        
        
    def faststat(self, with_filter=False, with_user_filter=False):        
        #raise exception if filters not there
        lines = self.lines
                        
        if (with_filter): 
            if not (self.filtered_lines):
                self.filtered_lines = filter_by_expr(self.filter, self.filename)
            lines = self.filtered_lines
        if (with_user_filter):
            if not (self.filtered_users):
                self.filtered_users = filter_users_by_expr(self.user_filter, self.filename)

        n = 0
        allids = set()
        C = Counter()
        for line in lines:
            n+=1
            person,evt,timestr = simplejson.loads(line.strip())
            evt = evt[:3]
            if (with_user_filter) and person not in self.filtered_users:
                continue 
            allids.add(person)
            if match(self.expr, evt):
                C[person] += 1
        summary(C)
        return {"percent":round(100*float(len(C))/len(allids),1), "summary": summary(C)}
        
    def all_events_of_type(self, filter):
        return filter_By_expr(filter, self.filename)
    
    def all_users_with_condition(self, user_filter):
        filter_users_by_expr(self.user_filter, self.filename)
    
def make_stat_table(datafile_name):
    #stats_by_tag = get_all_file_stats(expr_file_reader, datafile_name)
    all_stats = get_all_stats(datafile_name)
    print "<table border='1'>"
    print "<tr><th>Tag Name</th>"
    for stat in StatGenerator.stats:
        print "<th>",stat,"</th>"
    print "</tr>"
    for tag in all_stats:
        print "<tr><td>", tag, "</td>"
        for stat in StatGenerator.stats:
            print "<td>", all_stats[tag][stat], "</td>"
        print "</tr>"
    print "</table>"

#def get_all_file_stats(expr_file_reader, datafile_name):    
#    stats_by_tag = {}
#    for tup in expr_file_reader:
#        tag,expr = tup
#        expr = expr[1:-1].split(',')
#        sg = StatGenerator(datafile_name, expr)
#        stats_by_tag[tag] = sg.faststat()
#    return stats_by_tag

def get_all_stats(datafile_name):
    stats_by_expr = {}
    unique_expressions = (tuple(line.strip().split(',')) for line in sys.stdin)
    first_keyword_expressions = ()
    for expr in unique_expressions:
        sg = StatGenerator(datafile_name, expr)
        stats_by_expr[expr] = sg.faststat()
    return stats_by_expr
        
if __name__ == "__main__":
    import sys, getopt

    filter = None
    user_filter = None
    expression_file = None
    datafile_name = None
    expr = None
    all_flag = False

    opt, args = getopt.getopt(sys.argv[1:], "f:u:e:d:x:",["all"])
    
    for o, a in opt:     
        if o == "--all":
           all_flag = True
        elif o == "-e":
            expression_file = a
        elif o == "-f":
            filter = tuple(a[1:-1].split(','))
        elif o == "-u":
            user_filter = tuple(a[1:-1].split(','))
        elif o == "-d":
            datafile_name = a
        elif o == "-x":
            expr = tuple(a[1:-1].split(','))

    if all_flag:
         make_stat_table(datafile_name)
    else:
        sg = StatGenerator(datafile_name, expr, filter=filter, user_filter=user_filter)
        print sg.faststat()
        
    ###
    #x = expression
    #d = datafile name
    #f = filter (only consider this set of events)
    #u = user fileter (only consider users who have at least one of the following type of event)
    
    #example usage: python statgen.py -x "[urlbar,*,*]" -d events.txt -f [*,*,*] -u "[searchbar,*,*]"
    
    
    
    #cut -d[ -f3-4 events.txt| cut -d] -f1| cut -d, -f1-3 | tr -d '"' | sed 's/, /,/g' | sort | uniq

    
    
    