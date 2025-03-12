from sqlalchemy import select
from flask import request, jsonify, render_template, redirect, url_for, session
from config import app, db, get_user_session, create_user_database, setup_sessions
from helperfunction import add_user_to_database, user_exists, get_user_by_email, is_valid_email, is_valid_name, is_valid_password
from models import Type, Date, Release, Rating, Content, Season, Duration, Cast, Country, Genre, Director, User, DatabaseHandler

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'], user_firstname = session['firstName'].capitalize(), user_lastname = session['lastName'].capitalize())

    else:
        return redirect(url_for('login'))

@app.route('/add_to_collection/<int:show_id>', methods=['POST'])
def add_to_collection(show_id):
    user_session = get_user_session()
    if user_session is None:
        return jsonify({"error": "User session is not available."}), 500

    try:
        content = (
            db.session.query(Content)
            .filter(Content.show_id == show_id)
            .join(Type).join(Release).join(Date).join(Rating)
            .first()
        )

        if not content:
            return jsonify({"error": "Content not found in the collection."}), 404

        if user_session.query(Content).filter_by(show_id=content.show_id).first():
            return jsonify({"message": "Content already exists in the user's collection."}), 200

        new_content = Content(
            show_id=content.show_id,
            title=content.title,
            type_id=content.type_id,
            date_id=content.date_id,
            release_id=content.release_id,
            rating_id=content.rating_id,
            description=content.description
        )
        user_session.add(new_content)

        if not user_session.query(Type).filter_by(type_id=content.type_id).first():
            new_type = Type(type_id=content.type_id, types=content.types.types)
            user_session.add(new_type)

        if not user_session.query(Date).filter_by(date_id=content.date_id).first():
            new_date = Date(date_id=content.date_id, date_added=content.dates.date_added)
            user_session.add(new_date)

        if not user_session.query(Release).filter_by(release_id=content.release_id).first():
            new_release = Release(release_id=content.release_id, release_years=content.releases.release_years)
            user_session.add(new_release)

        if not user_session.query(Rating).filter_by(rating_id=content.rating_id).first():
            new_rating = Rating(rating_id=content.rating_id, ratings=content.ratings.ratings)
            user_session.add(new_rating)

        for cast in content.casts:
            if not user_session.query(Cast).filter_by(show_id=content.show_id, casts=cast.casts).first():
                new_cast = Cast(show_id=content.show_id, casts=cast.casts)
                user_session.add(new_cast)

        for country in content.countries:
            if not user_session.query(Country).filter_by(show_id=content.show_id, countries=country.countries).first():
                new_country = Country(show_id=content.show_id, countries=country.countries)
                user_session.add(new_country)

        for genre in content.genres:
            if not user_session.query(Genre).filter_by(show_id=content.show_id, genres=genre.genres).first():
                new_genre = Genre(show_id=content.show_id, genres=genre.genres)
                user_session.add(new_genre)

        for director in content.directors:
            if not user_session.query(Director).filter_by(show_id=content.show_id, directors=director.directors).first():
                new_director = Director(show_id=content.show_id, directors=director.directors)
                user_session.add(new_director)

        for duration in content.durations:
            if not user_session.query(Duration).filter_by(show_id=content.show_id, duration_minutes=duration.duration_minutes).first():
                new_duration = Duration(show_id=content.show_id, duration_minutes=duration.duration_minutes)
                user_session.add(new_duration)

        for season in content.seasones:
            if not user_session.query(Season).filter_by(show_id=content.show_id, seasons=season.seasons).first():
                new_season = Season(show_id=content.show_id, seasons=season.seasons)
                user_session.add(new_season)

        user_session.commit()
        return jsonify({"message": "Content added to user's collection."}), 200

    except Exception as e:
        user_session.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while adding to collection."}), 500

    finally:
        user_session.close()

@app.route('/remove_from_userCollection/<int:show_id>', methods=['DELETE'])
def remove_from_collection(show_id):
    user_session = get_user_session()
    if user_session is None:
        return jsonify({"error": "User session is not available."}), 500

    try:
        # Fetch the content record and related records
        content = user_session.query(Content).filter(Content.show_id == show_id).first()

        if not content:
            return jsonify({"error": "Content not found."}), 404
        
        # Delete related records in each table
        user_session.query(Cast).filter(Cast.show_id == show_id).delete(synchronize_session='fetch')
        user_session.query(Country).filter(Country.show_id == show_id).delete(synchronize_session='fetch')
        user_session.query(Genre).filter(Genre.show_id == show_id).delete(synchronize_session='fetch')
        user_session.query(Director).filter(Director.show_id == show_id).delete(synchronize_session='fetch')
        user_session.query(Duration).filter(Duration.show_id == show_id).delete(synchronize_session='fetch')
        user_session.query(Season).filter(Season.show_id == show_id).delete(synchronize_session='fetch')

        # Finally, delete the content record
        user_session.delete(content)
        user_session.commit()

        return jsonify({"message": "Content and related records deleted successfully."}), 200

    except Exception as e:
        user_session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        user_session.close()

@app.route('/update_collection', methods=['POST'])
def update_collection():
    user_session = get_user_session()
    if user_session is None:
        return jsonify({"error": "User session is not available."}), 500
    
    movie_subquery = (select(Content.show_id).join(Type).filter(Type.types == 'Movie').limit(500)).subquery()
    tvshow_subquery = (select(Content.show_id).join(Type).filter(Type.types == 'TV Show').limit(500)).subquery()

    movies = (db.session.query(Content).join(Type).filter(Type.types == 'Movie').join(Release).join(Duration).join(Director).join(Genre).join(Date).join(Rating).join(Cast).join(Country).filter(Content.show_id.in_(movie_subquery)).all())
    tv_shows = (db.session.query(Content).join(Type).filter(Type.types == 'TV Show').join(Release).join(Season).join(Director).join(Genre).join(Date).join(Rating).join(Cast).join(Country).filter(Content.show_id.in_(tvshow_subquery)).all())

    movies_data = [movie.to_json() for movie in movies]
    tv_shows_data = [tv_show.to_json() for tv_show in tv_shows]

    User_movies = (user_session.query(Content).join(Type).filter(Type.types == 'Movie').join(Release).join(Duration).join(Director).join(Genre).join(Date).join(Rating).join(Cast).join(Country).filter(Content.show_id.in_(movie_subquery)).all())
    User_tv_shows = (user_session.query(Content).join(Type).filter(Type.types == 'TV Show').join(Release).join(Season).join(Director).join(Genre).join(Date).join(Rating).join(Cast).join(Country).filter(Content.show_id.in_(tvshow_subquery)).all())

    User_movies_data = [movie.to_json() for movie in User_movies]
    User_tv_shows_data = [tv_show.to_json() for tv_show in User_tv_shows]

    return jsonify({'movies': movies_data, 'tv_shows': tv_shows_data, 'userMovies': User_movies_data, 'userTv_shows': User_tv_shows_data})

@app.route('/update_progress/<int:show_id>', methods=['PUT'])
def update_progress(show_id):
    user_session = get_user_session()
    if user_session is None:
        return jsonify({"error": "User session is not available."}), 500
    try:
        # Fetch the content record for the current user
        content = user_session.query(Content).filter(Content.show_id == show_id).first()
        
        if content:
            # Update progress (cycle between 0, 1, 2)
            content.progress = (content.progress + 1) % 3
            user_session.commit()
            return jsonify({"new_progress": content.progress}), 200
        else:
            return jsonify({"error": "Content not found."}), 404
    except Exception as e:
        user_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        user_session.close()

@app.route('/total_progress', methods=['GET'])
def total_progress():
    user_session = get_user_session()
    if user_session is None:
        return jsonify({"error": "User session is not available."}), 500

    try:
        # Get all movies for the user
        movies = user_session.query(Content).join(Type).filter(Type.types == 'Movie').all()
        tv_shows = user_session.query(Content).join(Type).filter(Type.types == 'TV Show').all()
        
        if not movies:
            return jsonify({"movietotal_progress": 0}), 200
        
        if not tv_shows:
            return jsonify({"tvshowtotal_progress": 0}), 200
    
        # Calculate the total progress as a percentage
        movietotal_progress = sum(movie.progress / 2 for movie in movies) / len(movies) * 100
        tvshowtotal_progress = sum(tv_show.progress / 2 for tv_show in tv_shows) / len(tv_shows) * 100
        return jsonify({"movietotal_progress": movietotal_progress, "tvshowtotal_progress": tvshowtotal_progress}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        user_session.close()

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if user_exists(email, password):
            user = get_user_by_email(email)
            session['id'] = user.user_id
            session['firstName'] = user.first_name
            session['lastName'] = user.last_name
            session['user'] = email
            setup_sessions(session['id'])
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login', error='Login failed. Please try again.'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        if not is_valid_name(first_name) or not is_valid_name(last_name):
            return redirect(url_for('register', error='Invalid name. Please use alphabetic characters only.'))

        if not is_valid_email(email):
            return redirect(url_for('register', error='Invalid email format.'))

        if not is_valid_password(password):
            return redirect(url_for('register', error='Password must be at least 16 characters.'))

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = add_user_to_database(first_name, last_name, email, password)

            create_user_database(new_user.user_id)

            return redirect(url_for('login'))
        else:
            return redirect(url_for('register', error='User already exists.'))

    return render_template('register.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db_handler = DatabaseHandler()
        db_handler.setup_database()
    app.run(debug=True)