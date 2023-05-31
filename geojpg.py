import pandas as pd
import piexif
from PIL import Image
import re
import os
import datetime
from datetime import timedelta


def write_exif_gps(folder, image_in, exif_gps):

    # function to write gps coordinates in jpg file

    jpg_path = folder + image_in
    exif = piexif.load(jpg_path)
    exif['GPS'] = exif_gps
    exif_bytes = piexif.dump(exif)
    piexif.insert(exif_bytes, jpg_path)

    return True


def read_gpx(folder):

    # function to read coordinates and dates from gpx

    gpxfiles = [f for f in os.listdir(folder) if re.match(r'.*\.gpx', f)]
    if len(gpxfiles) > 1:
        print('There is more than one GPX file in folder! ')
        return False
    gpx = open(folder + gpxfiles[0]).read()
    
    lat_pattern = r'lat="([0-9]+\.[0-9]+)'
    lon_pattern = r'lon="([0-9]+\.[0-9]+)'
    date_pattern = r'<time>(.*)</time>'
    lats = re.findall(lat_pattern, gpx)
    lons = re.findall(lon_pattern, gpx)
    dates = re.findall(date_pattern, gpx)
    
    df_gpx = pd.DataFrame({'lats':lats,'lons':lons,'dates':dates})

    df_gpx['dates'] = pd.to_datetime(df_gpx['dates'])
    df_gpx['dates'] = df_gpx['dates'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))   
    df_gpx['dates'] = pd.to_datetime(df_gpx['dates'])
    df_gpx['dates'] = df_gpx['dates'].apply(lambda x: x+timedelta(hours=3))
    df_gpx = df_gpx.drop_duplicates(subset=['dates'])
    df_gpx = df_gpx.reset_index()
    df_gpx = df_gpx.sort_values(by='dates')

    first_date = df_gpx['dates'].iloc[0]
    last_date =  df_gpx['dates'].iloc[-1]

    print(f'Got {len(df_gpx)} gps points with dates from   {first_date}MSK   to   {last_date}MSK')
    
    return df_gpx


def read_jpg(folder):

    # function to read dates from jpg files

    jpg_files = sorted([f for f in os.listdir(folder) if re.match(r'.*\.JPG', f)])

    if len(jpg_files) == 0:
        print('No JPG files in folder!')
    else: 
        print(f'Got {len(jpg_files)} JPG in folder')

    dates_bytes = [piexif.load(folder + file)['0th'][306] for file in jpg_files]
    dates = [re.findall(r'b\'(.*)\'', str(date_bytes))[0].replace(':','-',2) for date_bytes in dates_bytes]
    dates = pd.to_datetime(dates)

    first_date = sorted(dates)[0]
    last_date = sorted(dates)[-1]

    print(f'Got {len(dates)} dates in JPGs from   {first_date}MSK   to   {last_date}MSK')

    return dates, jpg_files


def find_coord(df_gpx,jpg_date):

    # function to search nearest coordinates in gpx

    max_delta = timedelta(minutes = 15)
    closest_index = df_gpx['dates'].searchsorted(jpg_date)

    if closest_index == len(df_gpx):
        closest_index = closest_index - 1

    closest = df_gpx.iloc[closest_index]
    date_gpx = closest['dates']

    max_delta = timedelta(minutes = 15)

    error_type = 'ok'

    if jpg_date < date_gpx:
        delta = date_gpx - jpg_date
        if delta > max_delta:
            # print('Photo made before gpx, delta is more than 15 minutes')
            lat = ''
            lon = ''
            error_type = 'before'
            return lat, lon, error_type
    else:
        delta = jpg_date - date_gpx
        if delta > max_delta:
            # print('Photo made after gpx, delta is more than 15 minutes')
            lat = ''
            lon = ''
            error_type = 'after'
            return lat, lon, error_type

    lat = closest['lats']
    lon = closest['lons']

    return lat, lon, error_type


def process_jpg(jpg_dates, jpg_files, folder_jpg, df_gpx):

    # function to process all jpg files and count errors

    after = []
    before = []
    norma = []

    for jpg_date, jpg_file in zip(jpg_dates, jpg_files):

        lat, lon, error_type =  find_coord(df_gpx, jpg_date)

        if error_type == 'ok':
            exif_gps = format_coord(lat, lon)
            write_exif_gps(folder_jpg, jpg_file, exif_gps)
            os.rename(folder_jpg + jpg_file, folder_jpg + jpg_file[0:-4] + '_gps' + jpg_file[-4:])
            norma.append(jpg_file)
        elif error_type == 'before':
            before.append(jpg_file)
            exif_gps = 'No gps'
        elif error_type == 'after':
            after.append(jpg_file)
            exif_gps = 'No gps'

        # print(jpg_date, jpg_file, lat, lon, error_type, exif_gps)

    if len(norma) > 0:
        print(f'Finished. {len(norma)} files updated')
    else:
        print(f'Finished, but no files updated :(')

    if len(before) > 0:
        print(f'{len(before)} file(s) not updated, seemed made before tracking:',', '.join(before))

    if len(after) > 0:
        print(f'{len(after)} file(s) not updated, seemed made after tracking:',', '.join(after))

    return True


def format_coord(lat, lon):

    # function to convert decimal coordinates to degree-minutes-seconds coordinates

    def decdeg2dms(dd):

        mnt,sec = divmod(abs(dd)*3600, 60)
        deg,mnt = divmod(mnt, 60)

        return int(deg), int(mnt), int(str(sec).replace('.','')[0:4])
    
    lat_deg, lat_mnt, lat_sec = decdeg2dms(float(lat))
    lon_deg, lon_mnt, lon_sec = decdeg2dms(float(lon))


    exif_gps = {    1: b'N',
                    3: b'E'}
    exif_gps[2] = ((int(lat_deg), 1), (int(lat_mnt), 1), (int(lat_sec), 100))
    exif_gps[4] = ((int(lon_deg), 1), (int(lon_mnt), 1), (int(lon_sec), 100))

    return exif_gps


def main():
    
    df_gpx = read_gpx(folder_gpx)
    jpg_dates, jpg_files = read_jpg(folder_jpg)
    process_jpg(jpg_dates, jpg_files, folder_jpg, df_gpx)

    return True


base_dir = os.path.dirname(__file__)
folder_jpg = os.path.join(base_dir, './')
folder_gpx = os.path.join(base_dir, './')
main()
