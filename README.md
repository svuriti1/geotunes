# GeoTunes

GeoTunes is an interactive web application that allows users to explore music preferences across different countries. By integrating with the Spotify API, GeoTunes provides personalized song recommendations based on a user's listening history and the top charts of the selected country.

## Features

- **Interactive Map**: A world map where users can click on different countries to see the top trending songs.
- **Personalized Recommendations**: Suggests songs based on the user's Spotify top tracks and the audio features of songs popular in the selected country.
- **Spotify Integration**: Direct links to songs on Spotify for easy listening and exploration.

## Libraries and Tools

The following libraries and tools are used in the application:

- **Flask**: A lightweight WSGI web application framework in Python, used to serve the GeoTunes application.
- **Requests**: A simple HTTP library for Python, used to make requests to external APIs like Spotify.
- **Base64**: Used for encoding client credentials in a way that is suitable for HTTP header authorization fields.
- **Pandas**: A data manipulation and analysis library for Python, used to process CSV files containing country-specific song data.
- **NumPy**: A library for the Python programming language, adding support for large, multi-dimensional arrays and matrices.
- **OS and Glob**: Used for file and directory manipulation within the server's file system.

## Requirements

You must have a Spotify account that you have ideally had for a while so we have more detailed information about your listening preferences. You need to have Python 3 and pip installed on your system. To install the necessary Python packages, run:

```bash
pip install Flask requests pandas numpy
```

## Usage
Once you have everything installed, in your terminal simple run:

```bash
flask run
```
Click on the link for the localhost and you're all set! If you are having trouble when clicking on a country on the map, please reach out to us so we can add you as an authorized user for the application.