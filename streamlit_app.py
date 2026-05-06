import streamlit as st
import pandas as pd

st.title("Book Recommender App")

st.write("Upload a CSV file with columns 'user_id' and 'top_10_recommendations' (comma-separated books the user has read).")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("CSV loaded successfully!")
    st.dataframe(df.head())

    num_users = st.number_input("Number of users", min_value=1, max_value=10, value=3, step=1)

    user_books = []
    for i in range(num_users):
        books = st.text_input(f"Enter books you've read for user {i+1} (comma-separated)")
        user_books.append(books)

    if st.button("Get Group Recommendation"):
        new_books_sets = []
        for books_str in user_books:
            entered_set = set(book.strip() for book in books_str.split(',') if book.strip())
            max_overlap = 0
            best_new_books = set()
            for _, row in df.iterrows():
                read_str = row['top_10_recommendations']
                read_set = set(book.strip() for book in read_str.split(',') if book.strip())
                overlap = len(entered_set & read_set)
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_new_books = read_set - entered_set
            if max_overlap > 0:
                new_books_sets.append(best_new_books)
            else:
                st.error(f"No similar users found for books: {books_str}")
                new_books_sets.append(set())

        if new_books_sets and all(s for s in new_books_sets):
            common = set.intersection(*new_books_sets)
            if common:
                st.success("Recommended books for the group:")
                for book in sorted(common):
                    st.write(f"- {book}")
            else:
                st.warning("No common recommended books found for the group.")
        else:
            st.error("Could not find recommendations for all users.")
