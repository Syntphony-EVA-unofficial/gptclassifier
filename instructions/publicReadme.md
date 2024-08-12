
![](https://eva.bot/wp-content/uploads/2021/11/Logo-Eva.png)
> Documentation made with https://dillinger.io/
> [View Logs](./logs)
# Intent classifier GPT-4 for eva.

## Description

> Note: `Warning` This function is only for use in service cell of Virtual Agents build with [Synthopy Conversational AI Platform](https://eva.bot)

For use this function, include the URL in the webhook field in the service cell you want to run the classifier. For more information about Service Cell, go to eva.bot documentation [Service Cell](https://docs.eva.bot/user-guide/using-eva/develop-your-bot/dialog-cells/service)

### Requirements

* All the conversations between the eva Virtual Agents and the human/users are stored in **hiddenContext.conversation**, do not override this variable in your bot/flows when using this classifier. Check this to know more about [eva Dynamic content](https://docs.eva.bot/user-guide/using-eva/advanced-options/dynamic-content-and-contexts)
* The service cell with this function in the webhook must have an option set as **not_expected** for all the messages that does not trigger an intent. 
* Every other intent must be in the option list, to do this, define a variable **hiddenContext.intent_list** before the service cell.
* The **hiddenContext.intent_list** variable can be set in a code cell. Check this to know more about [code cell](https://docs.eva.bot/user-guide/using-eva/develop-your-bot/dialog-cells/code)
* The code cell content can be like this:

 >**hiddenContext.intent_list** = 
    " 1. apply_card: Intent to apply a new credit card.
    2. credit_card_info: Intent to ask for credit card limit, used and available credit.
    3. block_card: Intent to block a lost or stolen card.
    4. latest_transactions: Intent to check the latest card transactions and when a user has doubts about transactions.
    5. report_fraud: Intent to report a fraud based on an unrecognize transaction either online or with a stolen/cloned card.
    6. general_info: intent to ask for product information and conditions."

* Do not include a "not_expected" in the intent list, it is not needed.
* Is important that intents defined in the list are express with the same name in the service cell as options.
* If the varialbe **hiddenContext.intent_list** is not defined, the service cell options will be used as intent description, of course it is recommended to set the intent list.

### Classifier response

After the service cell will runs, one of the options will trigger,

* ERROR is a default path/option when the function found an error. You cannot remove this path.
* NOT_EXPECTED is a path/option for every message the classifier do not detect any availabe intent
* If the classifier founds an intent in the conversation, it will trigger an appropiated path/option set in the **hiddenContext.intent_list**
* If the NOT_EXPECTED path/option is trigger, the **hiddenContext.follow_up** variable will contain a message to tell the user the message is not clear enought to understand the intent, this message is empathic based on previous messages. To use this feature, put a Answer Cell after the not_expected path of the service cell. Check this to know more about [Answer Cell](https://docs.eva.bot/user-guide/using-eva/develop-your-bot/dialog-cells/answer)
* If an intent is trigger, the **hiddenContext.follow_up** variable will contain a message to tell the user it will go to another flow, this message is empathic based on previous messages. To use this feature, put a Answer Cell after the intent path/option of the service cell.
* The follow_up message is optional and you can used it only in the option/path that makes more sense.

### Clasifier options
You can modify the behavior of the classifier by using the service cell header. Below are the options available:

**Model:** This option allows you to specify the GPT model to be used. To set this, create a header entry with the name “model” and set its value to the desired model name. The default value is “gpt-4o”.
`Warning`: Be sure to use valid model names like gpt-3.5-turbo, gpt-4, gpt-4o, gpt-4-turbo.

**Generate Empathy:** The follow-up response is optional. To disable it, create a header entry with the name “generateEmpathy” and set its value to “false”. The default value is true. 
Disable the follow-up makes the prompt smaller and therefore faster, but the service will only classify the intent without further interaction.

**Append Empathy:** Determines if the additional empathetic content should be appended to the end of the conversation stack. To prevent appending empathy, set the "appendEmpathy" header to “false”. If not set or set to any other value, "appendEmpathy" will be appended by default.

**Append User Input:** This option decides whether the user's input should be appended to the conversation stack. To avoid appending user input, set the "appendUserInput" header to “false”. If not specified or set to any other value, the user input will be appended by default.

### Improve classifier

In order to improve the classifier behavior some variables with context should be set. If these variables are not defined, the classifier will still work but the follow up answer will be generic.

* The variable **hiddenContext.institution_name** should be used for the institution name, like "Wakanda International Bank"
* The variable **hiddenContext.institution_description** should be used to describe the institution and set some context, like "Finantial Services for major companies both in Wakanda and other countries"
* The variable **hiddenContext.bot_name** should be used to describe the bot name, like "Wakobot"

### Development

This is an experimental feature, please make extensive test to realize is this is the best option for your project
