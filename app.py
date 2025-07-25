#Web linking
from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    session.clear()
    if request.method == 'POST':
        session['odd_even'] = request.form['odd_even']
        session['user_num'] = int(request.form['user_num'])
        comp = random.randint(0,10)
        session['comp_num'] = comp
        total = session['user_num'] + comp
        session['toss_result'] = 'even' if total % 2 == 0 else 'odd'
        session['user_won'] = (session['odd_even']==session['toss_result'])
        return redirect(url_for('choose'))
    return render_template('index.html')

@app.route('/choose', methods=['GET','POST'])
def choose():
    if not session['user_won']:
        session['user_action'] = random.choice(['bat', 'bowl'])
    else:
        if request.method == 'POST':
            print(request.form)

            session['user_action'] = request.form.get('choice')
            if session['user_action'] not in ['bat', 'bowl']:
                return "Invalid choice!", 400
        else:
            return render_template('choose.html')

    session['first_innings'] = True
    session['user_score'] = 0
    session['comp_score'] = 0
    session['target'] = None
    session['batting'] = 'You' if session['user_action'] == 'bat' else 'Computer'
    session['innings'] = 1
    return redirect(url_for('play'))


@app.route('/play', methods=['GET','POST'])
def play():
    if session.get('innings') is None:
        return redirect(url_for('index'))
    result = {}
    if request.method=='POST':
        u = int(request.form['user_input'])
        c = random.randint(0,10)
        result['user_input']=u
        result['computer_input']=c
        batting=session['batting']
        # double zero logic
        if u==0 and c==0:
            result['double_zero']=True
        elif u==0 and c!=0:
            runs = c
            result['runs']=runs
            if batting=='You':
                session['user_score']+=runs
            else:
                session['comp_score']+=runs
        elif u==c:
            result['out']=True
        else:
            runs = u if batting=='You' else c
            result['runs']=runs
            if batting=='You':
                session['user_score']+=runs
            else:
                session['comp_score']+=runs
        session['last']=result
        # Manage innings and check target
        if result.get('out'):
            if session['innings']==1:
                session['innings']=2
                session['target'] = session['user_score']+1 if batting=='You' else session['comp_score']+1
                session['batting'] = ('Computer' if batting=='You' else 'You')
                return redirect(url_for('play'))
            else:
                return redirect(url_for('result'))
        if session['innings']==2:
            if session['user_score'] >= session['target'] or session['comp_score'] >= session['target']:
                return redirect(url_for('result'))
    return render_template('play.html',
                           user_score=session['user_score'],
                           comp_score=session['comp_score'],
                           first_innings=session['innings']==1,
                           target=session.get('target'),
                           result=session.get('last'),
                           batting=session['batting'])

@app.route('/zero', methods=['POST'])
def zero():
    result={}
    u2 = int(request.form['second_user_input'])
    c2 = random.choice([1,2])
    result['second_user']=u2
    result['second_computer']=c2
    batting=session['batting']
    if u2==c2:
        result['out']=True
    else:
        runs=u2
        result['runs']=runs
        if batting=='You':
            session['user_score']+=runs
        else:
            session['comp_score']+=runs
    session['last']=result
    if result.get('out'):
        return redirect(url_for('play'))
    return redirect(url_for('play'))

@app.route('/result')
def result():
    u = session['user_score']
    c = session['comp_score']
    if u>c:
        winner = "You Win!"
    elif c>u:
        winner = "Computer Wins!"
    else:
        winner = "It's a Tie!"
    return render_template('result.html', user_score=u, comp_score=c, winner=winner)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)




def get_user_input(valid_choices):
    while True:
        try:
            choice = int(input(f"Enter your choice {valid_choices}: "))
            if choice in valid_choices:
                return choice
            else:
                print("Invalid input. Try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_user_odd_even():
    while True:
        choice = input("Choose odd or even: ").strip().lower()
        if choice in ['odd', 'even']:
            return choice
        print("Invalid choice. Please enter odd or even.")

def play_innings(batsman_name, bowler_name, target=None):
    score = 0
    while True:
        if batsman_name == "You":
            bowler = random.choice(list(range(0, 11)))
            batsman = int(input("Enter your choice (0-10): "))
            print(f"{bowler_name} chose: {bowler}")
        else:
            batsman = random.choice(list(range(0, 11)))
            bowler = int(input("Enter your choice (0-10): "))
            print(f"{batsman_name} chose: {batsman}")

        if batsman == 0 and bowler != 0:
            score += bowler
            print(f"Total: {score}")

        # Special rule
        if batsman == 0 and bowler == 0:
            print("\t Both chose 0! Second chance (choose between 1 and 2).")
            if batsman_name == "You":
                batsman = get_user_input([1, 2])
                bowler = random.choice([1, 2])
            else:

                batsman = random.choice([1, 2])
                bowler = get_user_input([1, 2])
                print(f"{batsman_name} chose: {batsman}")

            print(f"Second chance - {batsman_name}: {batsman}, {bowler_name}: {bowler}")
            if batsman == bowler:
                print(f"{batsman_name} is (are) OUT!")
                break
            else:
                score += batsman
                print(f"Total: {score}")
        elif batsman == bowler:
            print(f"{batsman_name} is (are) OUT!")
            break
        else:
            score += batsman
            print(f"Total: {score}")

        if target is not None and score >= target:
            print(f"{batsman_name} has reached the target!")
            break
    return score

def toss():
    print("Toss Time!")
    user_choice = get_user_odd_even()
    user_num = int(input("Enter your choice (0-10): "))
    comp_num = random.choice(list(range(0, 11)))
    total = user_num + comp_num
    print(f"Computer chose: {comp_num}. Total = {total} ({'Even' if total % 2 == 0 else 'Odd'})")

    result = "even" if total % 2 == 0 else "odd"

    if user_choice == result:
        print("You won the toss!")
        while True:
            bat_or_bowl = input("Do you want to 'bat' or 'bowl' first? ").strip().lower()
            if bat_or_bowl in ['bat', 'bowl']:
                return bat_or_bowl
            print("Invalid input. Enter 'bat' or 'bowl'.")
    else:
        print("Computer won the toss!")
        bat_or_bowl = random.choice(['bat', 'bowl'])
        print(f"Computer chooses to {bat_or_bowl} first.")
        return "bowl" if bat_or_bowl == "bat" else "bat" 

print("Welcome to Hand Cricket!")

user_action = toss()

if user_action == "bat":
    print("\n-- First Innings (You Bat) --")
    user_score = play_innings("You", "Computer")
    target = user_score + 1
    print(f"\nYour total: {user_score}")
    print(f"Target for Computer: {target}")

    print("\n-- Second Innings (Computer Batting) --")
    computer_score = play_innings("Computer", "You", target=target)
else:
    print("\n-- First Innings (Computer Bats) --")
    computer_score = play_innings("Computer", "You")
    target = computer_score + 1
    print(f"\nComputer total: {computer_score}")
    print(f"Target for You: {target}")

    print("\n-- Second Innings (You Batting) --")
    user_score = play_innings("You", "Computer", target=target)


print("\nMatch Result:")
if user_score > computer_score:
    print("You win!")
elif user_score < computer_score:
    print("Computer wins!")
else:
    print("It's a Tie!")
