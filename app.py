from flask import Flask, render_template, request
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

app = Flask(__name__, static_folder='static')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model
def load_model():
    try:
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        logger.info("Model loaded successfully.")
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

model, tokenizer = load_model()

def generate_response(prompt):
    try:
        full_prompt = f"You are a helpful AI Assistant.\nUser: {prompt}\nAI:"
        inputs = tokenizer(full_prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        output = model.generate(
            **inputs,
            max_length=2048,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7
        )
        decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded_output.split("AI:")[-1].strip()
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Sorry, something went wrong."

@app.route('/')
def home():
    return render_template('page1.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/page3', methods=['GET', 'POST'])
def page3():
    if request.method == 'POST':
        if 'profile' in request.form:
            profile = request.form['profile']
            suggestion = generate_response(f"Suggest a career for someone interested in {profile}")
            return render_template('results.html', user_input=profile, response=suggestion)

        elif 'ingredient' in request.form:
            ingredient = request.form['ingredient']
            recipe = generate_response(f"Suggest a recipe using {ingredient}")
            return render_template('results.html', user_input=ingredient, response=recipe)

        elif 'mood' in request.form:
            mood = request.form['mood']
            encouragement = generate_response(f"I'm feeling {mood}, give me some encouragement.")
            return render_template('results.html', user_input=mood, response=encouragement)

        """elif 'email' in request.form and 'password' in request.form:
            result = "Email classification not implemented yet."
            return render_template('results.html', user_input="email check", response=result)"""

    return render_template('page3.html')

if __name__ == '__main__':
    app.run(debug=True)
