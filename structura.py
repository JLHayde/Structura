import os
import argparse
import sys
import shutil
import traceback
import json

from numpy import array, int32, minimum
import nbtlib
from tkinter import messagebox
from tkinter import StringVar, Button, Label, Entry, Tk, Checkbutton, END, ACTIVE
from tkinter import filedialog, Scale, DoubleVar, HORIZONTAL, IntVar, Listbox, ANCHOR

from log_config import get_logger
from structura_core import Structura
import updater

# CLI Args
parser = argparse.ArgumentParser(
    description="Structura app that generates Resource packs from .mcstructure files."
)

parser.add_argument("--structure", type=str, help=".mcstructure file")
parser.add_argument("--pack_name", type=str, help="Name of pack")
parser.add_argument("--opacity", type=int, help="Opacity of blocks")
parser.add_argument("--icon", type=str, help="Icon for pack")
parser.add_argument("--offset", type=str, help="X, Y, X")
parser.add_argument("--overwrite", type=bool, help="Overwrite the output file.")
parser.add_argument("--debug", "-db", action="store_true", help="Enable debug mode")
parser.add_argument("--update", action="store_true", help="Run updater")

args = parser.parse_args()
logger = get_logger()
logger.info("Launched Structura.")

debug = args.debug
if debug:
    os.environ["DEBUG"] = "1"
    logger = get_logger(level="debug")
    logger.debug("Debug mode is on")


if not (os.path.exists("lookups")):
    logger.warning("No lookups found, fetching...")
    try:
        base_path = sys._MEIPASS
        for resource in ["lookups", "Vanilla_Resource_Pack"]:
            target_dir = os.path.join(os.getcwd(), resource)
            resource_dir = os.path.join(base_path, resource)

            shutil.copytree(resource_dir, target_dir)
            logger.info(f"Resources extracted to {target_dir}")
    # If using `pyinstaller --onefile` instead of .spec the datas are not
    # bundled in the frozen directory, Fallback to download if we error.
    except FileNotFoundError:
        logger.info("Did not find bundled lookup files.")
        logger.info("Downloading lookup files")
        updater.update(
            "https://update.structuralab.com/structuraUpdate", "Structura1-6", ""
        )
    except Exception:
        logger.critical("Error fetching lookup files, details below.")
        logger.critical(traceback.format_exc())


def browseStruct():
    # browse for a structure file.
    FileGUI.set(
        filedialog.askopenfilename(
            filetypes=(("Structure File", "*.mcstructure *.MCSTRUCTURE"),)
        )
    )


def browseIcon():
    # browse for a structure file.
    icon_var.set(filedialog.askopenfilename(filetypes=(("Icon File", "*.png *.PNG"),)))


def update():
    with open(r"lookups\lookup_version.json") as file:
        version_data = json.load(file)
        logger.info(version_data["version"])
    updated = updater.update(
        version_data["update_url"], "Structura1-6", version_data["version"]
    )
    if updated:
        with open(r"lookups\lookup_version.json") as file:
            version_data = json.load(file)
        messagebox.showinfo("Updated!", version_data["notes"])
    else:
        messagebox.showinfo("Status", "You are currently up to date.")


if args.update:
    update()


def box_checked():
    r = 0
    title_text.grid(row=r, column=0, columnspan=2)
    updateButton.grid(row=r, column=2)
    if check_var.get() == 0:
        modle_name_entry.grid_forget()
        modle_name_lb.grid_forget()
        deleteButton.grid_forget()
        cord_lb_big.grid_forget()
        listbox.grid_forget()
        saveButton.grid_forget()
        modelButton.grid_forget()
        cord_lb.grid_forget()
        r += 1
        file_lb.grid(row=r, column=0)
        file_entry.grid(row=r, column=1)
        packButton.grid(row=r, column=2)
        r += 1
        icon_lb.grid(row=r, column=0)
        icon_entry.grid(row=r, column=1)
        IconButton.grid(row=r, column=2)
        r += 1

        packName_lb.grid(row=r, column=0)
        packName_entry.grid(row=r, column=1)
        r += 1
        cord_lb.grid_forget()
        x_entry.grid_forget()
        y_entry.grid_forget()
        z_entry.grid_forget()
        big_build_check.grid_forget()
        transparency_lb.grid_forget()
        transparency_entry.grid_forget()
        get_cords_button.grid_forget()
        advanced_check.grid(row=r, column=0)
        export_check.grid(row=r, column=1)
        saveButton.grid(row=r, column=2)

    else:
        saveButton.grid_forget()
        get_cords_button.grid_forget()
        cord_lb.grid_forget()
        cord_lb_big.grid_forget()
        modle_name_entry.grid_forget()
        modle_name_lb.grid_forget()
        modelButton.grid_forget()
        r += 1
        file_lb.grid(row=r, column=0)
        file_entry.grid(row=r, column=1)
        packButton.grid(row=r, column=2)
        r += 1
        icon_lb.grid(row=r, column=0)
        icon_entry.grid(row=r, column=1)
        IconButton.grid(row=r, column=2)
        r += 1
        packName_lb.grid(row=r, column=0)
        packName_entry.grid(row=r, column=1)
        r += 1
        if big_build.get() == 0:

            modle_name_entry.grid(row=r, column=1)
            modle_name_lb.grid(row=r, column=0)
        else:
            get_cords_button.grid(row=r, column=0, columnspan=2)
        modelButton.grid(row=r, column=2)
        r += 1
        if big_build.get() == 0:
            cord_lb.grid(row=r, column=0, columnspan=3)
        else:
            cord_lb_big.grid(row=r, column=0, columnspan=3)
        r += 1
        x_entry.grid(row=r, column=0)
        y_entry.grid(row=r, column=1)
        z_entry.grid(row=r, column=2)
        r += 1
        transparency_lb.grid(row=r, column=0)
        transparency_entry.grid(row=r, column=1, columnspan=2)
        r += 1
        listbox.grid(row=r, column=1, rowspan=3)
        deleteButton.grid(row=r, column=2)
        r += 4
        advanced_check.grid(row=r, column=0)
        export_check.grid(row=r, column=1)
        saveButton.grid(row=r, column=2)
        r += 1
        big_build_check.grid(row=r, column=0, columnspan=2)


def add_model():
    valid = True
    if big_build.get() == 1:
        model_name_var.set(os.path.basename(FileGUI.get()))

    if len(FileGUI.get()) == 0:
        valid = False
        messagebox.showinfo("Error", "You need to browse for a structure file!")
    if model_name_var.get() in list(models.keys()):
        messagebox.showinfo("Error", "The Name Tag mut be unique")
        valid = False

    if valid:
        name_tag = model_name_var.get()
        opacity = (100 - sliderVar.get()) / 100
        models[name_tag] = {}
        models[name_tag]["offsets"] = [xvar.get(), yvar.get(), zvar.get()]
        models[name_tag]["opacity"] = opacity
        models[name_tag]["structure"] = FileGUI.get()
        listbox.insert(END, model_name_var.get())


def get_global_cords():
    mins = array([2147483647, 2147483647, 2147483647], dtype=int32)
    for name in models.keys():
        file = models[name]["structure"]
        struct = {}
        struct["nbt"] = nbtlib.load(file, byteorder="little")
        if "" in struct["nbt"].keys():
            struct["nbt"] = struct["nbt"][""]
        struct["mins"] = array(list(map(int, struct["nbt"]["structure_world_origin"])))
        mins = minimum(mins, struct["mins"])
        xvar.set(mins[0])
        yvar.set(mins[1])
        zvar.set(mins[2])


def delete_model():
    items = listbox.curselection()
    if len(items) > 0:
        models.pop(listbox.get(ACTIVE))
    listbox.delete(ANCHOR)


def log_build(structura_build):

    logger.info("Build Results...")
    unique_blocks = list(set(structura_build.unsupported_blocks))
    total_count = structura_build.get_unique_blocks_count()
    unsupported_count = len(unique_blocks)
    coverage = round((100 - (unsupported_count / total_count) * 100), 1)
    logger.info("Total Unique Blocks: %s" % total_count)
    logger.info("Total Unsupported Unique Blocks {}".format(unsupported_count))
    logger.info("Coverage of '{}' is {}% ".format(structura_build.pack_name, coverage))
    for i in unique_blocks:
        logger.info("\t {}".format(i.block["name"]))


def runFromGui():
    # wrapper for a gui.
    # global models, offsets
    stop = False
    if os.path.isfile("{}.mcpack".format(packName.get())):
        stop = True
        messagebox.showinfo("Error", "pack already exists or pack name is empty")
        # could be fixed if temp files were used.
    if check_var.get() == 0:
        if len(FileGUI.get()) == 0:
            stop = True
            messagebox.showinfo("Error", "You need to browse for a structure file!")
    if len(packName.get()) == 0:
        stop = True
        messagebox.showinfo("Error", "You need a Name")
    else:
        if len(list(models.keys())) == 0 and check_var.get():
            stop = True
            messagebox.showinfo("Error", "You need to add some structures")

    if not stop:

        structura_base = Structura(packName.get())
        structura_base.set_opacity(sliderVar.get())
        if len(icon_var.get()) > 0:
            structura_base.set_icon(icon_var.get())
        if debug:
            logger.debug(models)

        if not (check_var.get()):
            structura_base.add_model("", FileGUI.get())
            offset = [xvar.get(), yvar.get(), zvar.get()]
            structura_base.set_model_offset("", offset)
            structura_base.generate_with_nametags()
            if export_list.get() == 1:
                structura_base.make_nametag_block_lists()
            structura_base.compile_pack()
        elif big_build.get():
            for name_tag in models.keys():
                structura_base.add_model(name_tag, models[name_tag]["structure"])
            structura_base.make_big_model([xvar.get(), yvar.get(), zvar.get()])
            if export_list.get() == 1:
                structura_base.make_big_blocklist()
            structura_base.compile_pack()
        else:
            for name_tag in models.keys():
                structura_base.add_model(name_tag, models[name_tag]["structure"])
                structura_base.set_model_offset(
                    name_tag, models[name_tag]["offsets"].copy()
                )
            structura_base.generate_with_nametags()
            if export_list.get() == 1:
                structura_base.make_nametag_block_lists()
            structura_base.generate_nametag_file()
            structura_base.compile_pack()

        log_build(structura_base)


# Command Line interface
if args.structure and args.pack_name:

    opacity = args.opacity or 20
    offset = [0, 0, 0]
    if args.offset:
        offset = [int(val) for val in args.offset.split(",")]

    pack_file = "{}.mcpack".format(args.pack_name)
    if args.overwrite and os.path.isfile(pack_file):
        logger.info("Removing existing pack {}".format(pack_file))
        os.remove(pack_file)

    structura_base = Structura(args.pack_name)
    structura_base.set_opacity(opacity)

    if icon := args.icon:
        structura_base.set_icon(icon)

    structura_base.add_model("", args.structure)
    structura_base.set_model_offset("", offset)
    structura_base.generate_with_nametags()
    structura_base.compile_pack()

    log_build(structura_base)

    # Exit Script
    sys.exit(0)

offsetLbLoc = 4
offsets = {}
root = Tk()
root.title("Structura")
models = {}
FileGUI = StringVar()
packName = StringVar()
icon_var = StringVar()
icon_var.set("lookups/pack_icon.png")
sliderVar = DoubleVar()
model_name_var = StringVar()
xvar = DoubleVar()
xvar.set(0)
yvar = DoubleVar()
zvar = DoubleVar()
zvar.set(0)
check_var = IntVar()
export_list = IntVar()
big_build = IntVar()
big_build.set(0)
sliderVar.set(20)
listbox = Listbox(root)
title_text = Label(root, text="Structura")
file_entry = Entry(root, textvariable=FileGUI)
packName_entry = Entry(root, textvariable=packName)
modle_name_lb = Label(root, text="Name Tag")
modle_name_entry = Entry(root, textvariable=model_name_var)
cord_lb = Label(root, text="Offset")
cord_lb_big = Label(root, text="Corner")
x_entry = Entry(root, textvariable=xvar, width=5)
y_entry = Entry(root, textvariable=yvar, width=5)
z_entry = Entry(root, textvariable=zvar, width=5)
icon_lb = Label(root, text="Icon file")
icon_entry = Entry(root, textvariable=icon_var)
updateButton = Button(root, text="Update", command=update)
IconButton = Button(root, text="Browse", command=browseIcon)
file_lb = Label(root, text="Structure file")
packName_lb = Label(root, text="Pack Name")
if debug:
    debug_lb = Label(root, text="Debug Mode", fg="Red").place(x=0, y=2)
packButton = Button(root, text="Browse", command=browseStruct)
advanced_check = Checkbutton(
    root,
    text="advanced",
    variable=check_var,
    onvalue=1,
    offvalue=0,
    command=box_checked,
)
export_check = Checkbutton(
    root, text="make lists", variable=export_list, onvalue=1, offvalue=0
)
big_build_check = Checkbutton(
    root,
    text="Big Build mode",
    variable=big_build,
    onvalue=1,
    offvalue=0,
    command=box_checked,
)

deleteButton = Button(root, text="Remove Model", command=delete_model)
saveButton = Button(root, text="Make Pack", command=runFromGui)
modelButton = Button(root, text="Add Model", command=add_model)
get_cords_button = Button(root, text="Get Global Cords", command=get_global_cords)
transparency_lb = Label(root, text="Transparency")
transparency_entry = Scale(
    root,
    variable=sliderVar,
    length=200,
    from_=0,
    to=100,
    tickinterval=10,
    orient=HORIZONTAL,
)

box_checked()

root.resizable(0, 0)
root.mainloop()
root.quit()
