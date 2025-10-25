import pandas as pd
from tkinter import *

#needs: need a way for gui to access all csv's and figure out which csvs correspond to which data according to sap.
#Each CSV file given is information regarding a certain button or category on the sample GUI png.

#instantiate an instance of a window; main loop displays it on screen
window = Tk()
window.mainloop()

#simple csv reader, will display first five layers of csv
dataFrame = pd.read_csv("CSV Files/CDHDR.csv")
print(dataFrame.head())
