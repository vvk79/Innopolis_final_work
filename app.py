from flask import Flask, render_template, request
from final import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        num1 = int(request.form['num1'])
        num2 = float(request.form['num2'])
        num3 = int(request.form['num3'])
        num4 = int(request.form['num4'])
        word1 = request.form['word1']
        word2 = request.form['word2']
        word3 = request.form['word3']
        result = Gradient_boosting_prediction(num1, num2, num3, num4, word1, word2, word3)
        return render_template('index.html', result=result)
    return render_template('index.html')

def calculate_result(num1, num2, num3, num4, word1, word2, word3):
    total_sum = num1 + num2 + num3 + num4
    sentence = f"{word1} {total_sum} {word2} {word3}"
    return sentence

if __name__ == '__main__':
    app.run()