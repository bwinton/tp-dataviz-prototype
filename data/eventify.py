import simplejson
import fileinput
import time



def tryparse(contents):
    try:
        return simplejson.loads(contents)
    except:
        return None
    
def parse_input_file(fh):
    clean_fh = filter(lambda x: x != "\n", fh)
    return filter(None, (tryparse(l.strip().split('\t')[1]) for l in clean_fh))
    
def map_person_events(in_events):    
    in_events = list(in_events)
    for (ii, event) in enumerate(in_events):
        t, area, sub1, sub2, ts = event
        
        if t == 3: continue
        if t == 0: continue
        
        yield area,sub1,sub2,ts        

def main(fh):
    people = parse_input_file(fh)
    events = (x["events"] for x in people)
    mapped_events = (map_person_events(x) for x in events)
    for (ii,gen) in enumerate(mapped_events):
        for x in gen:
            print simplejson.dumps([ii,x,time.ctime(float(x[-1]/1000)).strip()])



if __name__ == "__main__":
    main(fileinput.input())
