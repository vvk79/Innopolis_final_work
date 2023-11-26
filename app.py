from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def calculate_sum():
    if request.method == 'POST':
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        num3 = float(request.form['num3'])
        num4 = float(request.form['num4'])
        num5 = float(request.form['num5'])
        num6 = float(request.form['num6'])
        num7 = float(request.form['num7'])
        num8 = float(request.form['num8'])
        result = num1 + num2 + num3 + num4 + num5 + num6 + num7 + num8
        return render_template('index.html', result=result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

#from final_work import linear_regression_prediction
#result = linear_regression_prediction(num1, num2, num3, num4, num5, num6, num7, num8)