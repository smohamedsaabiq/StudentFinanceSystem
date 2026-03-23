from flask import Flask, render_template, request, redirect
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["student_finance_db"]
collection = db["finance"]


# Home page
@app.route('/')
def home():
    return render_template('index.html')


# Add Income
@app.route('/add_income', methods=['GET', 'POST'])
def add_income():

    if request.method == 'POST':

        source = request.form['source']
        amount = int(request.form['amount'])

        collection.insert_one({
            "type": "income",
            "source": source,
            "amount": amount
        })

        return redirect('/report')

    return render_template('add_income.html')


# Add Expense
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():

    if request.method == 'POST':

        item = request.form['item']
        amount = int(request.form['amount'])

        collection.insert_one({
            "type": "expense",
            "item": item,
            "amount": amount
        })

        return redirect('/report')

    return render_template('add_expense.html')


# Report page
@app.route('/report')
def report():

    data = list(collection.find())

    income = [d for d in data if d["type"] == "income"]
    expense = [d for d in data if d["type"] == "expense"]

    total_income = sum(i["amount"] for i in income)
    total_expense = sum(e["amount"] for e in expense)

    balance = total_income - total_expense


    # find highest expense
    highest_expense = None
    alert_message = ""

    if expense:

        highest_expense = max(expense, key=lambda x: x["amount"])


        # case 1 : expenses more than income
        if total_expense > total_income:

            alert_message = "Warning! Your expenses are more than income!"


        # case 2 : single expense too high
        elif highest_expense["amount"] > (total_income * 0.5):

            alert_message = "Warning! Highest spending is on " + highest_expense["item"]


        # case 3 : good spending
        else:

            alert_message = "Good! Your spending is under control."


    return render_template(
        'report.html',
        income=income,
        expense=expense,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        highest_expense=highest_expense,
        alert_message=alert_message
    )


# clear all data
@app.route('/clear')
def clear():

    collection.delete_many({})

    return redirect('/')


# view all records (optional page)
@app.route('/view')
def view():

    data = collection.find()

    return render_template('view.html', data=data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
