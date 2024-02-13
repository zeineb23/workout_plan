
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

#**Importing dataset**

df = pd.read_csv("megaGymDataset.csv")
df.columns = df.columns.str.replace('Unnamed: 0', 'index')
df['Equipment'] = df['Equipment'].fillna('None')


def input_first():
    st.write("Hello, what are you looking for?", key="input_first")
    text = st.text_input("Type here : ")

    return text

def input_second():
    st.write("Do you prefer to workout at home?")
    home= st.selectbox("", ["","Yes", "No"])

    if (home=="Yes") :
        equip=st.text_input("what equipment do you have?", key="equipment_input")
        equipments = equip.split(",")
        equipments.append("None")
        st.write(equipments)
    return home
def extract_data(text, home):
    def ask_question(iteration):
        if iteration < 3:
                question = questions[iteration]
                answer = qa_pipeline(question=question, context=text)
                if answer['score'] < 0.6:
                    if iteration==0 :
                        x = st.selectbox("Choose your level:", ["","Beginner", "Intermediate", "Advanced"])
                    elif iteration==2:
                        x = st.selectbox("Choose your goal:" ,["","Cut","Bulk","Lean","Strength","Athletic"])
                    else :
                        x= st.selectbox("Enter your days available:",["","2","3","4","5"])
                        
                    if x : 
                        information[question] = x
                        ask_question(iteration + 1)
                else :
                    information[question] = answer["answer"]
                    ask_question(iteration + 1)
        return True  # Termination condition for the recursion

    with st.spinner(f"Processing..."):  
        # Importing model
        model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

    questions = [
        "Are you : Beginner or Intermediate or Expert?",
        "How many days per week can you go to the gym?",
        "What is your goal : Cut or Bulk or Lean or Strength or Athletic ?",
    ]
    information = {}
    if text:
        ask_question(0)
        return information

def execute_function(text,home,information):
        def extract_goal(answer):
                tokens = answer.lower().split()
                goal_keywords = ["cut", "bulk", "strength", "lean"]
                for token in tokens:
                    if token in goal_keywords:
                        return token.capitalize()
                return None
    
        def extract_day(answer):
            return int(answer)
        first_answer = list(information.values())[0]

        second_answer = list(information.values())[1]

        third_answer = list(information.values())[2]

        level=first_answer
        goal=extract_goal(third_answer)
        days=extract_day(second_answer)
        print(goal)
        print(days)
        print(level)
        print("***************************")

        programs={}
        Push = [{'Triceps' : 2}, {'Shoulders' : 2} , {'Chest' :3} ]
        Pull = [{'Biceps' :2}, {'Forearms' :1}, {'Lats' :1}, {'Middle Back':1}, {'Traps':1}]
        Legs = [ {'Abductors' :1} , {'Hamstrings' :2}, {'Quadriceps':2}]
        Glutes = [{'Adductors':1}, {'Glutes':1}]
        Core = [{'Abdominals' :3}, {'Lower Back':2}]

        Upper = Push + Pull
        Lower = Legs + Glutes

        #**Choosing program based on available days and goal**

        if days==2:
                programs.update({'Upper': Upper})
                programs.update({'Legs' : Legs})
        elif days == 3:
                programs['Push'] = Push
                programs['Pull'] = Pull
                programs['Legs'] = Legs
        elif days==4:
                programs['Push'] = Push
                programs['Pull'] = Pull
                programs['Legs'] = Legs
                programs['Core'] = Core
        elif days == 5:
                programs['Chest'] = Push + ['Chest']
                programs['Back'] = Pull + ['Middle Back']
                programs['Shoulder'] = Push + ['Shoulders']
                programs['Legs'] = Legs
                programs['Core'] = Core
        print(programs)

        Types=[]
        if (goal=="Cut") :
                Types=[{'Cardio' : 0.5},{'Strength' : 0.5}]
        elif(goal=="Lean") :
                Types=[{'Cardio' : 0.25},{'Strength' : 0.75}]
        elif(goal=="Bulk") :
                Types=[{'Powerlifting' : 0.5},{'Strength' : 0.5}]
        elif(goal=="Strength") :
                Types=[{'strongman' : 0.5},{'Strength' : 0.5}]
        elif(goal=="Athletic") :
                Types=[{'Plyometrics' : 0.5},{'Olympic Weightlifting' : 0.5}]
        print('---------------------')
        print(Types)
        print(goal)

        key1=list(Types[0].keys())[0]
        key2=list(Types[1].keys())[0]
        coeff1=Types[0][key1]
        coeff2=Types[1][key2]

        """#**Affecting program exercises**"""

        selected_program = pd.DataFrame(columns=['Day','BodyPart', 'Type', 'SelectedExercises'])
        if(home=="No"):
                for day in programs:
                    for part in programs[day]:
                        filtered_exercises = df[(df['BodyPart'] == next(iter(part))) & (df['Type'] == key1)]
                        top_exercises = filtered_exercises.sort_values(by='Rating', ascending=False).head(round(part[next(iter(part))]*coeff1))
                        exercise_titles = top_exercises['Title'].tolist()
                        count_exos=len(top_exercises)
                        if(count_exos>=0):
                            selected_program = pd.concat([selected_program, pd.DataFrame({'Day' : [day] , 'BodyPart': [next(iter(part))], 'Type' : key1 ,'SelectedExercises': [exercise_titles]})], ignore_index=True)

                            filtered_exercises_S = df[(df['BodyPart'] == next(iter(part))) & (df['Type'] == key2) & (df['Level'] == level)]
                            top_exercises_S = filtered_exercises_S.sort_values(by='Rating', ascending=False).head(part[next(iter(part))]-count_exos)
                            exercise_titles_S=top_exercises_S['Title'].tolist()
                            selected_program = pd.concat([selected_program, pd.DataFrame({'Day' : [day] , 'BodyPart': [next(iter(part))], 'Type' : key2, 'SelectedExercises': [exercise_titles_S]})], ignore_index=True)
        else :
                for day in programs:
                    for part in programs[day]:
                        filtered_exercises = df[(df['BodyPart'] == next(iter(part))) & (df['Type'] == key1) & df['Equipment'].isin(equipments)]
                        top_exercises = filtered_exercises.sort_values(by='Rating', ascending=False).head(round(part[next(iter(part))]*coeff1))
                        exercise_titles = top_exercises['Title'].tolist()
                        count_exos=len(top_exercises)
                        if(count_exos>=0):
                            selected_program = pd.concat([selected_program, pd.DataFrame({'Day' : [day] , 'BodyPart': [next(iter(part))], 'Type' : key1 ,'SelectedExercises': [exercise_titles]})], ignore_index=True)

                            filtered_exercises_S = df[(df['BodyPart'] == next(iter(part))) & (df['Type'] == key2) & (df['Level'] == level)]
                            top_exercises_S = filtered_exercises_S.sort_values(by='Rating', ascending=False).head(part[next(iter(part))]-count_exos)
                            exercise_titles_S=top_exercises_S['Title'].tolist()
                            selected_program = pd.concat([selected_program, pd.DataFrame({'Day' : [day] , 'BodyPart': [next(iter(part))], 'Type' : key2, 'SelectedExercises': [exercise_titles_S]})], ignore_index=True)
        st.write(selected_program)


def main():
    st.title('Your workout plan guide')
    text = input_first()

    # Proceed to the next step only if the first input is provided
    if text:
        home = input_second()
    
        if home :
            information=extract_data(text,home)

        # Proceed to execute the function only if the second input is provided
            print(information)
            if information :
                print("HEEEEYYYY")
                if st.button("Execute Function"):
                    execute_function(text,home,information)  # Call the function when the button is clicked

if __name__ == "__main__":
    main()