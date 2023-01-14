import os
import telebot
import pandas as pd
import csv
import datetime

#API
bot = telebot.TeleBot("5917771855:AAHjyjeP6WNnMk0dU8aB8u6Nfyra6u_kXOE", parse_mode=None)
#Global Variables
bigdata =[]
status = ""
storage = [] 

#Cancelling for the Event
def cancel(eventno):
    # Read the CSV file into a DataFrame
    df = pd.read_csv('data.csv')
    # Change the value of a specific cell
    df.iloc[eventno, 9] = True
    # Write the DataFrame back to the CSV file
    df.to_csv('data.csv', index=False)

#Importing Data into CSV/Database 
def importing(data):
	#Rowcount
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader)
    #
    with open('data.csv', 'a', newline = '') as file:
        writer = csv.writer(file)
        #Insert Index to Storage Data
        data.insert(0,row_count)
		#Writing into file
        writer.writerow(data)
    return True

#Appending Participants
def editing(index, column, message):
    global storage
    loading()
	
    # Read the CSV file into a DataFrame
    df = pd.read_csv('data.csv')

    # Change the value at the desired cell
    df.iloc[index, column] = message.chat.username

    # Write the modified DataFrame back to the CSV file
    df.to_csv('data.csv', index=False)

#Load our csv data to our array.
def loading():
    global bigdata
    bigdata = []
	
    with open('data.csv', 'r') as file:
        # Create a CSV reader object
        reader = csv.reader(file)

        # Append each row to the data list
        for row in reader:
            bigdata.append(row)

#Functions of Appending New Event with Several Type.
def find(msg,type,message):
    global status
    global storage
    
	#Validation Check
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
            bot.send_message(message.chat.id, "Please use the following format to create an event: ")
            bot.send_message(message.chat.id, "@date 22/04/2022 0900")
            return result
		
        #Remark
        else:
            status = "Confirmation"
            return result
    
    #Date and Time
    elif(type == "@date"):
        #Does This contains Date, Time ( Need further verification)
        if(len(msg) == 3 ):
            status = "remark"
            bot.send_message(message.chat.id, "Please use the following format to create an event: ")
            bot.send_message(message.chat.id, "@remark Meet infront of chicken rice shop")
            return [msg[1],msg[2]]
        else:
            status = ""
            storage = []
            bot.send_message(message.chat.id, "Insufficient Information")
            return 0

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    global status
    status = ""
    bot.send_message(message.chat.id, "Welcome! Please use the following commands: ")
    bot.send_message(message.chat.id, " /list /create /join /cancel")

@bot.message_handler(commands=['create'])
def send_create(message):
    global status 
    #Following Steps
    status = "venue" 
    bot.send_message(message.chat.id, "Please use the following format to create an event: ")
    bot.send_message(message.chat.id, "@venue UTown Green")

@bot.message_handler(commands=['cancel'])
def send_cancel(message):
    global status
    status = "cancel"     
    bot.send_message(message.chat.id, "@cancel <EventNo>  for example : @cancel 1" )

@bot.message_handler(commands=['list'])
def send_list(message):
    loading()
    Message = ""
    for singledata in bigdata:    
        x = datetime.datetime.now()
		#Data Extraction 
        Data_Date = int(singledata[2][0:2])
        Data_Month = int(singledata[2][3:5])
        Data_Year = int(singledata[2][6:10])
        CompareDate = datetime.datetime(Data_Year,Data_Month,Data_Date,int(singledata[3][0:2]),int(singledata[3][2:4]))
    
        #Cancellation Notcie
        if(singledata[9] == 'True'):
            CancelledMessage = "<Cancelled>"
        else:
            CancelledMessage = ""


		#Determine pax
        pax = 1
        print(singledata)
        if(singledata[8] != '0'):
            pax += 3 
        elif(singledata[7] != '0'):
            pax += 2
        elif(singledata[6] != '0'):
            pax += 1
        #Will Not Display Expire Date
        if(CompareDate > x):
            Message += "="*30 + "\n" + "Event Detail "+ CancelledMessage +" :  \n" "Event "+ singledata[0]  + " : Jio Lunch at " + singledata[1] + " ( "+ str(pax) +" / 4) \n"+"Date/Time : " + str(CompareDate) +"\n"
    bot.send_message(message.chat.id, Message + ("="*30) )

#Join
@bot.message_handler(commands=['join'])
def send_join(message):
    global status
    status = "join" 
    bot.send_message(message.chat.id, "Please use the following format to join event")
    bot.send_message(message.chat.id, "@join 1") 

#Handlers : Receiving Response
@bot.message_handler(func =lambda msg: msg.text is not None)
def at_answer(message):
    global storage
    global status
    loading() 
    texts = message.text.split()
    
    if(status == "venue"):
        storage.append(find(texts,"@venue",message))
    elif(status == "date"):
        result = find(texts,"@date",message)
        storage.append(result[0])
        storage.append(result[1])
    elif(status == "remark"):
        storage.append(find(texts, "@remark",message))
        storage += [message.chat.username,0,0,0,False]
        
        #Confirmation
        bot.send_message(message.chat.id, "="*30 + "\n" +"Confirmation Detail : \n" + "Event : Jio Lunch at " + storage[0] + "\n" + "Date/Time : " + storage[1] + " at " + storage[2] + "\n" + "="*30)
        bot.send_message(message.chat.id, "Please Enter @yes to confirm detail")

    #Register Process
    elif(status == "Confirmation"):
        if(len(texts) == 1 and texts[0].upper() == "@YES"):
            if(importing(storage)):
                bot.send_message(message.chat.id, "Registration Confirmed, Thanks")
        else:
            status = ""
            storage = []
            bot.send_message(message.chat.id, "Registration Failed")
    
	#Canceling
    elif(status == "cancel"):
        #Size, Numeric, Contains : Verification 
        if len(texts) == 2 and texts[1].isdigit() and int(texts[1]) <= len(bigdata) and  int(texts[1]) >= 1:
                print('yes')
                cancel(int(texts[1]))
        else:
            status = ""
            bot.send_message(message.chat.id, "Invalid Input for Cancel")
	
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