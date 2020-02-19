from tkinter import filedialog, Tk

## Opening a file explorer window to open a file
def open(tkobject, path="/"):
    tkobject.withdraw()
    filename = filedialog.askopenfilename(
        initialdir=path,
        title="Select file",
        filetypes=(("chr files", "*.chr"), ("all files", "*.*")),
    )
    return filename


## Opening a file explorer window to save a file
def save(tkobject, path="/"):
    tkobject.withdraw()
    filename = filedialog.asksaveasfilename(
        initialdir=path,
        title="Select file",
        filetypes=(("chr files", "*.chr"), ("all files", "*.*")),
    )
    return filename


if __name__ == "__main__":
    open(Tk())
