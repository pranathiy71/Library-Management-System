import pandas as pd
import numpy as np

df = pd.read_csv('borrowers.csv')
df1 = pd.read_csv('books.csv',sep='	')

df1.drop('Publisher',axis=1,inplace = True)
df1.dropna(inplace=True)

books = df1[['ISBN13','Title']]
books_table_csv = books.to_csv(r'book_table.csv',index=None,header=False)

Authors = df1[['ISBN13','Author']]

df4 = df1.Author.str.split(',').apply(pd.Series)
df4.index = df1.set_index(['ISBN13', 'Title']).index
df4=df4.stack().reset_index(['ISBN13', 'Title'])
df4.reset_index(inplace=True,drop=True)

df4['Author_Name'] = df4[df4.columns[2]]
Authors = df4['Author_Name'].drop_duplicates()
Authors = Authors.to_frame()
Authors.reset_index(inplace=True,drop=True)
Authors.index +=1
Authors['Author_id'] = Authors.index

cols = list(Authors.columns)
a, b = cols.index('Author_id'), cols.index('Author_Name')
cols[b], cols[a] = cols[a], cols[b]
Authors = Authors[cols]
Authors_table_csv = Authors.to_csv(r'author_table.csv',index=None,header=False)

bf = df4[['ISBN13','Author_Name']]
book_authors = pd.merge(Authors,bf,on='Author_Name', how='outer')
book_authors.drop('Author_Name',axis=1,inplace=True)
book_authors.drop_duplicates(inplace=True)
book_authors_table_csv = book_authors.to_csv(r'book_author_table.csv',index=None,header=False)

df['name'] = df['first_name']+' '+df['last_name']
df['Address'] = df['address']+', '+df['city']+', '+df['state']
df['ID0000id'] = df['ID0000id'].str[2:]
borrower = df[['ID0000id','ssn','name','Address','phone']]
borrower_table_csv = borrower.to_csv(r'borrower_table.csv',index=None,header=False,sep=';')