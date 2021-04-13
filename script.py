import random
import sqlite3


connection = sqlite3.connect('card.db')
cursor = connection.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS card (
    id INTEGER PRIMARY KEY,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0);
""")


def luhn(number):
    original_number = list(str(number))
    drop_last_digit = [int(num) for num in original_number[:-1]]
    mul_odd_by_2 = [num if i % 2 else num * 2 for i, num in enumerate(drop_last_digit)]
    sub_9 = [num - 9 if num > 9 else num for num in mul_odd_by_2]
    last_digit = 10 - sum(sub_9) % 10
    return ''.join([str(num) for num in drop_last_digit] + [str(last_digit)[-1]])


def create_card():
    card_number = luhn(4 * 10 ** 15 + random.randint(0, 10 ** 10))
    card_pin = str(random.randint(0, 10000))
    while len(card_pin) < 4:
        card_pin = '0' + card_pin
    print(f'Your card has been created\n'
          f'Your card number:\n'
          f'{card_number}\n'
          f'Your card PIN:\n'
          f'{card_pin}\n')
    cursor.execute(f'INSERT INTO card (number, pin) VALUES ({card_number}, {card_pin});')
    connection.commit()


def account(card_number):
    while True:
        print('1. Balance\n'
              '2. Add income\n'
              '3. Do transfer\n'
              '4. Close account\n'
              '5. Log out\n'
              '0. Exit\n')
        cursor.execute(f'SELECT balance FROM card WHERE number={card_number}')
        balance = cursor.fetchone()[0]
        entry = input()
        if entry == '1':
            print('Balance:', balance)
        if entry == '2':
            print('Enter income: ')
            cursor.execute(f'UPDATE card SET balance=balance+{int(input())} WHERE number={card_number}')
            connection.commit()
            print('Income has added!')
        if entry == '3':
            print('Transfer\n'
                  'Enter card number:')
            transfer = int(input())
            if str(transfer) != luhn(transfer):
                print('Probably you made a mistake in the card number. Please try again!')
                continue
            cursor.execute(f'SELECT number FROM card WHERE number={transfer}')
            query = cursor.fetchone()
            print('QUERY', query)
            if not query:
                print('Such a card does not exist.')
            else:
                print('Enter how much money you want to transfer:')
                amount = int(input())
                if amount > balance:
                    print('Not enough money!')
                else:
                    cursor.execute(f'UPDATE card SET balance=balance+{amount} WHERE number={transfer}')
                    cursor.execute(f'UPDATE card SET balance=balance-{amount} WHERE number={card_number}')
                    connection.commit()
                    print('Success!')
            if entry == '4':
                cursor.execute(f'DELETE FROM card WHERE number={card_number}')
                connection.commit()
                break
            if entry == '5':
                print('You have succesfully logged out!')
                break
            if entry == '0':
                exit()


def main():
    while True:
        print('1. Create an account\n'
              '2. Log into account\n'
              '0. Exit')
        entry = input()
        if entry == '1':
            create_card()
        elif entry == '2':
            print('Enter your card number:')
            user_number = input()
            print('Enter your PIN:')
            user_pin = input()
            query_pin = cursor.execute(f'SELECT substr("0000"||pin, 4) FROM card WHERE number={user_number}').fetchone()
            if user_pin == (query_pin[0] if query_pin else None):
                print('You have succesfully logged in!')
                account(user_number)
            else:
                print('Wrong card number or PIN!')
        elif entry == '0':
            print('Bye!')
            exit()


main()
