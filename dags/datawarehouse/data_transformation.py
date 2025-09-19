#We will be checking the lenght of the video to assume if it is a short or not since API does not have an option

from datetime import timedelta,datetime

#break apart string to extract values we want
def parse_duration(duration_str):
    
    duration_str = duration_str.replace('P',"").replace('T',"") #P string will be there but T might not be there, will still work
    #example
    #D1H12M13S54
    
    components = ["D","H","M","S"]
    values = {"D":0,"H":0,"M":0,"S":0}
    
    for component in components:
        if component in duration_str:
           value,duration_str = duration_str.split(component) #"1H12M13S".split("H")  # => ["1", "12M13S"]
           values[component] = int(value)
           
    total_duration = timedelta(
        days = values["D"],
        hours=values["H"],
        minutes=values["M"],
        seconds=values['S']
    )
    
    return total_duration


def transform_data(row):

    duration_td = parse_duration(row["Duration"])

    row["Duration"] = (datetime.min + duration_td).time()

    row["Video_Type"] = "Shorts" if duration_td.total_seconds() <= 60 else "Normal"

    return row