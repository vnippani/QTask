import tkinter as tk
from tkinter import Tk
import requests
from tkinter import Label
from functools import partial
from tkinter import PhotoImage
import sqlite3
import datetime
import os

os.chdir("C:/Users/vinee/Python/QTask")

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

class QuickTask:
    root = tk.Tk()
    canvas = tk.Canvas(root,height = 375, width = 600, bg="#263D42")
    connection = sqlite3.connect("qtask.db") 
    
    #INITIALIZE QUICKTASK
    def __init__(self):
        self.root.resizable(width=False, height=False)
        self.canvas.pack()  
        self.display5Tasks()
        self.root.mainloop()
    
    
    #CLEAR APP SCREEN
    def clear(self):
        list = self.root.place_slaves()
        for l in list:
            l.place_forget()
    
    #CONVERT IMPORTANCE, MONTH, DAY AND YEAR STRINGS TO INTEGERS
    def convertToInt(self,strInput):
        try:
            val = int(strInput)
        except ValueError:
            val = 0
        return val
        
            
    #ATTEMPT TO ADD A TASK TO THE DATABASE     
    def addTask(self,task_name,imp,month,day,year,message):
        task_name = task_name.get(1.0,tk.END)[:-1]
        imp = imp.get(1.0,tk.END)[:-1]
        month = month.get(1.0,tk.END)[:-1]
        day = day.get(1.0,tk.END)[:-1]
        year = year.get(1.0,tk.END)[:-1]
        
        current_time = datetime.datetime.now()
        crsr = self.connection.cursor() 
        error = False
        
            
        if task_name == '' or imp == '' or month == '' or day == '' or year == '':
            error = True
      
        #importance
        if not error:
            imp = self.convertToInt(imp)
            if imp < 1 or imp > 10:
                error = True
          
        #year
        if not error:
            year = self.convertToInt(year)     
            if year < current_time.year:
                error = True
           
        #month
        if not error:
            month = self.convertToInt(month)       
            if month < 1 or month > 12 or (year == current_time.year and month < current_time.month):
                error = True
     
        #day
        if not error:
            day = self.convertToInt(day)
            if month == 2 and (day < 1 or day > 28):
                error = True
            elif (month == 4 or month == 6 or month == 9 or month == 11) and (day < 1 or day > 30):
                error = True
            elif (day < 1 or day > 31):
                error = True
            #account for current day
            if (year == current_time.year and month == current_time.month and day < current_time.day):
                error = True

        #if there are no errors, add the task to the database
        if not error:
            toTable = "INSERT INTO tasks (task_name,importance,month,day,year) VALUES ('" + task_name + "'," + str(imp) + "," + str(month) + "," + str(day) + "," + str(year) + ")"
            crsr.execute(toTable)
            self.connection.commit()
            message.config(text="Success!",font=("Times New Roman", 12), fg="white",bg = "#263D42")
            
        else:
            message.config(text="Error",font=("Times New Roman", 12), fg="red",bg = "#263D42")
    
    #SWITCH INTERFACE TO ADD TASK
    def addInterface(self):
        self.clear()
        
        #task_name
        name = tk.Text(self.root, width = 20, height = 1, font = ("Helvetica",12))
        name.place(x=150,y=275,anchor=tk.CENTER) 
        info = Label(text="Task Name:")
        info.config(font=("Times New Roman", 12), fg="white",bg = "#263D42")
        info.place(x=98,y=250,anchor=tk.CENTER)
        
        #importance
        imp = tk.Text(self.root, width = 2, height = 1, font = ("Helvetica",12))
        imp.place(x=300,y=275,anchor=tk.CENTER) 
        info = Label(text="Imp:")
        info.config(font=("Times New Roman", 12), fg="white",bg = "#263D42")
        info.place(x=300,y=250,anchor=tk.CENTER)
        
        #month
        month = tk.Text(self.root, width = 2, height = 1, font = ("Helvetica",12))
        month.place(x=375,y=275,anchor=tk.CENTER) 
        info = Label(text="Month:")
        info.config(font=("Times New Roman", 12), fg="white",bg = "#263D42")
        info.place(x=375,y=250,anchor=tk.CENTER)
        
        #day
        day = tk.Text(self.root, width = 2, height = 1, font = ("Helvetica",12))
        day.place(x=450,y=275,anchor=tk.CENTER) 
        info = Label(text="Day:")
        info.config(font=("Times New Roman", 12), fg="white",bg = "#263D42")
        info.place(x=450,y=250,anchor=tk.CENTER)
        
        #year
        year = tk.Text(self.root, width = 4, height = 1, font = ("Helvetica",12))
        year.place(x=525,y=275,anchor=tk.CENTER) 
        info = Label(text="Year:")
        info.config(font=("Times New Roman", 12), fg="white",bg = "#263D42")
        info.place(x=525,y=250,anchor=tk.CENTER)
        
        
        #text to display success or failure after add
        tText = Label(text="Add a task!")
        tText.config(font=("Times New Roman", 12), fg="white",bg = "#263D42")
        tText.place(x=300,y=190,anchor=tk.CENTER)
        
        #add task button
        buttonCaller = partial(self.addTask,task_name = name,imp = imp,month = month,day = day,year = year, message = tText)
        sel = tk.Button(self.root,text="Add",padx = 10, pady = 5, fg = "blue",bg="#34ebe1",command = buttonCaller)
        sel.place(x=200,y=350,anchor=tk.CENTER)
        
        #back to task screen button
        buttonCaller = partial(self.display5Tasks)
        sel = tk.Button(self.root,text="Back",padx = 10, pady = 5, fg = "blue",bg="#34ebe1",command = buttonCaller)
        sel.place(x=400,y=350,anchor=tk.CENTER)
        
    
    #DISPLAY TOP FIVE TASKS CURRENTLY IN THE DATABASE
    def display5Tasks(self):
        #clear the screen before displaying tasks
        self.clear()
        
        crsr = self.connection.cursor() 
        getData = "SELECT task_name, month, day, year FROM tasks ORDER BY year ASC, month ASC, day ASC, importance ASC LIMIT 5"
        crsr.execute(getData)
        taskList = crsr.fetchall()
        #place all buttons with the most important task at the top.
        #importance based on date first, importance second
        pos = 50
        for item in taskList:
            buttonCaller = partial(self.deleteItem, task_name = item[0], month = item[1], day = item[2], year = item[3])
            text = item[0] + "    " + str(item[1]) +"-" + str(item[2]) + "-" + str(item[3])
            sel = tk.Button(self.root,text=text,padx = 100, pady = 5, fg = "yellow",bg="#4287f5",command = buttonCaller)
            sel.place(x=300,y=pos,anchor=tk.CENTER)
            pos = pos + 50
            
        buttonCaller = partial(self.addInterface)
        sel = tk.Button(self.root,text="Add",padx = 10, pady = 5, fg = "blue",bg="#34ebe1",command = buttonCaller)
        sel.place(x=50,y=350,anchor=tk.CENTER)
            
    #A TASK HAS BEEN COMPLETED, DELETE IT FROM THE DATABASE
    def deleteItem(self, task_name, month, day, year):
        #button clicked once task is finished
        crsr = self.connection.cursor() 
        delData = "DELETE FROM tasks WHERE (task_name = '" + task_name + "' AND month = " + str(month) + " AND day = " + str(day) + " AND year= " + str(year) + ")"
        crsr.execute(delData)
        self.connection.commit()
        
        #reset app screen after finishing task
        self.display5Tasks()
    
t = QuickTask()
    