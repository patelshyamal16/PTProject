# Pre-Progress Tracker (PPT)

## Developed by: Shyamal Patel  
## Course: Cognixia Future Horizon

### Getting Started
After downloading the project, delete Collection.db to recreate it. I kept it in GitHub to retain the Database folder.

To run the project:

1. Open your terminal and navigate to the **Backend** folder.
2. Execute the following command:  
   ```bash
   python app.py```
3. Open the  browser and navigate to `http://127.0.0.1:5000/` to  access the application.


### User Instructions

### 1. Create an Account
Sign up to log in and start tracking your content.

### 2. Loading Time
Please be patient; loading data from the Collection database may take a few seconds.

### 3. Dashboard Information
After logging in, check the side panel for helpful information about your collection.

### 4. Display Limit for Faster Loading
The dashboard query is limited to displaying 500 items to improve loading speed.  
If you want to view the entire Collection database:

1. Go to the `Backend` folder and open `app.py`.
2. Scroll to the `update_collection` function.
3. Modify the following lines to adjust the display limit:
   ```python
   movie_subquery = (select(Content.show_id).join(Type).filter(Type.types == 'Movie').limit(500)).subquery()
   tvshow_subquery = (select(Content.show_id).join(Type).filter(Type.types == 'TV Show').limit(500)).subquery()```

### Acknowledgments

Thank you for the opportunity to tackle and improve my skills with this project.

### Future Goals

My next goal is to optimize the rendering speed and enhance the user interface using React.
