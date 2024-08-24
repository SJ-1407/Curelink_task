import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
   

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


url = "https://clchatagentassessment.s3.ap-south-1.amazonaws.com/queries.json"
response = requests.get(url)
 

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


prompt_final_response = ChatPromptTemplate.from_messages(
    [("system","""

You are an experienced and empathetic doctor specializing in diet and nutrition. You will receive a patient's profile, their latest dietary query, including detailed descriptions of their meals, and the ideal meal prescribed for them at a specific time.

Your task is to:
1. **Thoroughly analyze each entry** in the latest query list to fully understand what the patient is consuming and what they are asking. Ensure that you consider every detail provided in the latest query.Analyze every image's description carefully.
2. **Carefully compare** the described meal with the prescribed ideal meal:
   - Identify any missing components from the ideal meal.
   - Note any unapproved additions or modifications to the meal, and mention it in your response,so that the patient knows about it.
   - Recognize and acknowledge if the patient has consumed the correct ingredients even if in a different form.
    -Do not aggressively find out mistakes.
3. **Respond with  precision, suggest improvements if and only if needed**:
   - If the patient has deviated from the ideal meal, gently inquire about the reason for the change and suggest necessary adjustments or additions to align with the prescribed diet.
   - If the patient is missing something from the ideal meal, kindly encourage them to include it in the future in brief.
   - Ensure that your response is clear, concise, and supportive, and your response shpuld be in same language and style as that of the patient's query.
4. ** Suggest improvements if and only if needed**:
   - If the patient is making an effort but there are minor discrepancies, suggest small, manageable changes,ignore if not that important.
   - Avoid overwhelming the patient with too much information; focus on actionable advice that aligns with their goals,only if needed.
   - Do not provide additional recommendations or suggest alternative meals or timings.
   - Do not provide any additional information beyond the comparison and suggestions.
5. **Brief and focused response**:
    - Your response should be brief and to the point, addressing the key points of comparison and providing constructive feedback.
    - Avoid detailed explanations or nutritional benefits.
    - Make sure to not provide any other suggestions or recommendations to the patient other than the ones mentioned above.
    - Do not add any unnecessarry salutations or closings to the response.
    - Ensure that you do not talk about any other meal , also do not mention what you see in the image explicitly.
    - Make sure not to be redundant in your response.
    - Do not try to aggresievley point out the patient's mistake , for instance if the patient has menmtioned to have eaten something which is not mentioned in the imgage descriptions , trust the patient of consuming the right thing.
    - Do not ask the patient to follow the diet chart strictly,for instance if patient is having either of the options of the ideal meal then it is good, however given the notes, if there is a lack of ideal requirements,do mention it.
    - Do not mention the ideal meal redundantly in the response.
    - Do not mention the notes provided in the reponse.
    -Keep the response simple and to the point and easily understandable.
    

Patient's Profile: {patient_profile}
Latest Query: {latest_query}
Ideal Meal: {ideal_meal}
"""
,),]



)
chain = prompt_final_response | llm


prompt_llm_as_judge = ChatPromptTemplate.from_messages(
    [("system","""

You are an experienced and empathetic doctor specializing in diet and nutrition. You will receive a  latest dietary query, including detailed descriptions of their meals, and the ideal meal prescribed for them at a specific time.
**Thoroughly analyze each entry** in the latest query list to fully understand what the patient is consuming and what they are asking. Ensure that you consider every detail provided in the latest query.Analyze every image's description carefully.
you have to compare the ideal meal and the meal the patient is currently having and just  return a score between 0 and 1 in float  and not any other data or information based on how close the patient's meal is to the ideal meal.
Do not provide any other information or suggestions to the patient.
Latest Query: {latest_query}
Ideal Meal: {ideal_meal}
"""
,),]
)
chain_1 = prompt_llm_as_judge | llm


with open("queries.json", "wb") as file:
    file.write(response.content)

print("Download complete. File saved as 'queries.json'.")


with open("queries.json", "r") as file:
    data = json.load(file)


def clean_html(html_content):
        """
        Converts HTML to plain text for readability.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

'''Coded the below function to print the diet chart in a more readable format , just for a better understanding.
Can be used if needed.

def print_diet_chart_1(diet_chart):
    print(f"Diet Chart ID: {diet_chart['id']}")
    print(f"Updated At: {diet_chart['updated_at']}")
    print(f"Start Date: {diet_chart['start_date']}")
    print("Notes: ")
    if(diet_chart['notes']!=None):
     print(clean_html(diet_chart['notes']))  
    print("\n")
    for day in diet_chart['meals_by_days']:
        print(f"Day {day['order']}:")
        for meal in day['meals']:
            print(f"  Meal: {meal['name']} at {meal['timings']}")
            for meal_option in meal['meal_options']:
                print("    Meal Option:")
                #print(f"    Notes: {meal_option['notes']}")
                if(meal_option['notes']!=None):
                    soup = BeautifulSoup(meal_option['notes'], "html.parser")
                    clean_notes = soup.get_text()

                    print(f"    Notes: {clean_notes.strip()}")
                for item in meal_option['meal_option_food_items']:
                    food_name = item['Food']['name']
                    quantity = item['food_measure_quantity']
                    measure_name = item['Food'].get('food_measures', [{'name': 'unit'}])[0]['name']  # Default to 'unit' if not present
                    calories = item['Food'].get('calories', 'N/A')
                    fats = item['Food'].get('fats', 'N/A')
                    carbs = item['Food'].get('carbs', 'N/A')
                    protein = item['Food'].get('protein', 'N/A')
                    fibre = item['Food'].get('fibre', 'N/A')

                    # Print food item details
                    print(f"      - {quantity} {measure_name} of {food_name}")
                    print(f"        - Calories: {calories}")
                    print(f"        - Fats: {fats}g")
                    print(f"        - Carbs: {carbs}g")
                    print(f"        - Protein: {protein}g")
                    print(f"        - Fibre: {fibre}g")
            print("\n")
        print("\n")
'''

def extract_information(query):
    profile_context = query['profile_context']
    patient_profile = profile_context['patient_profile']
    diet_chart = profile_context['diet_chart']
    latest_query = query['latest_query']
    chat_context = query['chat_context']
    ideal_response = query['ideal_response']

    return patient_profile, diet_chart, latest_query, chat_context, ideal_response


def parse_time(time_string):
    """
    Convert time in 'HH:MM AM/PM' format to a datetime object.
    """
    return datetime.strptime(time_string, '%I:%M %p')

def get_ideal_meal(diet_chart, timestamp,latest_query):
    """
    Given a diet chart and a timestamp, find the ideal meal corresponding to that time.
    """
    # Convert the timestamp to a datetime object (e.g., "June 14, 2024, 07:05 AM")
    query_time = datetime.strptime(timestamp, '%B %d, %Y, %I:%M %p')
    closest_meal_time = float('inf')
    meal_description = ""
    score=float('-inf')
    flag=0

    # Calculating the number of days since the diet chart start date
    start_date = datetime.strptime(diet_chart['start_date'], '%Y-%m-%dT%H:%M:%SZ')
    days_since_start = (query_time.date() - start_date.date()).days

    # Ensuring the days_since_start is valid
    if days_since_start < 0 or days_since_start >= len(diet_chart['meals_by_days']):
        return "No meal available for this date."

    # Getting the meals for the relevant day
    meals_for_day = diet_chart['meals_by_days'][days_since_start]['meals']

    # Finding the ideal meal based on the query time
    for meal in meals_for_day:
        meal_time = parse_time(meal['timings'])
        meal_time = meal_time.replace(year=query_time.year, month=query_time.month, day=query_time.day)
        
        # Checking if the query time is within the meal time range (I have assumed +/- 2 hour tolerance,however it can be changed as per the requirement)
        if abs((query_time - meal_time).total_seconds())<=7200   :  # 2 hour = 7200 seconds
            # Extracting the meal details
                '''Earlier I was using the closest_meal_time as a paramter to find the closest meal to the query time, 
                however in some cases it did not provide the correct meal as required ,so I decided to use llm as a judge to get the correct meal'''
          
               
                meal_temp=meal_description
              
                meal_description = f"Ideal meal at {meal['timings']} is: {meal['name']}\n"
            
                meal_description += "Meal Options:\n"
                
                for meal_option in meal['meal_options']:
                    soup = BeautifulSoup(meal_option['notes'], "html.parser")
                    clean_notes = soup.get_text()
                    meal_description += "Notes:\n" + (clean_notes) + "\n"
                    option_details = "  - Option:\n"
                    for item in meal_option['meal_option_food_items']:
                        food_name = item['Food']['name']
                        quantity = item['food_measure_quantity']
                        measure_name = item['Food'].get('food_measures', [{'name': 'unit'}])[0]['name']  # Default to 'unit'
                        calories = item['Food'].get('calories', 'N/A')
                        fats = item['Food'].get('fats', 'N/A')
                        carbs = item['Food'].get('carbs', 'N/A')
                        protein = item['Food'].get('protein', 'N/A')
                        fibre = item['Food'].get('fibre', 'N/A')
                        
                        # Format food item details
                        item_detail = (f"    - {quantity} {measure_name} of {food_name} "
                                    f"(Calories: {calories}, Fats: {fats}g, Carbs: {carbs}g, "
                                    f"Protein: {protein}g, Fibre: {fibre}g)")
                        option_details += item_detail + "\n"
                    
                    meal_description += option_details + "\n"
                    response = chain_1.invoke(
                        {
                            "latest_query": latest_query,
                            "ideal_meal": meal_description
                        }
                    )
                    if(float(response.content)>score):
                        flag=1
                        score=float(response.content)
                        closest_meal_time=abs((query_time - meal_time).total_seconds())
                    elif(float(response.content)==score):
                        if(closest_meal_time<abs((query_time - meal_time).total_seconds())):
                            meal_description=meal_temp
                    else:
                        meal_description=meal_temp

    if(flag!=1):
         return "No meal found for the given time."     
    else:  
      return meal_description.strip()
    
def get_latest_query_timestamp(latest_query, chat_context):
    
    #Given the latest query and the chat context, finding the timestamp corresponding  latest query.

    chat_history = chat_context['chat_history']

    for query in latest_query:
        query_content = query['content'].strip().lower()
        
        for message in chat_history:
            if message['message'].strip().lower() == query_content:
                return message['timestamp']
    



all_data = []

for i in range(len(data)):

        patient_profile, diet_chart, latest_query, chat_context, ideal_response = extract_information(data[i])


        timestamp = get_latest_query_timestamp(latest_query, chat_context)


        ideal_meal = get_ideal_meal(diet_chart, timestamp,latest_query)

   
        response = chain.invoke(
            {
            
                "patient_profile": patient_profile,
                "latest_query": latest_query,
                "ideal_meal": ideal_meal
            }
        )

        output_data={
                "ticket_id": chat_context["ticket_id"],
                "latest_query": latest_query,
                "generated_response": response.content,
                "ideal_response": ideal_response
        }

        all_data.append(output_data)

output_file_path = "output.json"
with open(output_file_path, 'w') as file:
    json.dump(all_data, file, indent=4)

print(f"Data saved successfully in {output_file_path}.")
