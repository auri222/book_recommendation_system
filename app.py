#Các thư viện cần thiết
from flask import Flask, render_template, request, url_for
import time
import pandas as pd

app = Flask(__name__)

# Lấy dữ liệu
books = pd.read_csv("https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv")
ratings=pd.read_csv("https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/ratings.csv")

# Lấy danh sách 20 quyển sách đầu của tập dữ liệu books => load lên thẻ select dropdown
ls = books['title'].head(20).tolist()

# Trộn ratings với books dựa trên book_id
books_dt = pd.merge(ratings, books, on='book_id')

# ------------------------------------------------------------------------------
# Xây dựng ma trận đánh giá
# Lấy giá trị trung bình các đánh giá của mỗi quyển sách
ratings_mean_count = pd.DataFrame(books_dt.groupby('title')['rating'].mean())

# Đếm số lượng đánh giá
ratings_mean_count['rating_counts'] = pd.DataFrame(books_dt.groupby('title')['rating'].count())

# Ma trận đánh giá của từng user đối với từng quyển sách
user_book_rating = books_dt.pivot_table(index='user_id',columns='title', values='rating')

# Hàm gợi ý danh sách các sách có độ tương tự cao so với tên sách đã chọn
def pred(book_name, rating_contraint_number, rank):
   book_ratings = user_book_rating[book_name]
   book_like_this_book = user_book_rating.corrwith(book_ratings, method = "pearson")
   corr_book = pd.DataFrame(book_like_this_book,columns=['Correlation'])
   corr_book['rating_counts'] = ratings_mean_count['rating_counts']
   corr_book.dropna(inplace=True)
   lst = corr_book[corr_book['rating_counts']>rating_contraint_number].sort_values('Correlation', ascending=False).head(rank).index.tolist()
   if book_name in lst:
       lst.remove(book_name)
   return lst

@app.route("/")
def Home():
    return render_template('index.html', select_value = ls)

@app.route("/process", methods = ['POST'])
def process():
    if request.method == 'POST':
        text = request.form['book_name']
        if not text:
            error_message = 'Hãy nhập tên sách!'
            return render_template('index.html', error_input=error_message)
        else:
            start_time = time.time()
            ls = pred(text, 100, 10)
            end_time = time.time() - start_time
            return render_template('index.html', value_input=ls, time_input = end_time, title_input = text)

@app.route("/process_select", methods = ['POST'])
def process_select():
    if request.method == 'POST':
        select_book = request.form['sl_book_name']
        if not select_book:
            error_message = 'Hãy chọn sách!'
            return render_template('index.html', error_select=error_message)
        else:
            start_time = time.time()
            lst = pred(select_book,100,10)
            end_time = time.time() - start_time
            return render_template('index.html', value_select=lst, time_select=end_time, title_select = select_book)


if __name__ == '__main__':
    app.run(threaded=True)
