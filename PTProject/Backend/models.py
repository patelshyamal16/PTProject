import sqlite3
import pandas as pd
from config import db
from datetime import datetime, date

class Type(db.Model):
    __tablename__ = 'type'
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    types = db.Column(db.String(50), unique=True, nullable=False)

    content = db.relationship('Content', backref='types', lazy=True)

class Date(db.Model):
    __tablename__ = 'date'
    date_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_added = db.Column(db.Date, unique=True, nullable=False)

    content = db.relationship('Content', backref='dates', lazy=True)

class Release(db.Model):
    __tablename__ = 'release'
    release_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    release_years = db.Column(db.Integer, unique=True, nullable=False)

    content = db.relationship('Content', backref='releases', lazy=True)

class Rating(db.Model):
    __tablename__ = 'rating'
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ratings = db.Column(db.String(10), unique=True, nullable=False)

    content = db.relationship('Content', backref='ratings', lazy=True)

class Content(db.Model):
    __tablename__ = 'content'
    show_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type.type_id'), nullable=True)
    date_id = db.Column(db.Integer, db.ForeignKey('date.date_id'), nullable=True)
    release_id = db.Column(db.Integer, db.ForeignKey('release.release_id'), nullable=True)
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.rating_id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    progress = db.Column(db.Integer, default = 0, nullable=True)


    casts = db.relationship('Cast', backref='content', lazy=True)
    countries = db.relationship('Country', backref='content', lazy=True)
    genres = db.relationship('Genre', backref='content', lazy=True)
    directors = db.relationship('Director', backref='content', lazy=True)
    durations = db.relationship('Duration', backref='content', lazy=True)
    seasones = db.relationship('Season', backref='content', lazy=True)

    def to_json(self):
        return {
            "show_id": self.show_id,
            "title": self.title,
            "dateAdded": self.dates.date_added if self.dates else None,
            "releaseYear": self.releases.release_years if self.releases else None,
            "rating": self.ratings.ratings if self.ratings else None,
            "description": self.description,
            "progress": self.progress,
            "type": self.types.types if self.types else None,
            "cast": [cast.casts for cast in self.casts],
            "country": [country.countries for country in self.countries],
            "genre": [genre.genres for genre in self.genres],
            "director": [director.directors for director in self.directors],
            "duration": self.durations[0].duration_minutes if self.types.types == "Movie" and self.durations else None,
            "season": self.seasones[0].seasons if self.types.types == "TV Show" and self.seasones else None,
        }

class Season(db.Model):
    __tablename__ = 'season'
    season_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('content.show_id'), nullable=False)
    seasons = db.Column(db.Integer, nullable=False)

class Duration(db.Model):
    __tablename__ = 'duration'
    duration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('content.show_id'), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)

class Cast(db.Model):
    __tablename__ = 'cast'
    cast_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('content.show_id'), nullable=False)
    casts = db.Column(db.String(255), nullable=False)

class Country(db.Model):
    __tablename__ = 'country'
    country_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('content.show_id'), nullable=False)
    countries = db.Column(db.String(255), nullable=False)

class Genre(db.Model):
    __tablename__ = 'genre'
    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('content.show_id'), nullable=False)
    genres = db.Column(db.String(100), nullable=False)

class Director(db.Model):
    __tablename__ = 'director'
    director_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('content.show_id'), nullable=False)
    directors = db.Column(db.String(255), nullable=False)

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            "userId": self.user_id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "joinDate": self.join_date,
        }

class DatabaseHandler:
    def __init__(self, db_name='Database/Collection.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_status_table()

    def setup_status_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS setup_status (
                                id INTEGER PRIMARY KEY, 
                                setup_done BOOLEAN)''')
        self.conn.commit()

    def create_table(self, table_name, create_statement):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if not self.cursor.fetchone():
            self.cursor.execute(create_statement)
            print(f"{table_name} table created.")

    def setup_database(self):
        self.cursor.execute("SELECT setup_done FROM setup_status WHERE id = 1")
        setup_status = self.cursor.fetchone()

        if setup_status and setup_status[0]:
            print("Database setup has already been completed.")
            return
        
        tables = [
            ("type", """CREATE TABLE IF NOT EXISTS type(
                type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                types TEXT UNIQUE NOT NULL)"""),
            ("date", """CREATE TABLE IF NOT EXISTS date(
                date_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_added DATE UNIQUE NOT NULL)"""),
            ("release", """CREATE TABLE IF NOT EXISTS release(
                release_id INTEGER PRIMARY KEY AUTOINCREMENT,
                release_years INTEGER UNIQUE NOT NULL)"""),
            ("rating", """CREATE TABLE IF NOT EXISTS rating(
                rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ratings TEXT UNIQUE NOT NULL)"""),
            ("content", """CREATE TABLE IF NOT EXISTS content(
                show_id INTEGER PRIMARY KEY NOT NULL,
                type_id INTEGER NOT NULL,
                date_id INTEGER NOT NULL,
                release_id INTEGER NOT NULL,
                rating_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                progress INTEGER NOT NULL,
                FOREIGN KEY (type_id) REFERENCES type(type_id),
                FOREIGN KEY (date_id) REFERENCES date(date_id),
                FOREIGN KEY (release_id) REFERENCES release(release_id),
                FOREIGN KEY (rating_id) REFERENCES rating(rating_id))"""),
            ("season", """CREATE TABLE IF NOT EXISTS season(
                season_id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER NOT NULL,
                seasons INTEGER NOT NULL,
                FOREIGN KEY (show_id) REFERENCES content(show_id))"""),
            ("duration", """CREATE TABLE IF NOT EXISTS duration(
                duration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER NOT NULL,
                duration_minutes INTEGER NOT NULL,
                FOREIGN KEY (show_id) REFERENCES content(show_id))"""),
            ("cast", """CREATE TABLE IF NOT EXISTS cast(
                cast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER NOT NULL,
                casts TEXT NOT NULL,
                FOREIGN KEY (show_id) REFERENCES content(show_id))"""),
            ("country", """CREATE TABLE IF NOT EXISTS country(
                country_id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER NOT NULL,
                countries TEXT NOT NULL,
                FOREIGN KEY (show_id) REFERENCES content(show_id))"""),
            ("genre", """CREATE TABLE IF NOT EXISTS genre(
                genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER NOT NULL,
                genres TEXT NOT NULL,
                FOREIGN KEY (show_id) REFERENCES content(show_id))"""),
            ("director", """CREATE TABLE IF NOT EXISTS director(
                director_id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER NOT NULL,
                directors TEXT NOT NULL,
                FOREIGN KEY (show_id) REFERENCES content(show_id))"""),
            ("user", """CREATE TABLE IF NOT EXISTS user(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""),
        ]

        for table_name, create_statement in tables:
            self.create_table(table_name, create_statement)

        self.load_data()

        self.cursor.execute("INSERT OR REPLACE INTO setup_status (id, setup_done) VALUES (1, TRUE)")
        self.conn.commit()
        self.close()
        print("Database setup completed successfully.")

    def clean_data(self, df):
        df.fillna("Not Available", inplace=True)
        
        if 'listed_in' in df.columns:
            df.rename(columns={'listed_in': 'genre'}, inplace=True)

        if 'rating' in df.columns:
            df.loc[df['title'] == '13TH: A Conversation with Oprah Winfrey & Ava DuVernay', 'rating'] = 'TV-PG'
            df.loc[df['title'] == 'Gargantia on the Verdurous Planet', 'rating'] = 'TV-14'
            df.loc[df['title'] == 'Little Lunch', 'rating'] = 'TV-G'
            df.loc[df['title'] == 'My Honor Was Loyalty', 'rating'] = 'PG-13'
        
        today_date = date.today()
        
        contains_not_available = (df['date_added'] == 'Not Available').any()
        contains_invalid_dates = df['date_added'].apply(lambda x: pd.to_datetime(x, errors='coerce')).isna().any()

        if contains_not_available or contains_invalid_dates:
            df['date_added'] = df['date_added'].apply(lambda x: today_date if x == 'Not Available' 
                                          else pd.to_datetime(x.strip(), format='%B %d, %Y', errors='coerce').date())
        
        if 'duration' in df.columns:
            if df['duration'].apply(lambda x: isinstance(x, str)).all():
                df['duration'] = df['duration'].str.replace(' min', '', regex=False)
                df['duration'] = df['duration'].str.replace(' Seasons', '', regex=False)
                df['duration'] = df['duration'].str.replace(' Season', '', regex=False)
        
                df.loc[df['duration'] == 'Not Available', 'duration'] = df['rating'].str.replace(' min', '', regex=False)
        
        if 'show_id' in df.columns:
            if df['show_id'].apply(lambda x: isinstance(x, str)).all():
                df['show_id'] = df['show_id'].str.replace('s', '', regex=False)

        return df

    def insert_data(self, df):
        for _, row in df.iterrows():
            type_obj = Type.query.filter_by(types=row['type']).first()
            if not type_obj:
                type_obj = Type(types=row['type'])
                db.session.add(type_obj)
                db.session.flush()

            date_obj = Date.query.filter_by(date_added=row['date_added']).first()
            if not date_obj:
                date_obj = Date(date_added=row['date_added'])
                db.session.add(date_obj)
                db.session.flush()

            release_obj = Release.query.filter_by(release_years=row['release_year']).first()
            if not release_obj:
                release_obj = Release(release_years=row['release_year'])
                db.session.add(release_obj)
                db.session.flush()

            rating_obj = Rating.query.filter_by(ratings=row['rating']).first()
            if not rating_obj:
                rating_obj = Rating(ratings=row['rating'])
                db.session.add(rating_obj)
                db.session.flush()

            content = Content(
                show_id=row['show_id'],
                type_id=type_obj.type_id,
                date_id=date_obj.date_id,
                release_id=release_obj.release_id,
                rating_id=rating_obj.rating_id,
                title=row['title'],
                description=row['description']
            )
            db.session.add(content)

            if type_obj.type_id == 1:
                duration = Duration(show_id=row['show_id'], duration_minutes=row['duration'])
                db.session.add(duration)
            else:
                season = Season(show_id=row['show_id'], seasons=row['duration'])
                db.session.add(season)

            for cast_member in row['cast'].split(','):
                cast_entry = Cast(show_id=row['show_id'], casts=cast_member.strip())
                db.session.add(cast_entry)

            for country in row['country'].split(','):
                country_entry = Country(show_id=row['show_id'], countries=country.strip())
                db.session.add(country_entry)

            for genre in row['genre'].split(','):
                genre_entry = Genre(show_id=row['show_id'], genres=genre.strip())
                db.session.add(genre_entry)

            for director in row['director'].split(','):
                director_entry = Director(show_id=row['show_id'], directors=director.strip())
                db.session.add(director_entry)

        db.session.commit()
        print("Content data inserted successfully into all tables.")

    def load_data(self):
        df = pd.read_csv('netflix_titles.csv')
        df = self.clean_data(df)
        self.insert_data(df)

    def close(self):
        self.conn.close()