from tkinter import *
from tkinter import filedialog,messagebox
from PIL import ImageTk,Image
from csv import DictWriter
import io,os

root = Tk()
root.title("Image Editor")
root.geometry("500x700")
root.iconbitmap("icon.ico")

global current,i_path,o_path,images,statusBar,canvas,color
i_path = ""
o_path = ""
current = 0

start_x = start_y = 0
rect_id = None
color = "Red"

def show_image(index):
    canvas.delete("all")
    canvas.image = images[index]  
    canvas.create_image(0, 0, image=canvas.image, anchor=NW)

def forward(e=None):
    global current
    
    if current < len(images)-1:
        current += 1
        show_image(current)
        statusBar.config(text=f"Image {current+1} of {len(images)}")

    if current == len(images)-1:
        forwardBtn.config(state=DISABLED)
    else:
        backwardsBtn.config(state=NORMAL)
    
    if current > 0:
        backwardsBtn.config(state=NORMAL)

def backward(e=None):
    global current
    
    if current > 0:
        current-=1
        show_image(current)
        statusBar.config(text=f"Image {current+1} of {len(images)}")

    if current <=  0:
        backwardsBtn.config(state=DISABLED)
    else:
        backwardsBtn.config(state=NORMAL)
    
    if current <= len(images)-1:
        forwardBtn.config(state=NORMAL)

def save(e=None):
    global rect_id,current,o_path,color
    
    if not images:
        return

    if rect_id is not None:
        c = canvas.coords(rect_id)
        print(c)
        cords_dict = {
                "x1":c[0],
                "y1":c[1],
                "x2":c[2],
                "y2":c[3],
                "color":color,
                "output":f"image{current+1}.png"
            }
        
        field_names = ["x1","y1","x2","y2","color","output"]
        
        with open(f"{o_path}\\data.csv","a",newline="\n") as file:
            writer = DictWriter(file, fieldnames=field_names)
            writer.writerow(cords_dict)

        show_image(current)
        ps = canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))

        if o_path:
            img.save(f"{o_path}\\image{current+1}.png")
        
        messagebox.showinfo("Saved!","Your rectangle's co-ordinates have been saved in data.csv located in the output folder.")
    else:
        messagebox.showerror("No Rectangle!","No rectangle has been drawn on the image. Kindly draw a rectangle and then click SAVE.")
        
def mouse_press(event):
    print("HI")
    global start_x, start_y, rect_id
    if switch_var.get() == "On":
        global color
        start_x, start_y = event.x, event.y
        rect_id = canvas.create_rectangle(start_x,start_y,start_x,start_y,outline=color.lower(),width=2)

def mouse_drag(event):
    print("YO")
    global rect_id
    if switch_var.get() == "On":
        canvas.coords(rect_id,start_x,start_y,event.x,event.y)

def switch_cmd(e):
    if not (switch_var.get() == "On" or switch_var.get() == "Off"):
        messagebox.showerror("No Option Selected","No option was selected. Please select on or off.")

def clear():
    global current
    if images:
        show_image(current)

def io_folder_sel(io_selec):
    global i_path,o_path,inputLabel,outputLabel,top

    path = filedialog.askdirectory()
    if path: 
        msg = "Folder Selected"

        if io_selec == "i": 
            i_path = path
            inputLabel.config(text=msg)
        if io_selec == "o": 
            o_path = path
            outputLabel.config(text=msg)
    
    try:
        if i_path and o_path:
            top.destroy()
            root.deiconify()
            root.focus_set()
            load_images()
            
    except: pass

def open_new_window():
    global inputLabel,outputLabel,top
    top = Toplevel(root) 
    top.title("Input Output Folder Choice")
    top.geometry("250x150")  

    inputLabel = Label(top,text="Select Input Folder")
    inputLabel.grid(row=1,column=0,pady=(25,10),padx=15)

    inputBtn = Button(top,text="Select",command=lambda: io_folder_sel("i"))
    inputBtn.grid(row=1,column=1,padx=15)

    outputLabel = Label(top,text="Select Output Folder")
    outputLabel.grid(row=2,column=0,pady=10,padx=15)

    outputBtn = Button(top,text="Select",command=lambda: io_folder_sel("o"))
    outputBtn.grid(row=2,column=1,padx=15)

def load_images(i=1):
    global images,statusBar,canvas,current,i_path,statusBar

    if i==1:
        images = []

    path = os.path.join(i_path,f"image{i}.png")
    if os.path.exists(path):
        img = Image.open(path)
        img = img.resize((500,500))
        images.append(ImageTk.PhotoImage(img))
        root.after(10, lambda: load_images(i+1)) 
    else:
        if images:
            statusBar = Label(root,text=f"Image 1 of {len(images)}",bd=1,anchor=E)
            statusBar.grid(row=2,column=0,columnspan=3,sticky=W+E,padx=10)

            canvas = Canvas(root, width=images[current].width(), height=images[current].height())
            canvas.create_image(0, 0, image=images[current],anchor=NW)
            canvas.grid(row=0,column=0,columnspan=3)
                        
            canvas.bind("<ButtonPress-1>",mouse_press)
            canvas.bind("<B1-Motion>",mouse_drag)

def color_cmd(e=None):
    global color
    color = color_var.get()

statusBar = Label(root)
canvas = Canvas(root)

saveBtn = Button(root,text="Save",fg="red",command=save,font=("Calibri",20))
saveBtn.grid(row=1,column=1)

forwardBtn = Button(root,text=">>",fg="blue",command=forward,font=("Calibri",25))
forwardBtn.grid(row=1,column=2,pady=10)

backwardsBtn = Button(root,text="<<",fg="blue",command=backward,state=DISABLED,font=("Calibri",25))
backwardsBtn.grid(row=1,column=0)

clearBtn = Button(root,text="Clear Canvas",command=clear,font=("Calibri",15))
clearBtn.grid(row=3,column=0)

switch_frame = LabelFrame(root,text="Rectangle Tool")
switch_frame.grid(row=3,column=1,padx=(0,15),pady=(10,20))

switch_var = StringVar(value="On")
switch = OptionMenu(switch_frame,switch_var,*["On","Off"],command=switch_cmd)
switch.grid(row=0,column=0,pady=5,padx=10)

color_var = StringVar(value="Red")
color_switch = OptionMenu(switch_frame,color_var,*["Red","Green","Blue","Yellow","Black"],command=color_cmd)
color_switch.grid(row=0,column=1,pady=5,padx=10)

root.bind("<Left>",backward)
root.bind("<Right>",forward)
root.bind("<Return>",save)

root.withdraw()
open_new_window()

root.mainloop()