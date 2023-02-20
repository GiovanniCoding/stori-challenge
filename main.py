import smtplib
import datetime
import pandas as pd

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def process_transactions(path_file):
    df = pd.read_csv(
        'data/txns.csv',
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
    
    return total_balance, average_debit, average_credit, transactions_per_month

def send_result(total_balance, average_debit, average_credit, transactions_per_month):
    sender_email = "egiovanni.vo@gmail.com"
    password = 'xzmoljbjgmxjvrgx'
    receiver_email = "edgarg.vo@gmail.com"

    # Convert transactions per month to HTML row
    transaction_rows_html = ''.join(['<tr><td>{0}</td><td>{1}</td></tr>'.format(transaction[0], transaction[1]) for transaction in transactions_per_month])

    body = MIMEText(
        """
            <html>
                <body>
                    <h2>Transactions's Summary</h2>
                    <p>Total balance: {0}</p>
                    <p>Average Debit Amount: {1}</p>
                    <p>Average Credit Amount: {2}</p>

                    <table>
                        <tr>
                            <td>Month</td>
                            <td>Number of Transactions</td>
                        </tr>
                        {3}
                    </table>

                    <img src="cid:storiLogo">
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


if __name__ == '__main__':
    path_file = 'data/txns.csv'
    total_balance, average_debit, average_credit, transactions_per_month = process_transactions(path_file)
    transaction_rows_html = ''.join(['<tr><td>{0}</td><td>{1}</td></tr>'.format(transaction[0], transaction[1]) for transaction in transactions_per_month])
    send_result(total_balance, average_debit, average_credit, transactions_per_month)
    