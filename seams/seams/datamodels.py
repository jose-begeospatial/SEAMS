from dataclasses import dataclass, field
from itertools import count
from typing import List



@dataclass(kw_only=True)
class DotPoint:
    frame_id: int
    x: float
    y: float
    count: int = field(default_factory=count().__next__, init=False)
    biota: list[str] = field(default_factory=list)
    substrates: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.count += 1



@dataclass(kw_only=True)
class Underwater_Images:
    img_id: int 
    path: str

@dataclass(kw_only=True)
class Frame:
    frame_id: int = field(default_factory=int)
    movie_id: str = field(default_factory=str)


@dataclass(kw_only=True)
class Movie:
    movie_id: str = field(default_factory=str)
    filename: str = field(default_factory=str)
    _filepath_url: str = field(default_factory=str)
    frames_selected: list[int] = field(default_factory=list[int])


@dataclass(kw_only=True)
class Media:
    movies: List[Movie] = field(default_factory=List[Movie])
    frames: List[Frame]  = field(default_factory=List[Frame])
    underwater_images: List[Underwater_Images]  = field(default_factory=List[Underwater_Images])


@dataclass(kw_only=True)
class Location:
    municipality: str = field(default_factory=str)
    county: str = field(default_factory= str)
    country: str = field(default='Sverige')
    countryCode: str = field(default='SE')
    decimal_latitude: float = field(default_factory=float)
    decimal_longitude: float = field(default_factory=float)
    SWEREF99TM_X: float = field(default_factory=float)
    SWEREF99TM_Y: float = field(default_factory=float)


# Using Minumum FlatObservation fields from Species Observation System (SOS)
# https://github.com/biodiversitydata-se/SOS/blob/master/Docs/FlatObservation.md#minimum
@dataclass(kw_only=True)
class Station:
    station_id: str = field(default_factory=str)
    project_name: str
    survey_name: str
    visit_year: str
    station_name: str = field(default_factory=str)    
    location: Location = field(default_factory=Location)
    dataset_name: str = field(default_factory=str)
    media: Media = field(default_factory=Media)

    