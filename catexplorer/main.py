# myapp.py

import json
import os
import copy
import numpy as np
import importlib.util

from fuzzywuzzy import process

from bokeh.layouts import column, row
from bokeh.models import Button, Range1d, ColumnDataSource
from bokeh.models.widgets import TextInput
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

# Because Bokeh server doesn't allow relative imports
spec = importlib.util.spec_from_file_location("plotting", os.path.dirname(os.path.abspath(__file__)) + '/../../../utils/plotting.py')
plotting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plotting)

# create a plot and style its properties
tools = "pan,wheel_zoom,box_zoom,save,crosshair,reset,resize"
p = figure(title='Photometry Explorer', active_drag='box_zoom', y_range=Range1d(start=1, end=0),
           y_axis_label='Apparent Magnitude', tools=tools, plot_width=485, plot_height=485,
           toolbar_location='above', toolbar_sticky=False, x_range=Range1d(start=0, end=1))
p.xaxis.axis_label_text_font = 'futura'
p.yaxis.axis_label_text_font = 'futura'
p.xaxis.major_label_text_font = 'futura'
p.yaxis.major_label_text_font = 'futura'
p.xaxis.axis_label_text_font_size = '11pt'
p.yaxis.axis_label_text_font_size = '11pt'
p.xaxis.major_label_text_font_size = '8pt'
p.yaxis.major_label_text_font_size = '8pt'
p.title.align = 'center'
p.title.text_font_size = '16pt'
p.title.text_font = 'futura'

mlobs = p.multi_line(xs='xs', ys='ys', line_color='colors', line_width='lws', line_join='round',
    source=ColumnDataSource(data=
        {
            'xs':[[]],
            'ys':[[]],
            'colors':['white'],
            'lws':[2]
        }
    ))

circobs = p.circle(x='xs', y='ys', color='colors',
    source=ColumnDataSource(data=
        {
            'xs':[[]],
            'ys':[[]],
            'colors':['white'],
        }
    ))

# add a button widget and configure with the call back
button = Button(label="Fetch Data")
namefield = TextInput(value="", title="Name(s):")
bandfield = TextInput(value="", title="Band(s):")

# add a text renderer to out plot (no data yet)

with open('/root/astrocats/astrocats/supernovae/output/names.min.json') as f:
    names = json.loads(f.read())
names = list(names.keys())
unames = [x.upper() for x in names]

bands = ['U', 'B', 'V', 'R', 'I']
ubands = [x.upper() for x in bands]

nds = []

def callback():
    nds = []
    new = namefield.value
    newnames = []
    for name in [x.strip() for x in new.split(',')]:
        finalname = ''
        if name:
            newname = name.upper()
            choices = []
            for ui, un in enumerate(unames):
                if un == newname:
                    finalname = names[ui]
                    break
                if newname in un:
                    choices.append(names[ui])
            if not finalname:
                finalname = process.extractOne(name, choices)[0]
        if not finalname:
            finalname = 'SN1987A'
        newnames.append(finalname)
    namefield.value = ', '.join(newnames)

    new = bandfield.value
    newbands = []
    for band in [x.strip() for x in new.split(',')]:
        finalband = ''
        if band:
            newband = band.upper()
            choices = []
            for ui, un in enumerate(ubands):
                if un == newband:
                    finalband = bands[ui]
                    break
                if newband in un:
                    choices.append(bands[ui])
            if not finalband:
                finalband = process.extractOne(band, choices)[0]
        if not finalband:
            finalband = 'V'
        newbands.append(finalband)
    bandfield.value = ', '.join(newbands)

    for name in newnames:
        with open('/root/astrocats/astrocats/supernovae/output/json/' +
                  name.replace('/', '_') + '.json') as f:
            event = json.loads(f.read())
        event = event[list(event.keys())[0]]

        for band in newbands:
            new_data = {}
            new_data['x'] = []
            new_data['y'] = []
            new_data['band'] = band
            for photo in event['photometry']:
                if photo.get('band', '') != band:
                    continue
                new_data['x'].append(float(photo['time']))
                new_data['y'].append(float(photo['magnitude']))
            nds.append(copy.deepcopy(new_data))

    if len(newnames) > 1:
        maxmjd = []
        for nd in nds:
            if not len(nd['x']):
                continue
            maxmjd.append(nd['x'][nd['y'].index(min(nd['y']))])
        for ndi, nd in enumerate(nds):
            if not len(nd['x']):
                continue
            nds[ndi]['x'] = [x - maxmjd[ndi] for x in nd['x']]

    nxs = []
    nys = []
    for nd in nds:
        nxs.extend(nd['x'])
        nys.extend(nd['y'])
    x_buf = 0.1*(max(nxs) - min(nxs))
    y_buf = 0.1*(max(nys) - min(nys))

    p.x_range.start = min(nxs) - x_buf
    p.x_range.end = max(nxs) + x_buf
    p.y_range.start = max(nys) + y_buf
    p.y_range.end = min(nys) - y_buf

    mld = {}
    mldf = {}
    for nd in nds:
        mld.setdefault('xs',[]).append(nd['x'])
        mld.setdefault('ys',[]).append(nd['y'])
        mld.setdefault('colors',[]).append(plotting.bandcolorf(nd['band']))
        mld.setdefault('lws',[]).append(2)

        mldf.setdefault('xs',[]).extend(nd['x'])
        mldf.setdefault('ys',[]).extend(nd['y'])
        mldf.setdefault('colors',[]).extend([plotting.bandcolorf(nd['band']) for x in range(len(nd['x']))])
        
    mlobs.data_source.data = mld
    circobs.data_source.data = mldf

def bandcb(attrname, old, new):
    callback()

def namecb(attrname, old, new):
    callback()

namefield.on_change('value', namecb)
bandfield.on_change('value', bandcb)
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(p, row(namefield, bandfield), button))
