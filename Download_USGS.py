import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union

def download_usgs_earthquakes(
    min_latitude: float,
    max_latitude: float,
    min_longitude: float,
    max_longitude: float,
    start_time: Union[str, datetime],
    end_time: Union[str, datetime],
    min_magnitude: float = 0.0,
    max_magnitude: Optional[float] = None,
    proxy: Optional[dict] = None,
    chunk_days: int = 365,
    max_events_per_chunk: int = 20000,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Download earthquake events from USGS FDSN event API for a specified region and time range.
    
    Parameters
    ----------
    min_latitude, max_latitude : float
        Southern and northern bounds of the region.
    min_longitude, max_longitude : float
        Western and eastern bounds.
    start_time, end_time : str or datetime
        Time range (UTC). Strings should be ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).
    min_magnitude : float, default 0.0
        Minimum magnitude to include.
    max_magnitude : float, optional
        Maximum magnitude to include (exclusive if using USGS 'maxmagnitude' parameter).
    proxy : dict, optional
        Proxy configuration for requests, e.g. {'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}.
    chunk_days : int, default 365
        Length of each time window in days (to stay under the 20k event limit).
    max_events_per_chunk : int, default 20000
        Maximum events to request per query (USGS limit is 20000).
    verbose : bool, default True
        Print progress information.
    
    Returns
    -------
    pd.DataFrame
        Columns: 'time' (datetime), 'latitude', 'longitude', 'depth' (km), 'mag'
    """
    # Convert string dates to datetime if needed
    if isinstance(start_time, str):
        start_time = pd.to_datetime(start_time)
    if isinstance(end_time, str):
        end_time = pd.to_datetime(end_time)
    
    base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    all_events = []
    
    current_start = start_time
    total_chunks = 0
    
    if verbose:
        print(f"Downloading events from {start_time.date()} to {end_time.date()}")
        print(f"Region: lon [{min_longitude}, {max_longitude}], lat [{min_latitude}, {max_latitude}]")
        print(f"Magnitude: M ≥ {min_magnitude}" + (f" and M < {max_magnitude}" if max_magnitude else ""))
        if proxy:
            print(f"Using proxy: {proxy.get('http', proxy.get('https', 'unknown'))}")
    
    while current_start < end_time:
        current_end = min(current_start + timedelta(days=chunk_days), end_time)
        params = {
            'format': 'geojson',
            'starttime': current_start.strftime('%Y-%m-%d'),
            'endtime': current_end.strftime('%Y-%m-%d'),
            'minmagnitude': min_magnitude,
            'minlatitude': min_latitude,
            'maxlatitude': max_latitude,
            'minlongitude': min_longitude,
            'maxlongitude': max_longitude,
            'limit': max_events_per_chunk,
            'orderby': 'time'
        }
        if max_magnitude is not None:
            params['maxmagnitude'] = max_magnitude
        
        try:
            resp = requests.get(base_url, params=params, proxies=proxy, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            events = data.get('features', [])
            all_events.extend(events)
            total_chunks += 1
            if verbose:
                print(f"  Chunk {total_chunks}: {current_start.date()} → {current_end.date()} → {len(events)} events")
        except Exception as e:
            if verbose:
                print(f"  ERROR for chunk {current_start.date()} → {current_end.date()}: {e}")
        time.sleep(0.5)  # be polite to the server
        current_start = current_end + timedelta(days=1)
    
    if not all_events:
        if verbose:
            print("No events downloaded.")
        return pd.DataFrame(columns=['time', 'latitude', 'longitude', 'depth', 'mag'])
    
    # Convert to DataFrame
    records = []
    for ev in all_events:
        props = ev['properties']
        geom = ev['geometry']
        if geom is None:
            continue
        coords = geom['coordinates']
        records.append({
            'time': pd.to_datetime(props['time'], unit='ms'),
            'latitude': coords[1],
            'longitude': coords[0],
            'depth': coords[2],
            'mag': props['mag']
        })
    
    df = pd.DataFrame(records)
    df = df.dropna(subset=['mag', 'latitude', 'longitude', 'depth', 'time'])
    df.sort_values('time', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    if verbose:
        print(f"\nTotal events downloaded: {len(df)}")
        if len(df) > 0:
            print(f"Time range: {df['time'].min()} to {df['time'].max()}")
            print(f"Magnitude range: {df['mag'].min():.2f} – {df['mag'].max():.2f}")
    
    return df


# Configure your proxy (if needed)
proxy_settings = {
    'http': 'http://127.0.0.1:10808',
    'https': 'http://127.0.0.1:10808'
}
df = download_usgs_earthquakes(
    min_latitude=24, max_latitude=41,
    min_longitude=43, max_longitude=64,
    start_time='2020-01-01',
    end_time=datetime.now(),
    min_magnitude=3.5,
    proxy=proxy_settings,      # remove if no proxy needed
    chunk_days=365,
    verbose=True
)



# Configure your proxy (if needed)
proxy_settings = {
    'http': 'http://127.0.0.1:10808',
    'https': 'http://127.0.0.1:10808'
}
df = download_usgs_earthquakes(
    min_latitude=24, max_latitude=41,
    min_longitude=43, max_longitude=64,
    start_time='2020-01-01',
    end_time=datetime.now(),
    min_magnitude=3.5,
    proxy=proxy_settings,      # remove if no proxy needed
    chunk_days=365,
    verbose=True
)
