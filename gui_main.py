import tkinter as tk


window = tk.Tk()
window.title('Ceiba Downloader by jameshwc')
window.geometry('600x800')
label1 = tk.Label(window, text='')

button_login = tk.Button(window, text='登入')

# button_login.grid(column=0, row=0)
button_login.pack(side='top', ipadx=100, padx=100)
label1.pack()
window.mainloop()