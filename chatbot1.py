import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
import datetime
import wikipedia #pip install wikipedia
import webbrowser
import os
import requests
import re
import smtplib
from weather import Weather

with open("intents.json") as file:
    data = json.load(file)


try:
    with open("data2.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)

except:

    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)

    with open("data2.pickle", "wb") as f:
        pickle.dump((words, labels, training, output),f)

tensorflow.reset_default_graph()


net=tflearn.input_data(shape=[None,len(training[0])])
net=tflearn.fully_connected(net,8)
net=tflearn.fully_connected(net,8)
net=tflearn.fully_connected(net,len(output[0]),activation="softmax")
net=tflearn.regression(net)
model=tflearn.DNN(net)

try:
    model.load("model.tflearn")
except:

    model.fit(training,output,n_epoch=1000,batch_size=8,show_metric=True)
    model.save("model.tflearn")

def bag_of_words(s,words):
    bag=[0 for _ in range(len(words))]

    s_words=nltk.word_tokenize(s)
    s_words=[stemmer.stem(word.lower()) for word in s_words]
    for se in s_words:
        for i,w in enumerate(words):
            if w==se:
                bag[i]=1
    return numpy.array(bag)




    
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[1].id)
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")   

    else:
        speak("Good Evening!")  

    speak("I am doraemon.  tell me how may I help you")       

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source,duration=0.5)
        r.energy_threshold=300
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        print(e)    
        print("Say that again please...")  
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('prateeksinghkhutail@gmail.com', 'khutailjaat')
    server.sendmail('prateeksinghkhutail@gmail.com', to, content)
    server.close()

if __name__ == "__main__":
    wishMe()
    while True:
    # if 1:
        query = takeCommand().lower()

        # Logic for executing tasks based on query
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=3)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")   

        elif 'open gmail' in query:
            webbrowser.open("gmail.com")


        elif 'play music' in query:
            music_dir = 'D:\\Music\\punjabi'
            songs = os.listdir(music_dir)
            print(songs)    
            os.startfile(os.path.join(music_dir, songs[0]))

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")    
            speak(f"Sir, the time is {strTime}")

        elif 'open code' in query:
            codePath = "C:\\Users\\prate\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            os.startfile(codePath)


        elif 'joke' in query:
            res = requests.get('https://icanhazdadjoke.com/',
                headers={"Accept":"application/json"}
                )
            if res.status_code == requests.codes.ok:
                print((str(res.json()['joke'])))
                speak(str(res.json()['joke']))

                
            else:
                print('oops!I ran out of jokes')
                speak('oops!I ran out of jokes')



        elif 'current weather in' in query:
            reg_ex = re.search('current weather in (.*)', query)
            if reg_ex:
                city = reg_ex.group(1)
                api_address='http://api.openweathermap.org/data/2.5/weather?appid=277e3f44496d4b82df481a2fc4d7b9a8&q='
                url = api_address + city
                weather = Weather()
                location = weather.lookup_by_location(city)
                condition = location.condition()
                speak('The Current weather in %s is %s The tempeture is %.1f degree' % (city, condition.text(), (int(condition.temp())-32)/1.8))

        
        elif 'open reddit' in query:
            reg_ex = re.search('open reddit (.*)', query)
            url = 'https://www.reddit.com/'
            if reg_ex:
                subreddit = reg_ex.group(1)
                url = url + 'r/' + subreddit
                webbrowser.open(url)
                print('Done!')
                speak('done!')

                
        elif 'open website' in query:
            reg_ex = re.search('open website (.+)', query)
            if reg_ex:
                domain = reg_ex.group(1)
                url = 'https://www.' + domain
                webbrowser.open(url)
                print('Done!')
            else:
                speak('sorry i was unable to open the required website')
                print('sorry i was unable to open the required website')

        elif 'send e-mail' in query:
            try:
                speak("whom do you want to send mail?")
                to=input('enter e-mail address:')
                speak("What should I say?")
                content = takeCommand()   
                sendEmail(to, content)
                speak("Email has been sent!,what else i can do for you?")
            except Exception as e:
                print(e)
                speak("Sorry. I am not able to send this email fue to some problems")    
        elif 'none' in query:
            pass
        else  :
        
            inp=query
            if inp.lower()=="quit":
                break

            results=model.predict([bag_of_words(inp,words)])
            results_index=numpy.argmax(results)
            
            tag = labels[results_index]
            
            for tg in data["intents"]:
                if tg['tag']==tag:
                    responses=tg['responses']
            print(random.choice(responses))
            speak(random.choice(responses))
