from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory, render_template
import json
import os 
from in_memory_log_handler import custom_logger  # Import the custom handler
import logging
import random
import threading


app = Flask(__name__)

# Thread-local storage for tracking codes
thread_local = threading.local()

@app.route('/', methods=['GET'])
def handle_get():
    return send_from_directory('instructions/','publicReadme.html')

@app.route('/logs', methods=['GET'])
def get_logs():
    # Group logs by tracking_code
    grouped_logs = {}
    for log in custom_logger.logs:
        tracking_code = log['tracking_code']
        if tracking_code not in grouped_logs:
            grouped_logs[tracking_code] = []
        grouped_logs[tracking_code].append(log)
    
    # Pass grouped logs to the template
    return render_template('logtemplates.html', grouped_logs=grouped_logs)

@app.route('/', methods=['POST'])
def handle_post():
    try:
        #text is always available, load it
        text = request.json["text"]
        
        tracking_code = generate_tracking_code(text)

        client = OpenAI()
     
        #header behaviors
        #model selection
        if request.headers.get('model', '')!='':
            selectedModel = request.headers.get('model')
        else:   
            selectedModel = "gpt-4o"

        #followup disable
        if request.headers.get('generateEmpathy', '')=='false':
            promptfile = "without_empathy.txt"
        else:
            promptfile = "with_empathy.txt"   
            
        if request.headers.get('appendEmpathy', '')=='false':
            appendEmpathy = False
        else:
            appendEmpathy = True

        if request.headers.get('appendUserInput', '')=='false':
            appendUserInput = False
        else:
            appendUserInput = True


        
        #conversation may be in the context or not
        if "conversation" in request.json["hiddenContext"]:    
            conversation = request.json["hiddenContext"].get('conversation', [])
            conversation_exist = True
            #logging
            custom_logger.info(f"initial conversation: \n {json.dumps(request.json['hiddenContext']['conversation'],indent=4)}", tracking_code)
     
        else:
            conversation_exist = False
        
        #hardcode instructions for debug 
        if (text.lower() == "restart" ):
            retorno = {
                "openContext": {},
                "visibleContext": {},
                "hiddenContext": {},
                "option": "RESTART"
            }
            return retorno
        
        #first, we try to detect the intention, get the prompt for that and create the openAI call
        promptIntent = get_prompt(promptfile)    
        messagesStack=[]
        messagesStack.append({"role": "system", "content":promptIntent})
        
        #if there is a previous conversation get added to stack to improve detection
        if conversation_exist:
            messagesStack+=conversation

        #add the last user text, highly possible the intent is here
        messagesStack.append({"role": "user", "content": text})


        RawResponseGpt = call_gpt(messagesStack,client, selectedModel)
        
        expected_options = request.json.get('expectedOptions', [])
        
        #logging
        custom_logger.info(f"GPT prompt: {promptIntent}", tracking_code)
        custom_logger.info(f"GPT raw response: {RawResponseGpt}", tracking_code)
        custom_logger.info(f"expected Options: {json.dumps(request.json['expectedOptions'])}", tracking_code)
        try:
            parts = RawResponseGpt.split(',', 1)
            intent = parts[0].strip()
            empathy = parts[1].strip() if len(parts) > 1 else ""
        except Exception as e:
            option = "ERROR"
            custom_logger.error(f"error in split of '{RawResponseGpt}'", tracking_code)
            raise ValueError(f"error in split of '{RawResponseGpt}'", tracking_code)
            

        #the intent needs to be in the expectedOptions, otherwise it will raise an error

        if intent.lower() in [optionI.lower() for optionI in expected_options]:
            option = intent.lower()
        else:
            custom_logger.error(f"intent '{intent}'do not match with ExpectedOptions: {request.json['expectedOptions']}", tracking_code)
            raise ValueError(f"intent '{intent}'do not match with ExpectedOptions: {request.json['expectedOptions']}", tracking_code)
            option = "ERROR"
        
        #logging
        custom_logger.info(f"Intent: {intent}", tracking_code)
        custom_logger.info(f"Empathy: {empathy}", tracking_code)

        # Now, parts[0] contains the first string and parts[1] contains the second string
        #create conversation and message to return    
        storedConversation = []
        if conversation_exist:
            storedConversation+=conversation
        
        if appendUserInput:
            storedConversation.append({"role": "user", "content": text})

        if appendEmpathy:
            storedConversation.append({"role": "assistant", "content": empathy})

        while len(storedConversation) > 10:
            storedConversation.pop(0)

        request.json["hiddenContext"]["conversation"] = storedConversation
        request.json["hiddenContext"]["follow_up"] = empathy
        request.json["hiddenContext"]["optionSelected"] = option
        
        response = {
            "openContext":request.json['openContext'],
            "visibleContext":request.json['visibleContext'],
            "hiddenContext":request.json['hiddenContext'],
            "option" : option
        }
        
        #logging
        if conversation_exist:
            custom_logger.info(f"final conversation: \n { json.dumps(request.json['hiddenContext']['conversation'],indent=4) }",tracking_code)        

        return response

    except Exception as e:
        logging.error(f"Error: {e}")
        response = {
            "openContext": {},
            "visibleContext": {},
            "hiddenContext": {},
            "option": "ERROR"
        }
        return response



def call_gpt(messagesOpenAi, client, selectedModel):
    response = client.chat.completions.create(
        model=selectedModel,
        messages=messagesOpenAi,
        temperature=0.2,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    return response.choices[0].message.content

def get_prompt(promptfile):
    #deal with parameters
    try:
        institutionname= request.json["hiddenContext"]["institution_name"]
    except:
        institutionname = "an institution"
    try:
        botname= request.json["hiddenContext"]["bot_name"]
    except:
        botname = "eva"
    try:
        institutiondesc =  request.json["hiddenContext"]["institution_description"] 
    except:
        institutiondesc = "attending public"

    #add here options in an automatic way
    try:
        intent_list =  request.json["hiddenContext"]["intent_list"] 
    except:
        intent_list = json.dumps(request.json["expectedOptions"])

    with open(promptfile, "r") as file:
        prompt = file.read().strip()
        prompt = prompt.replace("$_INTENTS_$", intent_list).replace("$_BOT-NAME_$",botname).replace("$_INSTITUTION_$",institutionname).replace("$_INSTITUTION-DESCRIPTION_$", institutiondesc)
        return prompt

def generate_tracking_code(text):
    random_number = random.randint(100000, 999999)
    return f"{text}:{random_number}"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))  # Use PORT environment variable if it exists, otherwise default to 8080
    custom_logger.info('Server started.', "Server start messages")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
    