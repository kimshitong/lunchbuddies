import os
import telebot
import pandas as pd
import csv
import datetime
from datetime import date


bot = telebot.TeleBot("5917771855:AAHjyjeP6WNnMk0dU8aB8u6Nfyra6u_kXOE", parse_mode=None)

bigdata =[]
status = ""
storage = [] 
StoreStatus = False

def cancel(eventno):
    # Read the CSV file into a DataFrame
    df = pd.read_csv('data.csv')
    # Change the value of a specific cell
    df.iloc[eventno, 9] = False
    # Write the DataFrame back to the CSV file
    df.to_csv('data.csv', index=False)

def importing(data):
    
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader)
    
    with open('data.csv', 'a', newline = '') as file:
        writer = csv.writer(file)
        # Count the number of rows
        data.insert(0,row_count)
        writer.writerow(data)
    return True

def editing(index, column, message):
    global storage

    loading()

    # Read the CSV file into a DataFrame
    df = pd.read_csv('data.csv')

    # Change the value at the desired cell
    df.iloc[index, column] = message.chat.username

    # Write the modified DataFrame back to the CSV file
    df.to_csv('data.csv', index=False)

    
def loading():

    global bigdata
    with open('data.csv', 'r') as file:
        # Create a CSV reader object
        reader = csv.reader(file)

        # Append each row to the data list
        for row in reader:
            bigdata.append(row)

def find(msg,type,message):
    global status
    global storage
    #Case for Venue or remark

    if(type != msg[0]):
        status = ""
        storage = []
        bot.send_message(message.chat.id, "Invalid Prefix")
        return 0
    
    #Remark And Venue
    if(type == '@venue' or type == "@remark"):
        #Verification
        result = "";
        #Copy String
        for i in range (1,len(msg)):                    
            if(i == len(msg)-1):
                result += msg[i]
            else:
                result += msg[i] + " "
        
        #Venue     
        if(type == '@venue'):
            status = "date"
            bot.send_message(message.chat.id, "Please use the following format to create event ")
            bot.send_message(message.chat.id, "@date 22/04/2022 0900")
            return result
        #Remark
        else:
            status = "Confirmation"
            return result
    
    #Date and Time
    elif(type == "@date"):
        print("hello here got?")
        if(len(msg) == 3 ):
            status = "remark"
            bot.send_message(message.chat.id, "Please use the following format to create event ")
            bot.send_message(message.chat.id, "@remark Meet infront of chicken rice shop")
            return [msg[1],msg[2]]
        else:
            status = ""
            storage = []
            bot.send_message(message.chat.id, "Insufficient Information")
            return 0

#/Greet
@bot.message_handler(command = ['Greet'])
def greet(message):
    bot.reply_to(message,"hey")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Welcome ! Please use the following commands.")
	bot.send_message(message.chat.id, "/list /create /join /edit")

@bot.message_handler(commands=['create'])
def send_create(message):
    global status 
    status = "venue" 
    bot.send_message(message.chat.id, "Please use the following format to create event ")
    bot.send_message(message.chat.id, "@venue UTown Green")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    global status
    status = "cancel"     
    bot.send_message(message.chat.id, "@cancel <EventNo>  for example : @cancel 1" )

@bot.message_handler(commands=['list'])
def list(message):
    loading()
    Message = "";
    for singledata in bigdata:
        
        x = datetime.datetime.now()
        Data_Date = int(singledata[2][0:2])
        Data_Month = int(singledata[2][3:5])
        Data_Year = int(singledata[2][6:10])
        CompareDate = datetime.datetime(Data_Year,Data_Month,Data_Date,int(singledata[3][0:2]),int(singledata[3][2:4]))
        
        if(CompareDate > x):
            Message += "="*30 + "\n" + "Event Detail :  \n" "Event "+ singledata[0] +" : Jio Lunch at " + singledata[1] + " ( "+ str(pax) +" / 4) \n"+"Date/Time : " + str(CompareDate) +"\n"

    bot.send_message(message.chat.id, Message + ("="*30) )

@bot.message_handler(commands=['join'])
def list(message):
    global status
    status = "join" 
    bot.send_message(message.chat.id, "Please use the following format to join event")
    bot.send_message(message.chat.id, "@join 1") 

@bot.message_handler(func =lambda msg: msg.text is not None)
def at_answer(message): 
    global storage
    texts = message.text.split()
    print(texts)
    print(status)
    
    if(status =="error"):
        #Reset Temp Storage
        storage = []
    elif(status == "venue"):
        storage.append(find(texts,"@venue",message))

    elif(status == "date"):
        print("1")
        result = find(texts,"@date",message)
        storage.append(result[0])
        storage.append(result[1])

    elif(status == "remark"):
        storage.append(find(texts, "@remark",message))
        storage.append(message.chat.username)
        storage.append("0")
        storage.append("0")
        storage.append("0")
        storage.append(False)
        
        #Confirmation
        bot.send_message(message.chat.id, "="*30)
        bot.send_message(message.chat.id, "Confirmation Detail : ")
        bot.send_message(message.chat.id, "Event : Jio Lunch at " + storage[0])
        bot.send_message(message.chat.id, "Date/Time : " + storage[1] + " at " + storage[2])
        bot.send_message(message.chat.id, "="*30)
        bot.send_message(message.chat.id, "Please Enter @yes to confirm detail")

        #Register Process
    elif(status == "Confirmation"):
        if(len(texts) == 1 and texts[0].upper() == "@YES"):
            #if(function)
            if(importing(storage)):
                print(storage)
                bot.send_message(message.chat.id, "Registration Confirmed, Thanks")
        else:
            bot.send_message(message.chat.id, "Registration Failed")
    elif(status == "cancel"):
        #Size, Numeric, Contains 
        if len(texts) == 2 and texts[1].isnumeric() and int(texts[1]) <= len(bigdata) and int(texts[1]) >=1:
            cancel(texts[1])
        else:
            bot.send_message(message.chat.id, "Invalid Input")
	
    elif(status == "join"):
        #Array Size = 2 && Validity of the number
        loading()
        print(bigdata)
        if len(texts) == 2 and texts[1].isnumeric() and int(texts[1]) <= len(bigdata) and int(texts[1]) >=1:
            if bigdata[int(texts[1])][6] == '0':
                editing(int(texts[1]),6,message)
                bot.send_message(message.chat.id, "See you!")
            elif bigdata[int(texts[1])][7] == '0':
                editing(int(texts[1]),7,message)
                bot.send_message(message.chat.id, "See you!")
            elif bigdata[int(texts[1])][8] == '0':
                editing(int(texts[1]),8,message)
                bot.send_message(message.chat.id, "See you!")
            else:
                bot.send_message(message.chat.id, "The Event is Full")
        else:
            bot.send_message(message.chat.id, "Invalid Input")

        status = ""
        storage = []
    


#Look into





# Array = [
# [EventID,Venue, Date, Time, Remark, Creator,userone,usertwo,userthree]
# [100, Utown, 22/3, 1300, "hello", "Jack"],
# [200, PGP, 23/4 , 1400, "hehe", "Dice"],
# []
# ]





bot.polling()

#Join
# /join 3
