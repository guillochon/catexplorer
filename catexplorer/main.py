# myapp.py

import json
import numpy as np

from fuzzywuzzy import process

from bokeh.layouts import column, row
from bokeh.models import Button, Range1d
from bokeh.models.widgets import TextInput
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

# create a plot and style its properties
yr = Range1d(start=20, end=5)
p = figure(x_range=(49000, 50000), y_range=yr, toolbar_location=None)
p.outline_line_color = None
p.grid.grid_line_color = None

# add a button widget and configure with the call back
button = Button(label="Press Me")
namefield = TextInput(value="", title="Name(s):")
bandfield = TextInput(value="", title="Band(s):")

# add a text renderer to out plot (no data yet)
r = p.line(x=[], y=[], color="navy", line_width=3, line_join='round')

ds = r.data_source

with open('/root/astrocats/astrocats/supernovae/output/names.min.json') as f:
    names = json.loads(f.read())
names = list(names.keys())
unames = [x.upper() for x in names]

bands = ['U', 'B', 'V', 'R', 'I']
ubands = [x.upper() for x in bands]

# create a callback that will add a number in a random location
def callback():
    new = namefield.value
    finalname = ''
    if new:
        newname = new.upper()
        choices = []
        for ui, un in enumerate(unames):
            if un == newname:
                finalname = names[ui]
                break
            if newname in un:
                choices.append(names[ui])
        if not finalname:
            finalname = process.extractOne(new, choices)[0]
    if not finalname:
        finalname = 'SN1987A'
    namefield.value = finalname

    new = bandfield.value
    finalband = ''
    if new:
        newband = new.upper()
        choices = []
        for ui, un in enumerate(ubands):
            if un == newband:
                finalband = bands[ui]
                break
            if newband in un:
                choices.append(bands[ui])
        if not finalband:
            finalband = process.extractOne(new, choices)[0]
    if not finalband:
        finalband = 'V'
    bandfield.value = finalband

    with open('/root/astrocats/astrocats/supernovae/output/json/' +
              finalname.replace('/', '_') + '.json') as f:
        event = json.loads(f.read())
    event = event[list(event.keys())[0]]
    new_data = {}
    new_data['x'] = []
    new_data['y'] = []
    for photo in event['photometry']:
        if photo.get('band', '') != finalband:
            continue
        new_data['x'].append(float(photo['time']))
        new_data['y'].append(float(photo['magnitude']))
    x_buf = 0.1*(max(new_data['x']) - min(new_data['x']))
    y_buf = 0.1*(max(new_data['y']) - min(new_data['y']))
    p.x_range.start = min(new_data['x']) - x_buf
    p.x_range.end = max(new_data['x']) + x_buf
    p.y_range.start = max(new_data['y']) + y_buf
    p.y_range.end = min(new_data['y']) - y_buf
    ds.data = new_data

def bandcb(attrname, old, new):
    callback()

def namecb(attrname, old, new):
    callback()

namefield.on_change('value', namecb)
bandfield.on_change('value', bandcb)
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(p, row(namefield, bandfield)))
