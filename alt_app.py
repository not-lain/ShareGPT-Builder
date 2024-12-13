from flask import Flask, render_template, request, redirect, url_for
import json, os

app = Flask(__name__)

def clean_entry(entry):
    entry = entry.strip().replace("\r", "").replace(" \n", "\n")
    return entry

# Route for index/main page
@app.route('/', defaults={'active_tab': 'sft'})
@app.route('/<active_tab>')
def index(active_tab):
    return render_template('index.html', active_tab=active_tab)

# Route for the SFT Dataset Builder.
@app.route('/sft', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Extract form data
        system_prompt = request.form.get('system')
        user_prompts = request.form.getlist('user[]')
        gpt_responses = request.form.getlist('gpt[]')

        # Clean the system prompt, user prompts, and gpt responses
        system_prompt = clean_entry(system_prompt)
        user_prompts = [clean_entry(prompt) for prompt in user_prompts]
        gpt_responses = [clean_entry(response) for response in gpt_responses]
        
        # Data to be appended
        data_to_append = {
            'conversations': [
                {
                    'from': 'system',
                    'value': system_prompt
                }
            ],
            'source': 'manual'
        }

        # Add turns to the conversation
        for user_prompt, gpt_response in zip(user_prompts, gpt_responses):
            data_to_append['conversations'].append({
                'from': 'human',
                'value': user_prompt
            })
            data_to_append['conversations'].append({
                'from': 'gpt',
                'value': gpt_response
            })

        # File path
        file_path = './sft_data.json'

        # Check if file exists and append data
        if os.path.exists(file_path):
            with open(file_path, 'r+', encoding='utf-8') as file:
                data = json.load(file)
                data.append(data_to_append)
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump([data_to_append], file, indent=4)

        return redirect(url_for('index'))
    return redirect(url_for('index'))

# Route for the DPO dataset builder
@app.route('/dpo', methods=['GET', 'POST'])
def dpo_form():
    if request.method == 'POST':
        # Extract form data
        system_prompt = request.form.get('system')
        prompt = request.form.get('prompt')
        chosen = request.form.get('chosen')
        rejected = request.form.get('rejected')

        # Data to be appended
        data_to_append = {
            'system': clean_entry(system_prompt),
            'question': clean_entry(prompt),
            'chosen': clean_entry(chosen),
            'rejected': clean_entry(rejected),
            'source': 'manual'
        }

        # File path
        file_path = './dpo_data.json'

        # Check if file exists and append data
        if os.path.exists(file_path):
            with open(file_path, 'r+', encoding='utf-8') as file:
                data = json.load(file)
                data.append(data_to_append)
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump([data_to_append], file, indent=4)

        return "Success", 200
    return render_template('index.html', active_tab='dpo')

if __name__ == '__main__':
    app.run(debug=True, port=7272)
