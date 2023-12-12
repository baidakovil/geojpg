"""The program embed gps coordinates from gpx into jpg files on time eq-ty"""

import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Tuple

import piexif


class Cfg:  # pylint: disable=too-few-public-methods
    """
    Class to keep config values.
    """

    minutes_max_jpg_gpx_delta = 15
    meters_coord_bias = 5
    utc_gap = 3
    lat_pattern = r'lat="([0-9]+\.[0-9]+)'
    lon_pattern = r'lon="([0-9]+\.[0-9]+)'
    date_pattern = r'<time>(.*)</time>'
    gpxdate_pattern = '%Y-%m-%dT%H:%M:%S.%fZ'
    exifdate_pattern = '%Y:%m:%d %H:%M:%S'
    gpxfiles_pattern = r'.*\.gpx'
    jpgfiles_pattern = r'.*\.jpg'


def write_exif_gps(folder: str, image_in: str, exif_gps: dict) -> bool:
    """
    Function to write gps coordinates in jpg file.
    Args:
        folder: folder where jpg file stores
        image_in: jpg filename to write
        exif_gps: gps coordinates to write
    Returns:
        True
    """
    jpg_path = folder + image_in
    exif = piexif.load(jpg_path)
    exif['GPS'] = exif_gps
    exif_bytes = piexif.dump(exif)
    piexif.insert(exif_bytes, jpg_path)
    return True


class Point:
    """
    Class to store and compare gpx geopoints.
    """

    def __init__(self, lat: str, lon: str, date: str) -> None:
        self.lat = lat
        self.lon = lon
        self.date = datetime.strptime(date, CFG.gpxdate_pattern) + timedelta(
            hours=CFG.utc_gap
        )

    def __hash__(self) -> int:
        return hash(self.date)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.date == other.date
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.date < other.date
        return False

    def __repr__(self) -> str:
        return 'pnt:' + str(self.date)


def read_gpx(folder: str) -> List[Point]:
    """
    Function to read coordinates and dates from gpx file.
    Args:
        folder: folder where gpx files stores.
    Returns:
        all points from gpx file.
    """
    print('\nRead gpx...', end='')
    gpxfiles = [
        f for f in os.listdir(folder) if re.match(CFG.gpxfiles_pattern, f, re.I)
    ]
    if not gpxfiles:
        print('No gpx files found!')
        return []

    print(f'{len(gpxfiles)} found...', end='')
    points = []
    for gpxfile in gpxfiles:
        with open(folder + gpxfile, encoding='utf-8') as file:
            gpxtext = file.read()
            lats, lons, dates = (
                re.findall(pattern, gpxtext)
                for pattern in (CFG.lat_pattern, CFG.lon_pattern, CFG.date_pattern)
            )
        points += [
            Point(lat=lat, lon=lon, date=date)
            for lat, lon, date in zip(lats, lons, dates)
        ]
    print('ok')
    points_cleaned = list(dict.fromkeys(points))
    print(f'Duplicates removed: {len(points) - len(points_cleaned)}')
    points_sorted = sorted(points_cleaned)
    print(
        f'Got {len(points_sorted)} gps points with dates in local time\n\
FROM: {points_sorted[0].date}\n\
TO  : {points_sorted[-1].date}'
    )
    return points_sorted


def read_jpg(folder: str) -> Tuple[List[datetime], List[str]]:
    """
    Function to read dates from jpg files.
    Args:
        folder: folder where jpgs are stored.
    Returns:
        List of dates, list of filenames
    """
    print('\nRead jpg...', end='')
    jpg_files = sorted(
        [f for f in os.listdir(folder) if re.match(CFG.jpgfiles_pattern, f, re.I)]
    )
    if not jpg_files:
        print('\nNo JPG files in folder!')
        return [], []
    print(f'ok.\nGot {len(jpg_files)} JPG in folder')
    dates_bts = [piexif.load(folder + file)['0th'][306] for file in jpg_files]
    dates = [re.findall(r'b\'(.*)\'', str(date_bts))[0] for date_bts in dates_bts]
    dates = [datetime.strptime(date, CFG.exifdate_pattern) for date in dates]
    dates = sorted(dates)
    print(
        f'Got {len(dates)} timestamps in JPGs\n\
FROM: {(dates)[0]} MSK\n\
TO  : {(dates)[-1]} MSK'
    )
    return dates, jpg_files


def find_coord(
    gpxs: List[Point], jpg_date: datetime
) -> Tuple[str, str, Literal['ok', 'before', 'after']]:
    """
    Gives coordinate point from gpx with nearest to jpg_date date.
    Args:
        gpxs: list of gps points
        jpg_date: date from exif
    Returns:
        lat, lon - coordinates, one of error_types for statistics
    """
    max_delta = timedelta(minutes=CFG.minutes_max_jpg_gpx_delta)
    td = [abs((gpx.date - jpg_date).total_seconds()) for gpx in gpxs]
    closest_point = gpxs[td.index(min(td))]
    date, lat, lon = closest_point.date, closest_point.lat, closest_point.lon
    error_type = 'ok'
    if abs(date - jpg_date) > max_delta:
        lat, lon = '', ''
        error_type = 'before' if jpg_date < date else 'after'
    return lat, lon, error_type


def process_jpg(
    jpg_dates: List[datetime],
    jpg_files: List[str],
    folder: str,
    points: List[Point],
) -> None:
    """
    Function to find nearest coord for every jpg file, insert, save and count.
    Args:
        jpg_dates: dates from jpgs
        jpg_files: list of files
        folder: where stores jpgs
        points: coordinate points from gpx
    """
    after = []
    before = []
    norma = []

    for jpg_date, jpg_file in zip(jpg_dates, jpg_files):
        lat, lon, error_type = find_coord(points, jpg_date)
        if error_type == 'ok':
            exif_gps = format_coord(lat, lon)
            write_exif_gps(folder, jpg_file, exif_gps)
            os.rename(
                folder + jpg_file,
                folder + jpg_file[0:-4] + '_gps' + jpg_file[-4:],
            )
            norma.append(jpg_file)
        elif error_type == 'before':
            before.append(jpg_file)
            exif_gps = 'No gps'
        elif error_type == 'after':
            after.append(jpg_file)
            exif_gps = 'No gps'
        # print(jpg_date, jpg_file, lat, lon, error_type, exif_gps)
    if norma:
        print(f'\nNice. {len(norma)} files updated')
    else:
        print('\nFinished, but no files updated :(')
    if before:
        print(
            f'{len(before)} file(s) not updated, seemed made before tracking:',
            ', '.join(before),
        )
    if after:
        print(
            f'{len(after)} file(s) not updated, seemed made after tracking:',
            ', '.join(after),
        )


def format_coord(lat: str, lon: str) -> Dict[int, Any]:
    """
    Function to reformat coordinates from strings to exif format.
    Args:
        lat, lon: decima floats as strings from gpx
    Returns:
        Dict with keys 1, 2, 3, 4, 31 as special exif fields.
    """

    def decdeg2dms(dd):
        """
        Convert decimal degrees to degrees-minutes-seconds format.
        Args:
            dd: decimal degree value
        Returns:
            degree, minute, second/multiplier, multiplier
        """
        mnt, sec = divmod(abs(dd) * 3600, 60)
        deg, mnt = divmod(mnt, 60)

        result_deg = int(deg)
        result_mnt = int(mnt)
        result_sec = int(str(sec).replace('.', '')[0:4])

        sec_mltpl = int(round(result_sec / sec))
        return result_deg, result_mnt, result_sec, sec_mltpl

    lat_deg, lat_mnt, lat_sec, lat_sec_mltpl = decdeg2dms(float(lat))
    lon_deg, lon_mnt, lon_sec, lon_sec_mltpl = decdeg2dms(float(lon))

    exif_gps: Dict[int, Any] = {1: b'N', 3: b'E'}
    exif_gps[2] = (lat_deg, 1), (lat_mnt, 1), (lat_sec, lat_sec_mltpl)
    exif_gps[4] = (lon_deg, 1), (lon_mnt, 1), (lon_sec, lon_sec_mltpl)
    exif_gps[31] = (CFG.meters_coord_bias, 1)

    return exif_gps


def main(f_jpg, f_gpx) -> None:
    """
    The only function to run.
    """
    print('\nSTART')
    start_time = time.monotonic()

    points = read_gpx(f_gpx)
    if points:
        jpg_dates, jpg_files = read_jpg(f_jpg)
        if jpg_files:
            process_jpg(jpg_dates, jpg_files, f_jpg, points)
    end_time = time.monotonic()
    print(
        f'It took \
{round(timedelta(seconds=end_time - start_time).total_seconds(),2)} seconds'
    )
    print('\nFINISH\n')


base_dir = os.path.dirname(__file__)
folder_jpg = os.path.join(base_dir, './test/9/')
folder_gpx = folder_jpg
CFG = Cfg()

if __name__ == '__main__':
    main(folder_jpg, folder_gpx)
