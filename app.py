#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import datetime
import os
import sys
from click import edit
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate=Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
      return f'< Venue name:{self.name} genres:{self.genres} >'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, nullable=False)
  venue_id = db.Column(db.Integer, nullable=False)
  start_time = db.Column(db.DateTime(), default=datetime.now())
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  venue_areas = db.session.query(Venue.city, Venue.state).distinct().all()
  for area in venue_areas:
    body={}
    body['city'] = area[0]
    body['state'] = area[1]

    # categorized venues
    cat_venues = Venue.query.filter_by(city=area[0], state=area[1]).all()
    venues=[]
    for venue in cat_venues:
      venue_detail={}
      venue_detail['id']=venue.id
      venue_detail['name']=venue.name
      num_of_upcoming_shows = Show.query.filter_by(venue_id=venue.id).count()
      venue_detail['num_upcoming_shows']=num_of_upcoming_shows
      venues+=[venue_detail]
    body['venues'] = venues
    data+=[body]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  search_result = Venue.query.filter(Venue.name.ilike(f"%{search_term}%"))
  venues=search_result.all()
  count=search_result.count()
  response={}
  response['count']=count
  data=[]
  for venue in venues:
    body={}
    body['id']=venue.id
    body['name']=venue.name
    num_upcoming_show=Show.query.filter(Show.venue_id==venue.id, Show.start_time>datetime.now()).count()
    body['num_upcoming_show']=num_upcoming_show
    data+=[body]
  response['data']=data

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id) 
  data = {}
  data['id']=venue.id
  data['name']=venue.name
  data['genres']=venue.genres
  data['address']=venue.address
  data['city']=venue.city
  data['state']=venue.state
  data['phone']=venue.phone
  data['website']=venue.website_link
  data['facebook_link']=venue.facebook_link
  data['seeking_talent']=venue.seeking_talent
  data['seeking_description']=venue.seeking_description
  data['image_link']=venue.image_link

  shows = Show.query.filter_by(venue_id=venue_id).all()
  past_shows=[]
  upcoming_shows=[]
  
  for show in shows:
    artist_id = show.artist_id
    body={}
    artist = Artist.query.get(artist_id)
    body['artist_id']=artist.id
    body['artist_name']=artist.name
    body['artist_image_link']=artist.image_link
    show_start_time = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    body['start_time']=show_start_time
    now = datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    if show_start_time<time:
      past_shows+=[body]
    else:
      upcoming_shows+=[body]  
  data['past_shows']=past_shows
  data['upcoming_shows']=upcoming_shows
  data['past_shows_count']=len(past_shows)
  data['upcoming_shows_count']=len(upcoming_shows)

  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  try:
    seeking_talent=False
    if request.form['seeking_talent']=='y':
      seeking_talent=True
    
    venue = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      genres=request.form['genres'],
      address=request.form['address'],
      phone=request.form['phone'],
      website_link=request.form['website_link'],
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      seeking_talent=seeking_talent,
      seeking_description=request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')    
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  print('deleting venue',venue_id)
  error=False
  name=''
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    shows = Show.query.filter_by(venue_id=venue.id)
    for show in shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred. Venue ' + name + ' could not be deleted.')
    else:
      flash('Venue ' + name + ' was successfully deleted.')
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data=[]
  for artist in artists:
    body={}
    body['id']=artist.id
    body['name']=artist.name
    data+=[body]
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')
  search_result = Artist.query.filter(Artist.name.ilike(f"%{search_term}%"))
  artists=search_result.all()
  count=search_result.count()
  response={}
  response['count']=count
  data=[]
  for artist in artists:
    body={}
    body['id']=artist.id
    body['name']=artist.name
    num_upcoming_show=Show.query.filter(Show.artist_id==artist.id, Show.start_time>datetime.now()).count()
    body['num_upcoming_show']=num_upcoming_show
    data+=[body]
  response['data']=data
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id) 
  data = {}
  data['id']=artist.id
  data['name']=artist.name
  data['genres']=artist.genres
  data['city']=artist.city
  data['state']=artist.state
  data['phone']=artist.phone
  data['website']=artist.website_link
  data['facebook_link']=artist.facebook_link
  data['seeking_venue']=artist.seeking_venue
  data['seeking_description']=artist.seeking_description
  data['image_link']=artist.image_link

  shows = Show.query.filter_by(artist_id=artist_id).all()
  past_shows=[]
  upcoming_shows=[]
  
  for show in shows:
    venue_id = show.venue_id
    body={}
    venue = Venue.query.get(venue_id)
    body['venue_id']=venue.id
    body['venue_name']=venue.name
    body['venue_image_link']=venue.image_link
    show_start_time = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    body['start_time']=show_start_time
    now = datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    if show_start_time<time:
      past_shows+=[body]
    else:
      upcoming_shows+=[body]  
  data['past_shows']=past_shows
  data['upcoming_shows']=upcoming_shows
  data['past_shows_count']=len(past_shows)
  data['upcoming_shows_count']=len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  edit_artist = Artist.query.get(artist_id)
  artist={
    "id": edit_artist.id,
    "name": edit_artist.name,
    "genres": edit_artist.genres,
    "city": edit_artist.city,
    "state": edit_artist.state,
    "phone": edit_artist.phone,
    "website_link": edit_artist.website_link,
    "facebook_link": edit_artist.facebook_link,
    "seeking_venue": edit_artist.seeking_venue,
    "seeking_description": edit_artist.seeking_description,
    "image_link": edit_artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    seeking=False
    if request.form['seeking_venue']=='y':
      seeking=True
    artist = Artist.query.get(artist_id)
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.genres=request.form['genres']
    artist.phone=request.form['phone']
    artist.website_link=request.form['website_link']
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link']
    artist.seeking_venue=seeking
    artist.seeking_description=request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')    
    else:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  edit_venue = Venue.query.get(venue_id)
  venue={
    "id": edit_venue.id,
    "name": edit_venue.name,
    "genres": edit_venue.genres,
    "address": edit_venue.address,
    "city": edit_venue.city,
    "state": edit_venue.state,
    "phone": edit_venue.phone,
    "website": edit_venue.website_link,
    "facebook_link": edit_venue.facebook_link,
    "seeking_talent": edit_venue.seeking_talent,
    "seeking_description": edit_venue.seeking_description,
    "image_link": edit_venue.image_link
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    seeking=False
    if request.form['seeking_talent']=='y':
      seeking=True
    venue = Venue.query.get(venue_id)
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.state=request.form['state']
    venue.address=request.form['address']
    venue.genres=request.form['genres']
    venue.phone=request.form['phone']
    venue.website_link=request.form['website_link']
    venue.image_link=request.form['image_link']
    venue.facebook_link=request.form['facebook_link']
    venue.seeking_talent=seeking
    venue.seeking_description=request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')    
    else:
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    seeking_venue=False
    if request.form['seeking_venue']=='y':
      seeking_venue=True
    artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      genres=request.form['genres'],
      phone=request.form['phone'],
      website_link=request.form['website_link'],
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      seeking_venue=seeking_venue,
      seeking_description=request.form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')    
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data=[]
  for show in shows:
    venue=Venue.query.get(show.venue_id)
    artist=Artist.query.get(show.artist_id)
    body={}
    body['venue_id']=venue.id
    body['venue_name']=venue.name
    body['artist_id']=artist.id
    body['artist_name']=artist.name
    body['artist_image_link']=artist.image_link
    body['start_time']=show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    data+=[body]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occured. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
    return render_template('pages/home.html')
    

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    app.debug = True

