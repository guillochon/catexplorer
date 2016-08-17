# myapp.py

from bokeh.layouts import column, row
from bokeh.models import Button, Range1d
from bokeh.models.widgets import TextInput
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

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
p.line(x=[], y=[], color="navy", line_width=3, line_join='round')

# add a button widget and configure with the call back
button = Button(label="Press Me")
namefield = TextInput(value="", title="Name(s):")
bandfield = TextInput(value="", title="Band(s):")

# add a text renderer to out plot (no data yet)

lineobs = []
circobs = []
new_datas = []
nds = []

def callback():
    new_datas = [{'x':[0.0, 1.0],'y':[0.0, 1.0]}]
    nxs = []
    nys = []
    for nd in new_datas:
        nxs.extend(nd['x'])
        nys.extend(nd['y'])
    x_buf = 0.1*(max(nxs) - min(nxs))
    y_buf = 0.1*(max(nys) - min(nys))

    p.x_range.start = min(nxs) - x_buf
    p.x_range.end = max(nxs) + x_buf
    p.y_range.start = max(nys) + y_buf
    p.y_range.end = min(nys) - y_buf

    for nd in new_datas:
        nds.append(nd)

        lineobs.append(p.line(x=[], y=[], color="navy", line_width=3, line_join='round'))
        circobs.append(p.circle(x=[], y=[], color="navy", line_width=3, line_join='round'))

        lineobs[-1].data_source.data = nds[-1]
        circobs[-1].data_source.data = nds[-1]

button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(p, row(namefield, bandfield), button))

