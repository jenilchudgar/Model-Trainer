from tkinter import *
from tkinter import filedialog,messagebox
from PIL import ImageTk,Image
from csv import DictWriter
import io,os,random

root = Tk()
root.title("Image Editor")
root.geometry(f"500x700+500+50")
root.iconbitmap("icon.ico")

global current,i_path,o_path,images,statusBar,canvas,color
i_path = ""
o_path = ""
current = 0

start_x = start_y = 0
color = ""
rectangles = []
rectangles_data = {}
original_images = []
label_list = []
label_dict = {}

def show_image(index):
    global rectangles
    rectangles.clear()
    canvas.delete("all")
    canvas.image = images[index]  
    canvas.create_image(0, 0, image=canvas.image, anchor=NW)

    if index in rectangles_data:
        for coords, clr in rectangles_data[index]:
            rect_id = canvas.create_rectangle(*coords, outline=clr.lower(), width=2)
            rectangles.append((rect_id, clr))

def forward(e=None):
    global current
    rectangles_data[current] = [
        (canvas.coords(rect_id[0]), rect_id[1]) for rect_id in rectangles
    ]
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
    rectangles_data[current] = [
        (canvas.coords(rect_id[0]), rect_id[1]) for rect_id in rectangles
    ]
    
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
    global current, o_path, color

    if not images:
        return

    if not rectangles:
        messagebox.showerror("No Rectangle!", "No rectangle has been drawn on the image. Kindly draw rectangle(s) and then click SAVE.")
        return

    img_w, img_h = original_images[current].size
    canvas_w = canvas.winfo_width()
    canvas_h = canvas.winfo_height()
    scale_x = img_w / canvas_w
    scale_y = img_h / canvas_h

    field_names = ["x1", "y1", "x2", "y2", "color", "file"]

    for rect_id in rectangles:
        rect, clr = rect_id[0], rect_id[1]
        c = canvas.coords(rect)

        cords_dict = {
            "x1": round(c[0] * scale_x, 2),
            "y1": round(c[1] * scale_y, 2),
            "x2": round(c[2] * scale_x, 2),
            "y2": round(c[3] * scale_y, 2),
            "color": clr,
            "file": f"image{current+1}.png"
        }

        with open(f"{o_path}\\data.csv", "a", newline="\n") as file:
            writer = DictWriter(file, fieldnames=field_names)
            writer.writerow(cords_dict)

def mouse_press(event):
    global start_x, start_y
    if switch_var.get() == "On":
        global color
        start_x, start_y = event.x, event.y
        rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline=color.lower(), width=2)
        rectangles.append((rect_id, color))

        img_key = f"image{current+1}.png"
        if img_key not in rectangles_data:
            rectangles_data[img_key] = []

        # Get scaling factors based on original image size
        img_w, img_h = original_images[current].size
        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()
        scale_x = img_w / canvas_w
        scale_y = img_h / canvas_h

        rectangles_data[img_key].append({
            "x1": start_x * scale_x,
            "y1": start_y * scale_y,
            "x2": start_x * scale_x,
            "y2": start_y * scale_y,
            "color": color
        })

def mouse_drag(event):
    if switch_var.get() == "On" and rectangles:
        canvas.coords(rectangles[-1][0], start_x, start_y, event.x, event.y)

        img_key = f"image{current+1}.png"
        if img_key in rectangles_data and rectangles_data[img_key]:
            img_w, img_h = original_images[current].size
            canvas_w = canvas.winfo_width()
            canvas_h = canvas.winfo_height()
            scale_x = img_w / canvas_w
            scale_y = img_h / canvas_h

            rectangles_data[img_key][-1]["x2"] = event.x * scale_x
            rectangles_data[img_key][-1]["y2"] = event.y * scale_y

def switch_cmd(e):
    if not (switch_var.get() == "On" or switch_var.get() == "Off"):
        messagebox.showerror("No Option Selected","No option was selected. Please select on or off.")

def clear():
    global current
    if images:
        rectangles.clear()
        canvas.delete("all")
        canvas.image = images[current]  
        canvas.create_image(0, 0, image=canvas.image, anchor=NW)
        rectangles_data[current] = []

def selection(io_selec):
    global i_path,o_path,inputLabel,outputLabel,top

    path = filedialog.askdirectory()
    
    if path: 
        msg = f"Folder ({path.split('/')[-1]}) Selected"

        if io_selec == "i": 
            i_path = path
            inputLabel.config(text=msg)
        if io_selec == "o": 
            o_path = path
            outputLabel.config(text=msg)

def submit():
    global i_path, o_path,label_entry,label_dict,switch,var

    label_list = label_entry.get().split(",")

    if i_path and o_path and (label_list is not None):
        top.destroy()
        root.deiconify()
        root.focus_set()
        load_images()

        menu = switch['menu']
        menu.delete(0,END)
        for label in label_list:
                clr = random_clr()
                label_dict[label] = clr
                menu.add_command(label=label,command=lambda c=clr: color_cmd(c))
        
        var.set(label_list[0])
        color_cmd(label_dict[label_list[0]])
            
def open_new_window():
    global inputLabel,outputLabel,top,label_entry
    top = Toplevel(root) 
    top.title("Input Output Folder Choice")
    top.geometry(f"500x200+550+300")  

    inputLabel = Label(top,text="Select Input Folder")
    inputLabel.grid(row=1,column=0,pady=(25,10),padx=15)

    inputBtn = Button(top,text="Select",command=lambda: selection("i"))
    inputBtn.grid(row=1,column=1,padx=15)

    outputLabel = Label(top,text="Select Output Folder")
    outputLabel.grid(row=2,column=0,pady=10,padx=15)

    outputBtn = Button(top,text="Select",command=lambda: selection("o"))
    outputBtn.grid(row=2,column=1,padx=15)

    label = Label(top,text="Enter Labels (comma seperated)")
    label.grid(row=3,column=0,pady=10,padx=15)

    label_entry = Entry(top,width=40)
    label_entry.grid(row=3,column=1,pady=10,padx=15)

    subBtn = Button(top,text="Submit",command=submit)
    subBtn.grid(row=4,column=0,padx=15,pady=(20,5),columnspan=2)

def load_images(i=1):
    global images, original_images, statusBar, canvas, current, i_path

    if i == 1:
        images = []
        original_images = []

    path = os.path.join(i_path, f"image{i}.png")
    if os.path.exists(path):
        img = Image.open(path)
        original_images.append(img.copy())  # Store original image
        img = img.resize((500, 500))
        images.append(ImageTk.PhotoImage(img))
        root.after(10, lambda: load_images(i + 1))
    else:
        if images:
            statusBar = Label(root, text=f"Image 1 of {len(images)}", bd=1, anchor=E)
            statusBar.grid(row=2, column=0, columnspan=3, sticky=W + E, padx=10)

            canvas = Canvas(root, width=images[current].width(), height=images[current].height())
            canvas.create_image(0, 0, image=images[current], anchor=NW)
            canvas.grid(row=0, column=0, columnspan=3)

            canvas.bind("<ButtonPress-1>", mouse_press)
            canvas.bind("<B1-Motion>", mouse_drag)

def color_cmd(clr):
    global color,label_dict
    color = clr
    
    for item in label_dict:
        if label_dict[item] == color:
            var.set(item)
            break

def random_clr(): 
    clr = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    if clr not in label_dict.values():
        return clr     
    else:   
        random_clr()

statusBar = Label(root)
canvas = Canvas(root)

cmd_frame = Frame(root)
cmd_frame.grid(row=1,column=0,columnspan=3)

saveBtn = Button(cmd_frame,text="Save",fg="red",command=save,font=("Calibri",15))
saveBtn.grid(row=0,column=1,padx=40)

forwardBtn = Button(cmd_frame,text=">>",fg="blue",command=forward,font=("Calibri",25))
forwardBtn.grid(row=0,column=2)

backwardsBtn = Button(cmd_frame,text="<<",fg="blue",command=backward,state=DISABLED,font=("Calibri",25))
backwardsBtn.grid(row=0,column=0)

clearBtn = Button(root,text="Clear Canvas",command=clear)
clearBtn.grid(row=3,column=0,padx=(20,5))

switch_frame = LabelFrame(root,text="Rectangle Tool")
switch_frame.grid(row=3,column=1,padx=(10,15),pady=(10,20))

switch_var = StringVar(value="On")
switch = OptionMenu(switch_frame,switch_var,*["On","Off"],command=switch_cmd)
switch.grid(row=0,column=0,pady=5,padx=10)

var = StringVar()
switch = OptionMenu(switch_frame, var, command=color_cmd,*["None"])
switch.grid(row=0,column=1,pady=5,padx=10)

root.bind("<Left>",backward)
root.bind("<Right>",forward)
root.bind("<Return>",save)

root.withdraw()
open_new_window()

root.mainloop()