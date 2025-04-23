import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import time
import requests

# Page config
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size:3rem !important;
        color:#1E3A8A;
        font-weight:700;
        margin-bottom:1rem;
        text-align:center;
        text-shadow:2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size:1.8rem !important;
        color:#3B82F6;
        font-weight:600;
        margin-top:1rem;
        margin-bottom:1rem;
    }
    .success-message {
        padding:1rem;
        background-color:#ECFDF5;
        border-left:5px solid #10B981;
        border-radius:0.375rem;
    }
    .warning-message {
        padding:1rem;
        background-color:#FEF3C7;
        border-left:5px solid #F59E0B;
        border-radius:0.375rem;
    }
    .book-card {
        background-color:#F3F4F6;
        border-radius:0.5rem;
        padding:1rem;
        margin-bottom:1rem;
        border-left:5px solid #3B82F6;
    }
    .read-badge {
        background-color: #10B981;
        color:white;
        padding:0.25rem 0.75rem;
        border-radius:1rem;
        font-size:0.875rem;
        font-weight:600;
    }
    .unread-badge {
        background-color:#F87171;
        color:white;
        padding:0.25rem 0.75rem;
        border-radius:1rem;
        font-size:0.875rem;
        font-weight:600;
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Session state init
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load/save library

def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as f:
            st.session_state.library = json.load(f)

def save_library():
    with open('library.json', 'w') as f:
        json.dump(st.session_state.library, f)

# Book ops

def add_book(title, author, year, genre, read):
    book = {
        'title': title,
        'author': author,
        'publication_year': year,
        'genre': genre,
        'read_status': read
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True

# Search

def search_books(term, by):
    term = term.lower()
    st.session_state.search_results = [
        b for b in st.session_state.library
        if term in b[by.lower()].lower()
    ]

# Stats

def get_library_stats():
    total = len(st.session_state.library)
    read = sum(1 for b in st.session_state.library if b['read_status'])
    percent = (read / total * 100) if total > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for b in st.session_state.library:
        genres[b['genre']] = genres.get(b['genre'], 0) + 1
        authors[b['author']] = authors.get(b['author'], 0) + 1
        decade = (b['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total,
        'read_books': read,
        'percent_read': percent,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Charts

def create_visualizations(stats):
    if stats['total_books'] > 0:
        fig_read = go.Figure(data=[
            go.Pie(labels=['Read', 'Unread'],
                   values=[stats['read_books'], stats['total_books'] - stats['read_books']],
                   hole=0.4,
                   marker_colors=['#10B981', '#F87171'])
        ])
        fig_read.update_layout(title="Read vs Unread")
        st.plotly_chart(fig_read, use_container_width=True)

    if stats['genres']:
        df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig = px.bar(df, x='Genre', y='Count', color='Count', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    if stats['decades']:
        df = pd.DataFrame({
            'Decade': [f"{d}s" for d in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig = px.line(df, x='Decade', y='Count', markers=True)
        st.plotly_chart(fig, use_container_width=True)

# Load existing data
load_library()

# Sidebar Nav
lottie_book = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_m9tFNm.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200)

nav = st.sidebar.radio("Navigate", ["View Library", "Add Book", "Search Books", "Library Statistics"])

if nav == "View Library":
    st.session_state.current_view = "library"
elif nav == "Add Book":
    st.session_state.current_view = "add"
elif nav == "Search Books":
    st.session_state.current_view = "search"
elif nav == "Library Statistics":
    st.session_state.current_view = "stats"

# Main title
st.markdown("<h1 class='main-header'>Personal Library Manager</h1>", unsafe_allow_html=True)

# View Rendering
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title")
            author = st.text_input("Author")
            year = st.number_input("Year", 1000, datetime.now().year, step=1, value=2023)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Tech", "Fantasy", "Romance", "Poetry", "Religious", "Art", "Other"])
            read = st.radio("Read?", ["Read", "Unread"])
            read_status = read == "Read"

        if st.form_submit_button("Add Book"):
            if title and author:
                add_book(title, author, year, genre, read_status)

    if st.session_state.book_added:
        st.success("Book added successfully!")
        st.balloons()
        st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books!")
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        remove_book(i)
                        st.rerun()
                with col2:
                    label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                    if st.button(label, key=f"toggle_{i}"):
                        st.session_state.library[i]['read_status'] = not book['read_status']
                        save_library()
                        st.rerun()

elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search by", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term")

    if st.button("Search") and search_term:
        with st.spinner("Searching..."):
            time.sleep(0.5)
            search_books(search_term, search_by)

    if st.session_state.search_results:
        for book in st.session_state.search_results:
            st.markdown(f"""
            <div class='book-card'>
                <h3>{book['title']}</h3>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Year:</strong> {book['publication_year']}</p>
                <p><strong>Genre:</strong> {book['genre']}</p>
                <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
            </div>
            """, unsafe_allow_html=True)
    elif search_term:
        st.warning("No results found.")

elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.warning("No books to analyze.")
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", stats['total_books'])
        col2.metric("Books Read", stats['read_books'])
        col3.metric("% Read", f"{stats['percent_read']:.1f}%")
        create_visualizations(stats)

st.markdown("---")
st.markdown("© 2025 Sobia Naz - Personal Library Manager", unsafe_allow_html=True)
