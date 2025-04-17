import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd

def handleDroppedFile(event):
    file_path = event.data.strip('{}')
    print(f"read {file_path}")
    processFile(file_path)

def processFile(file_path):
    print(f"converting {file_path}")
    logfile = f"{file_path}"

    outLog = []
    outHeaders = []
    firstRead = True

    with open(logfile, 'r') as file:
        for line in file:
            if firstRead:
                outHeaders = line.split(',')
                firstRead = False
                continue
            outLog.append(line.split(','))

    df = pd.DataFrame(outLog, columns=outHeaders)

    newPathList = file_path.split('.')
    del(newPathList[-1])
    newPath = '.'.join(newPathList)

    df.to_csv(f'{newPath}.csv', index=False)

def main():
    root = TkinterDnD.Tk()
    root.title("convert a log to a csv")
    root.geometry("400x200")

    label = tk.Label(root, text="drag log file here to convert", bg="lightgray", relief="ridge", width=40, height=10)
    label.pack(padx=20, pady=40)
    
    label.drop_target_register(DND_FILES)
    label.dnd_bind('<<Drop>>', handleDroppedFile)

    root.mainloop()

if __name__ == "__main__":
    main()
