import pandas as pd
import datetime

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
for i in range(len(count)):
    print(datetime.date(1900, count.iloc[i]['Date'], 1).strftime('%B'), count.iloc[i]['count'])