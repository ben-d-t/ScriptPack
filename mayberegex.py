import sys
import json
import re
import openai
import os

systemprompt = '''
Your job is to provide me a regex string that can be parsed in python based off of the query I ask in english.  Provide your answer as a json document containing the explanation and then examples that will match, then the regex. Provide nothing but the JSON. Make sure it is valid json.
For example, if I say:
"Find all the lines that contain only lower case letters and spaces"
then you say:
"{"explanation": "This regex will match any line that contains only lower case letters and spaces. The '^' and '$' anchors ensure that the regex matches the entire line. The '+' quantifier after the character set '[a-z ]' matches one or more occurrences of lower case letters or spaces. The '^$' alternative matches empty lines.","examples": ["hello world","this is a line with spaces","justlowercaseletters"," a line starting with a space and lowercase letters"],  "regex": "^[a-z ]+$|^$"}"
As another example, I say: 
"Find the words separated by a '-'. Example lines that will match include  'Auto-tagging is helpful' or 'You should focus on note-taking'"
then you say:
"{"explanation": "This regex will match any line that contains words separated by a '-' character. The character set '\\\\w' matches any word character (alphanumeric or underscore), the '+' quantifier matches one or more occurrences of word characters, and the '-' character is matched. The whole pattern is repeated one or more times with the '\\\\s+' to match one or more non-word characters between each group of words.",  "examples": ["Auto-tagging is helpful","You should focus on note-taking","This-line-has-four-words"],  "regex": "\\w+(?:-\\w+)+"}"
Let's start.
'''

api_key_path = os.path.expanduser('~/projects/ScriptPack/openai.key')
with open(api_key_path, "r") as api_key_file:
    OPENAI_API_KEY = api_key_file.read().strip()


def fetch_json_data(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": systemprompt},
            {"role": "user", "content": prompt}
        ]
    )

    print("Raw API response:", response)


    return response.choices[0].message.content.strip()



def is_valid_json(json_str):
    try:
        data = json.loads(json_str)
    except ValueError as e:
        print(f"Invalid JSON: {e}")
        return False

    if not isinstance(data, dict):
        print("Malformatted response form OPENAI. JSON data must be a dictionary")
        return False

    if "examples" not in data or "regex" not in data or "explanation" not in data:
        print("Malformatted response form OPENAI. JSON data must contain 'examples', 'explanation' and 'regex' keys")
        return False

    if not (isinstance(data["examples"], list) and isinstance(data["regex"], str) and isinstance(data["explanation"], str)):
        print("Malformatted response form OPENAI.  'examples' and 'explanation' must be a list and 'regex' must be a string")
        return False

    return True


def test_regex(json_data):
    if not is_valid_json(json_data):
        print("Invalid JSON data")
        return
    
    data = json.loads(json_data)
    examples = data["examples"]
    regex_pattern = data["regex"]
    print("\nPattern: ", regex_pattern, "\n\n")
    print("Reasoning: ", data["explanation"])
    print("Testing the Regex Pattern: ", regex_pattern, " with generated input\n")
    
    for example in examples:
        example = example.strip()
        match = re.search(regex_pattern, example)
        if match:
            print(f"{example}:\nMatch")
        else:
            print(f"{example}:\nNo Match")

    user_input_regex_test(regex_pattern)

def user_input_regex_test(regex_pattern):
    print(f"\nTesting user input against regex pattern: {regex_pattern}")
    print("Enter 'q' or 'Q' to quit.")

    while True:
        user_input = input("Enter your input: ")

        if user_input.lower() == 'q':
            break

        match = re.search(regex_pattern, user_input)
        if match:
            print("Match")
        else:
            print("No Match")

def main(prompt):
    if not prompt:
        print("nothing")
        sys.exit(1)

    json_data = fetch_json_data(prompt)
    test_regex(json_data)

if __name__ == "__main__":
    main(*sys.argv[1:])