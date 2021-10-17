import tkinter as tk
from tkinter import *
import os
from PIL import Image, ImageTk
import sys

class Redirect():
    
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert('end', text)

def run_script():
	script = os.system('python active_brownian.py')

root = tk.Tk()

canvas = tk.Canvas(root, height=500, width=800)
canvas.grid(columnspan=10, rowspan=10)

#logo
logo = Image.open('logo.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image = logo)
logo_label.image = logo
logo_label.grid(columnspan=2, column=1, row=0)

#instructions
instructions = tk.Label(root, text="Variable and Flexible Diffusion and Advection Simulation Tool. Change the Variables and Settings before running.")
instructions.grid(columnspan=10, column=0, row=1)

#input boxes
timeVar = tk.Label(root, text="Max Time (s)")
timeVar.grid(column=0, row=3)
timeInput = tk.Entry(root)
timeInput.grid(column=1, row=3)

timeStep = tk.Label(root, text="Time Step/ dT (s)")
timeStep.grid(column=2, row=3)
timeStepInput = tk.Entry(root)
timeStepInput.grid(column=3, row=3)

numParticle = tk.Label(root, text="Number of Particles")
numParticle.grid(column=0, row=4)
numInput = tk.Entry(root)
numInput.grid(column=1, row=4)

diff = tk.Label(root, text="Diffusivity")
diff.grid(column=2, row=4)
diffInput = tk.Entry(root)
diffInput.grid(column=3, row=4)

numParticle = tk.Label(root, text="Velocity Field(Place File into Folder)")
numParticle.grid(column=0, row=5)
numInput = tk.Entry(root)
numInput.grid(column=1, row=5)

diff = tk.Label(root, text="Simulation Type: 1D/ 2D/ Live")
diff.grid(column=2, row=5)
diffInput = tk.Entry(root)
diffInput.grid(column=3, row=5)


#buttons
runScript = tk.Button(root, text="Run Simulation", padx=10, pady=10, fg="black", bg="pink", command=run_script)
runScript.grid(columnspan=2, column=1, row=6, sticky = tk.W+tk.E)

text = tk.Text(root)
text.grid(columnspan=2, column=1, row=7, sticky = tk.W+tk.E)

old_stdout = sys.stdout    
sys.stdout = Redirect(text)

root.mainloop()