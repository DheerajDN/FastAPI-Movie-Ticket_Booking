from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

# Pydantic models
class BookingRequest(BaseModel):
    customer_name: str=Field(min_length=2)
    movie_id: int=Field(gt=0)
    seats: int=Field(gt=0, le=10, description="Number of seats must be greater than 0 and at most 10")
    phone: str=Field(min_length=10)
    seat_type: str=Field(default="standard")
    promo_code: str=Field(default="")

class NewMovie(BaseModel):
    title: str=Field(min_length=2)
    genre: str=Field(min_length=2)
    language: str=Field(min_length=2)
    duration_mins: int=Field(gt=0)
    ticket_price: int=Field(gt=0)
    seats_available: int=Field(gt=0)

class SeatHoldRequest(BaseModel):
    customer_name: str=Field(min_length=2)
    movie_id: int=Field(gt=0)
    seats: int=Field(gt=0, le=10)

# Helper functions
def find_movie(movie_id: int):
    """Find a movie by ID. Returns the movie or None if not found."""
    for movie in movies:
        if movie["id"]==movie_id:
            return movie
    return None

def calculate_ticket_cost(base_price: int, seats: int, seat_type: str, promo_code: str="") -> dict:
    multiplier={
        "standard": 1.0,
        "premium": 1.5,
        "recliner": 2.0
    }
    seat_type_lower=seat_type.lower()
    rate=multiplier.get(seat_type_lower, 1.0)
    original_cost=int(base_price * rate * seats)
    discount_rate=0
    promo_upper=promo_code.upper()
    if promo_upper=="SAVE10":
        discount_rate=0.10
    elif promo_upper=="SAVE20":
        discount_rate=0.20
    discounted_cost=int(original_cost*(1-discount_rate))
    return {
        "original_cost": original_cost,
        "discounted_cost": discounted_cost,
        "discount_applied": discount_rate * 100 if discount_rate > 0 else None
    }

def filter_movies_logic(genre: str=None, language: str=None, max_price: int=None, min_seats: int=None) -> list:
    filtered=movies[:]
    if genre is not None:
        genre_lower=genre.lower()
        filtered=[m for m in filtered if m["genre"].lower()==genre_lower]
    if language is not None:
        language_lower=language.lower()
        filtered=[m for m in filtered if m["language"].lower()==language_lower]
    if max_price is not None:
        filtered=[m for m in filtered if m["ticket_price"]<=max_price]
    if min_seats is not None:
        filtered=[m for m in filtered if m["seats_available"]>=min_seats]
    return filtered

# Movies database
movies = [
    {
        "id": 1,
        "title": "The Dark Knight",
        "genre": "Action",
        "language": "English",
        "duration_mins": 152,
        "ticket_price": 250,
        "seats_available": 45
    },
    {
        "id": 2,
        "title": "Parasite",
        "genre": "Drama",
        "language": "Korean with subtitles",
        "duration_mins": 132,
        "ticket_price": 299,
        "seats_available": 32
    },
    {
        "id": 3,
        "title": "Hera Pheri",
        "genre": "Comedy",
        "language": "Hindi",
        "duration_mins": 156,
        "ticket_price": 199,
        "seats_available": 58
    },
    {
        "id": 4,
        "title": "Tumbbad",
        "genre": "Horror",
        "language": "Hindi",
        "duration_mins": 104,
        "ticket_price": 299,
        "seats_available": 28
    },
    {
        "id": 5,
        "title": "Inception",
        "genre": "Action",
        "language": "English",
        "duration_mins": 148,
        "ticket_price": 250,
        "seats_available": 51
    },
    {
        "id": 6,
        "title": "Dangal",
        "genre": "Drama",
        "language": "Hindi",
        "duration_mins": 161,
        "ticket_price": 199,
        "seats_available": 22
    },
    {
        "id": 7,
        "title": "3 Idiots",
        "genre": "Comedy",
        "language": "Hindi",
        "duration_mins": 170,
        "ticket_price": 199,
        "seats_available": 64
    }
]

bookings=[]
booking_counter=1
holds=[]
hold_counter=1
movie_counter=8

# Home endpoint
@app.get("/")
def read_Home():
    return {"message": "Welcome to CineStar Booking"}

# Get all movies with total count and total seats available
@app.get("/movies")
def get_movies():
    total_movies=len(movies)
    total_seats_available=sum(movie["seats_available"] for movie in movies)
    return {
        "movies": movies,
        "total": total_movies,
        "total_seats_available": total_seats_available
    }

# Filter movies with multiple optional criteria using is not None checks
@app.get("/movies/filter")
def filter_movies(genre: str=None, language: str=None, max_price: int=None, min_seats: int=None):
    genre_lower=genre.lower() if genre is not None else None
    language_lower=language.lower() if language is not None else None
    filtered=filter_movies_logic(genre=genre_lower, language=language_lower, max_price=max_price, min_seats=min_seats)
    return {
        "movies": filtered,
        "total": len(filtered),
        "filters_applied": {
            "genre": genre_lower,
            "language": language_lower,
            "max_price": max_price,
            "min_seats": min_seats
        }
    }

# Search movies by keyword across title, genre, and language
@app.get("/movies/search")
def search_movies(keyword: str):
    keyword_lower=keyword.lower()
    matches=[]
    for movie in movies:
        title_match=keyword_lower in movie["title"].lower()
        genre_match=keyword_lower in movie["genre"].lower()
        language_match=keyword_lower in movie["language"].lower()
        if title_match or genre_match or language_match:
            matches.append(movie)
    if not matches:
        return {
            "total_found": 0,
            "message": f"No movies found matching '{keyword}'",
            "keyword": keyword,
            "matches": []
        }
    return {
        "total_found": len(matches),
        "keyword": keyword,
        "matches": matches,
        "message": f"Found {len(matches)} movie(s) matching '{keyword}'"
    }

# Sort movies by specified field with validation
@app.get("/movies/sort")
def sort_movies(sort_by: str="ticket_price"):
    valid_sort_fields=["ticket_price", "title", "duration_mins", "seats_available"]
    sort_by_lower=sort_by.lower()
    if sort_by_lower not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by parameter. Allowed values: {', '.join(valid_sort_fields)}"
        )
    sorted_movies=sorted(movies, key=lambda m: m[sort_by_lower])
    return {
        "total": len(sorted_movies),
        "sorted_by": sort_by_lower,
        "order": "ascending",
        "movies": sorted_movies
    }

# Paginate movies with validation for page and limit parameters
@app.get("/movies/page")
def paginate_movies(page: int=1, limit: int=3):
    if page<1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0")
    if limit<1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    total_movies=len(movies)
    total_pages=(total_movies+limit-1) // limit 
    if page > total_pages and total_movies > 0:
        raise HTTPException(status_code=400, detail=f"Page {page} out of range. Total pages: {total_pages}")
    start_idx=(page-1)*limit
    end_idx=start_idx+limit
    paginated_movies=movies[start_idx:end_idx]
    return {
        "page": page,
        "limit": limit,
        "total": total_movies,
        "total_pages": total_pages,
        "movies": paginated_movies
    }

# Combined endpoint to browse movies with search, filter, sort, and pagination
@app.get("/movies/browse")
def browse_movies(
    keyword: str=None,
    genre: str=None,
    language: str=None,
    sort_by: str="ticket_price",
    order: str="asc",
    page: int=1,
    limit: int=3
):   
    result_movies = movies[:]
    if keyword is not None:
        keyword_lower=keyword.lower()
        result_movies=[
            m for m in result_movies
            if (keyword_lower in m["title"].lower() or
                keyword_lower in m["genre"].lower() or
                keyword_lower in m["language"].lower())
        ]
    if genre is not None:
        genre_lower=genre.lower()
        result_movies=[m for m in result_movies if m["genre"].lower()==genre_lower]
    if language is not None:
        language_lower=language.lower()
        result_movies=[m for m in result_movies if m["language"].lower()==language_lower]
    valid_sort_fields=["ticket_price", "title", "duration_mins", "seats_available"]
    sort_by_lower=sort_by.lower()
    if sort_by_lower not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by parameter. Allowed values: {', '.join(valid_sort_fields)}"
        )
    order_lower=order.lower()
    if order_lower not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid order parameter. Allowed values: asc, desc"
        )
    reverse=order_lower=="desc"
    result_movies=sorted(result_movies, key=lambda m: m[sort_by_lower], reverse=reverse)
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    total_movies=len(result_movies)
    total_pages=(total_movies+limit-1) // limit
    if page > total_pages and total_movies > 0:
        raise HTTPException(status_code=400, detail=f"Page {page} out of range. Total pages: {total_pages}")
    start_idx=(page-1)*limit
    end_idx=start_idx+limit
    paginated_movies=result_movies[start_idx:end_idx]
    return {
        "page": page,
        "limit": limit,
        "total": total_movies,
        "total_pages": total_pages,
        "sorted_by": sort_by_lower,
        "order": order_lower,
        "filters": {
            "keyword": keyword,
            "genre": genre,
            "language": language
        },
        "movies": paginated_movies
    }
    
# Endpoint to get summary statistics about movies
@app.get("/movies/summary")
def get_movies_summary():
    total_movies=len(movies)
    if movies:
        most_expensive_movie=max(movies, key=lambda m: m["ticket_price"])
        cheapest_movie=min(movies, key=lambda m: m["ticket_price"])
        most_expensive_ticket=most_expensive_movie["ticket_price"]
        most_expensive_title=most_expensive_movie["title"]
        cheapest_ticket=cheapest_movie["ticket_price"]
        cheapest_title=cheapest_movie["title"]
    else:
        most_expensive_ticket=0
        cheapest_ticket=0
        most_expensive_title=None
        cheapest_title=None
    
    total_seats=sum(movie["seats_available"] for movie in movies)
    
    genre_count={}
    for movie in movies:
        genre = movie["genre"]
        genre_count[genre]=genre_count.get(genre, 0)+1
    return {
        "total_movies": total_movies,
        "most_expensive_ticket": most_expensive_ticket,
        "most_expensive_movie": most_expensive_title,
        "cheapest_ticket": cheapest_ticket,
        "cheapest_movie": cheapest_title,
        "total_seats": total_seats,
        "movies_by_genre": genre_count
    }

# Endpoint to create a new movie with validation and duplicate title check
@app.post("/movies", status_code=status.HTTP_201_CREATED)
def create_movie(new_movie: NewMovie):
    global movie_counter
    title_lower=new_movie.title.lower()
    for movie in movies:
        if movie["title"].lower()==title_lower:
            raise HTTPException(status_code=400, detail=f"Movie with title '{new_movie.title}' already exists")
    movie={
        "id": movie_counter,
        "title": new_movie.title,
        "genre": new_movie.genre,
        "language": new_movie.language,
        "duration_mins": new_movie.duration_mins,
        "ticket_price": new_movie.ticket_price,
        "seats_available": new_movie.seats_available
    }
    movies.append(movie)
    movie_counter+=1
    return {
        "status": "created",
        "movie": movie
    }

# Endpoint to get movie details by ID with error handling for not found
@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    for movie in movies:
        if movie["id"]==movie_id:
            return movie
    raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")

# Endpoint to update movie details with validation and partial updates
@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: int = None, seats_available: int = None):
    movie=find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    if ticket_price is not None:
        movie["ticket_price"]=ticket_price
    if seats_available is not None:
        movie["seats_available"]=seats_available
    return {
        "status": "updated",
        "movie": movie
    }

# Endpoint to delete a movie with checks for existing bookings and error handling
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie=find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    movie_bookings=[b for b in bookings if b["movie_id"]==movie_id]
    if movie_bookings:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete movie with id {movie_id}. {len(movie_bookings)} booking(s) exist for this movie."
        )
    movies.remove(movie)
    return {
        "status": "deleted",
        "message": f"Movie with id {movie_id} successfully deleted"
    }

# Endpoint to get all bookings with total count and total revenue
@app.get("/bookings")
def get_bookings():
    total_bookings=len(bookings)
    total_revenue=sum(booking.get("total", 0) for booking in bookings)
    return {
        "bookings": bookings,
        "total": total_bookings,
        "total_revenue": total_revenue
    }

# Endpoint to search bookings by customer name with case-insensitive matching and detailed response
@app.get("/bookings/search")
def search_bookings(customer_name: str):
    customer_name_lower=customer_name.lower()
    matches=[]
    for booking in bookings:
        if customer_name_lower in booking["customer_name"].lower():
            matches.append(booking)
    if not matches:
        return {
            "total_found": 0,
            "message": f"No bookings found for customer '{customer_name}'",
            "customer_name": customer_name,
            "matches": []
        }
    return {
        "total_found": len(matches),
        "customer_name": customer_name,
        "matches": matches,
        "message": f"Found {len(matches)} booking(s) for '{customer_name}'"
    }

# Endpoint to sort bookings by total cost or number of seats with validation
@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total"):
    valid_sort_fields=["total", "seats"]
    sort_by_lower=sort_by.lower()
    if sort_by_lower not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by parameter. Allowed values: {', '.join(valid_sort_fields)}"
        )
    sorted_bookings=sorted(bookings, key=lambda b: b[sort_by_lower])
    return {
        "total": len(sorted_bookings),
        "sorted_by": sort_by_lower,
        "order": "ascending",
        "bookings": sorted_bookings
    }

# Endpoint to paginate bookings with validation for page and limit parameters
@app.get("/bookings/page")
def paginate_bookings(page: int=1, limit: int=5):
    if page<1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0")
    if limit<1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    total_bookings=len(bookings)
    total_pages=(total_bookings+limit-1)// limit
    if page > total_pages and total_bookings > 0:
        raise HTTPException(status_code=400, detail=f"Page {page} out of range. Total pages: {total_pages}")
    start_idx=(page-1)*limit
    end_idx=start_idx+limit
    paginated_bookings=bookings[start_idx:end_idx]
    return {
        "page": page,
        "limit": limit,
        "total": total_bookings,
        "total_pages": total_pages,
        "bookings": paginated_bookings
    }

# Endpoint to create a new booking with validation, cost calculation, and error handling for movie and seat availability
@app.post("/bookings")
def create_booking(booking_request: BookingRequest):
    global booking_counter
    movie=find_movie(booking_request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {booking_request.movie_id} not found")
    if movie["seats_available"]<booking_request.seats:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough seats available. Requested: {booking_request.seats}, Available: {movie['seats_available']}"
        )
    cost_breakdown=calculate_ticket_cost(movie["ticket_price"], booking_request.seats, booking_request.seat_type, booking_request.promo_code)
    booking={
        "booking_id": booking_counter,
        "customer_name": booking_request.customer_name,
        "phone": booking_request.phone,
        "movie_title": movie["title"],
        "movie_id": booking_request.movie_id,
        "seats": booking_request.seats,
        "seat_type": booking_request.seat_type,
        "promo_code": booking_request.promo_code if booking_request.promo_code else None,
        "original_cost": cost_breakdown["original_cost"],
        "discount_applied": cost_breakdown["discount_applied"],
        "total": cost_breakdown["discounted_cost"]
    }
    bookings.append(booking)
    movie["seats_available"]-=booking_request.seats
    booking_counter+=1
    return booking

# Endpoint to manage seat holds with creation, confirmation, and release functionality
@app.get("/seat-hold")
def get_seat_holds():
    total_holds=len(holds)
    total_seats_on_hold=sum(hold.get("seats", 0) for hold in holds)
    return {
        "holds": holds,
        "total": total_holds,
        "total_seats_on_hold": total_seats_on_hold
    }

# Endpoint to create a seat hold with validation for movie existence and seat availability, and temporary reduction of available seats
@app.post("/seat-hold", status_code=status.HTTP_201_CREATED)
def create_seat_hold(hold_request: SeatHoldRequest):
    global hold_counter
    movie=find_movie(hold_request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {hold_request.movie_id} not found")
    if movie["seats_available"]<hold_request.seats:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough seats available. Requested: {hold_request.seats}, Available: {movie['seats_available']}"
        )
    hold = {
        "hold_id": hold_counter,
        "customer_name": hold_request.customer_name,
        "movie_id": hold_request.movie_id,
        "movie_title": movie["title"],
        "seats": hold_request.seats
    }
    holds.append(hold)
    movie["seats_available"]-=hold_request.seats
    hold_counter+=1
    return {
        "status": "created",
        "hold": hold
    }

# Endpoint to confirm a seat hold, converting it into a booking, and removing the hold from the list
@app.post("/seat-confirm/{hold_id}")
def confirm_seat_hold(hold_id: int):
    global booking_counter
    hold=None
    for h in holds:
        if h["hold_id"]==hold_id:
            hold=h
            break
    if not hold:
        raise HTTPException(status_code=404, detail=f"Hold with id {hold_id} not found")
    movie=find_movie(hold["movie_id"])
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {hold['movie_id']} not found")
    booking={
        "booking_id": booking_counter,
        "customer_name": hold["customer_name"],
        "phone": "",
        "movie_title": hold["movie_title"],
        "movie_id": hold["movie_id"],
        "seats": hold["seats"],
        "seat_type": "standard",
        "promo_code": None,
        "original_cost": movie["ticket_price"] * hold["seats"],
        "discount_applied": None,
        "total": movie["ticket_price"] * hold["seats"]
    }
    bookings.append(booking)
    holds.remove(hold)
    booking_counter+=1
    return {
        "status": "confirmed",
        "booking": booking
    }

# Endpoint to release a seat hold, adding the seats back to the movie's available seats, and removing the hold from the list
@app.delete("/seat-release/{hold_id}")
def release_seat_hold(hold_id: int):
    hold=None
    for h in holds:
        if h["hold_id"]==hold_id:
            hold=h
            break
    if not hold:
        raise HTTPException(status_code=404, detail=f"Hold with id {hold_id} not found")
    movie=find_movie(hold["movie_id"])
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {hold['movie_id']} not found")
    movie["seats_available"] += hold["seats"]
    holds.remove(hold)
    return {
        "status": "released",
        "message": f"Hold {hold_id} released. {hold['seats']} seats added back to {hold['movie_title']}"
    }