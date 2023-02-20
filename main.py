import smtplib
import datetime
import psycopg2
import pandas as pd

from time import sleep
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def process_transactions(path_file):
    df = pd.read_csv(
        path_file,
        sep = ',',
        header = 0,
    )

    df['Date'] = df['Date'].str.split('/').str[0].astype('int')
    df['Transaction'] = df['Transaction'].astype('float')

    total_balance = df['Transaction'].sum()
    average_debit = df['Transaction'][df['Transaction'].apply(lambda x: x >= 0)].mean()
    average_credit = df['Transaction'][df['Transaction'].apply(lambda x: x < 0)].mean()

    print(df)
    print(total_balance)
    print(average_debit)
    print(average_credit)

    count = df.groupby(['Date']).size().reset_index(name='count')
    count.sort_values('Date')
    transactions_per_month = []
    for i in range(len(count)):
        transactions_per_month.append((datetime.date(1900, count.iloc[i]['Date'], 1).strftime('%B'), count.iloc[i]['count']))

    insert_data_db(df, path_file.split('/')[-1])
    
    return total_balance, average_debit, average_credit, transactions_per_month

def send_result(total_balance, average_debit, average_credit, transactions_per_month):
    sender_email = "egiovanni.vo@gmail.com"
    password = 'xzmoljbjgmxjvrgx'
    receiver_email = "edgarg.vo@gmail.com"

    # Convert transactions per month to HTML row
    transaction_rows_html = ''.join(['<tr style="border: 1px solid;"><td style="border: 1px solid;">{0}</td><td style="border: 1px solid;">{1}</td></tr>'.format(transaction[0], transaction[1]) for transaction in transactions_per_month])

    body = MIMEText(
        """
            <html>
                <body>
                    <h2 style="color:#009F74;text-align:center;">Transactions's Summary</h2>
                    <h3><span style="font-weight: bold;">Total balance:</span> {0}</h3>
                    <h3><span style="font-weight: bold;">Average Debit Amount:</span> {1}</h3>
                    <h3><span style="font-weight: bold;">Average Credit Amount:</span> {2}</h3>

                    <table style="border: 1px solid;">
                        <tr style="border: 1px solid;">
                            <td style="border: 1px solid;">Month</td>
                            <td style="border: 1px solid;">Number of Transactions</td>
                        </tr>
                        {3}
                    </table>

                    <img style="margin-top: 1em;" src="cid:storiLogo">
                </body>
            </html>
        """.format(
                total_balance,
                average_debit,
                average_credit,
                transaction_rows_html,
            ),
        'html'
    )

    message = MIMEMultipart()
    message["Subject"] = "test"
    message["From"] = sender_email
    message["To"] = receiver_email

    message.attach(body)
    
    # Load and attach image
    fp = open('images/stori_logo.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    
    msgImage.add_header('Content-ID', '<storiLogo>')
    message.attach(msgImage)

    # Attach csv file
    with open("data/txns.csv", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment; filename=transactions.csv",
    )
    message.attach(part)

    # Send email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

def init_db():

    conn = psycopg2.connect(
        host='postgresql',
        database="postgres",
        user='postgres',
        password='pass',
        port= '5432'
    )
    cursor = conn.cursor()

    query = '''
        CREATE TABLE IF NOT EXISTS transactions (
            id integer NOT NULL,
            date integer NOT NULL,
            transaction integer NOT NULL,
            file varchar(100) NOT NULL
        )
    '''
    cursor.execute(query)
    conn.commit()
    
    cursor.close()
    conn.close()

def insert_data_db(df, file):
    df['file'] = file

    conn = psycopg2.connect(
        host='postgresql',
        database="postgres",
        user='postgres',
        password='pass',
        port= '5432'
    )
    cursor = conn.cursor()

    data = (
        df['Id'].tolist(),
        df['Date'].tolist(),
        df['Transaction'].tolist(),
        df['file'].tolist()
    )
    for i in range(len(data[0])):
        query = """
        INSERT INTO transactions(id, date, transaction, file) VALUES ({},{},{},'{}');
        """.format(data[0][i], data[1][i], data[2][i], data[3][i])
        cursor.execute(query, data)
        conn.commit()
    cursor.close()

    conn.close()


if __name__ == '__main__':
    sleep(60)
    init_db()

    path_file = 'data/txns.csv'
    total_balance, average_debit, average_credit, transactions_per_month = process_transactions(path_file)
    transaction_rows_html = ''.join(['<tr><td>{0}</td><td>{1}</td></tr>'.format(transaction[0], transaction[1]) for transaction in transactions_per_month])
    send_result(total_balance, average_debit, average_credit, transactions_per_month)
    