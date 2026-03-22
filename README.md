# CineStar Booking - Movie Ticket Reservation System

## Introduction

CineStar Booking is a comprehensive movie ticket reservation system built with modern web technologies. This project demonstrates the implementation of a fully functional backend API for a cinema booking platform, complete with advanced features like seat holds, promo codes, and intelligent search/filtering capabilities. It's designed to handle real-world movie booking scenarios while maintaining clean, maintainable code architecture.

## Project Overview

CineStar Booking is a RESTful API that allows users to browse movies, create bookings, manage seat reservations, and apply promotional discounts. The system operates on a mock database with pre-loaded movie data and provides comprehensive endpoints for movie management, booking operations, and seat hold functionality.

The project serves as an excellent learning tool for understanding FastAPI, data validation with Pydantic, RESTful API design principles, and practical backend development patterns.

## Tech Stack

- **Framework**: FastAPI (Python)
- **Data Validation**: Pydantic
- **Language**: Python 3.8+
- **Server**: Uvicorn (ASGI server)
- **Architecture**: RESTful API with in-memory data storage

## Key Features

### Movie Management
- **Browse & Search**: Full-text search across movie titles, genres, and languages
- **Filtering**: Advanced filtering by genre, language, price range, and seat availability
- **Sorting**: Sort movies by various criteria (ticket price, title, duration, available seats)
- **Pagination**: Paginated movie listings with customizable page size
- **Advanced Browse**: Combined search, filter, sort, and pagination in a single endpoint

### Booking System
- **Flexible Seat Selection**: Support for different seat types (standard, premium, recliner) with dynamic pricing
- **Promo Codes**: Support for discount codes (SAVE10: 10% off, SAVE20: 20% off)
- **Booking Confirmation**: Complete booking history with customer and payment details
- **Revenue Tracking**: Automatic calculation of total revenue across all bookings

### Seat Hold Management
- **Temporary Seat Holds**: Hold seats for a limited time without immediate payment
- **Hold Confirmation**: Convert holds to confirmed bookings
- **Hold Release**: Cancel holds and restore seats to availability
- **Hold Tracking**: Monitor all active seat holds in the system

### Advanced Features
- **Movie CRUD Operations**: Create, read, update, and delete movies
- **Duplicate Prevention**: Prevent duplicate movie titles in the system
- **Booking Constraints**: Prevent deletion of movies with active bookings
- **Case-Insensitive Operations**: All searches and filters are case-insensitive for better UX
- **Comprehensive Statistics**: Get insights into movie inventory and pricing

## Project Structure

```
FastAPI-Movie-Ticket-Booking/
├── main.py                    # Main application file with all endpoints
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

### Code Organization in main.py

1. **Imports & App Setup** - FastAPI initialization and imports
2. **Pydantic Models** - Data validation classes
   - `BookingRequest`: Booking creation schema
   - `NewMovie`: Movie creation schema
   - `SeatHoldRequest`: Seat hold creation schema
3. **Helper Functions** - Reusable utility functions
   - `find_movie()`: Locate movies by ID
   - `calculate_ticket_cost()`: Calculate costs with seat types and promos
   - `filter_movies_logic()`: Apply multiple filters
4. **Data Layer** - In-memory databases
   - `movies`: Movie catalog
   - `bookings`: Confirmed reservations
   - `holds`: Temporary seat holds
5. **API Endpoints** - Organized by resource type (movies, bookings, seat-holds)

## How to Run the Project

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   cd FastAPI-Movie-Ticket-Booking
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API**
   - API will be available at: `http://localhost:8000`
   - Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
   - Alternative documentation (ReDoc): `http://localhost:8000/redoc`

### Testing the API

You can test the API using any of these tools:
- **Swagger UI** (http://localhost:8000/docs) - Interactive interface in browser
- **curl** - Command line tool
- **Postman** - API testing application
- **Python requests** - Programmatic testing

Example curl request:
```bash
curl http://localhost:8000/movies
```

## API Endpoints Overview

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/` | Welcome message | - |
| **MOVIES** | | | |
| GET | `/movies` | Get all movies with stats | - |
| GET | `/movies/{movie_id}` | Get specific movie by ID | movie_id (path) |
| GET | `/movies/search` | Search movies by keyword | keyword (required) |
| GET | `/movies/filter` | Filter movies by criteria | genre, language, max_price, min_seats |
| GET | `/movies/sort` | Sort movies by field | sort_by (default: ticket_price) |
| GET | `/movies/page` | Paginate movies | page (default: 1), limit (default: 3) |
| GET | `/movies/browse` | Search + filter + sort + paginate | keyword, genre, language, sort_by, order, page, limit |
| GET | `/movies/summary` | Get movie statistics | - |
| POST | `/movies` | Create new movie | title, genre, language, duration_mins, ticket_price, seats_available |
| PUT | `/movies/{movie_id}` | Update movie details | ticket_price, seats_available |
| DELETE | `/movies/{movie_id}` | Delete movie | movie_id (path) |
| **BOOKINGS** | | | |
| GET | `/bookings` | Get all bookings with revenue | - |
| GET | `/bookings/{booking_id}` | Get booking details | booking_id (path) |
| GET | `/bookings/search` | Search bookings by customer | customer_name (required) |
| GET | `/bookings/sort` | Sort bookings | sort_by (total or seats) |
| GET | `/bookings/page` | Paginate bookings | page (default: 1), limit (default: 5) |
| POST | `/bookings` | Create booking | customer_name, movie_id, seats, phone, seat_type, promo_code |
| **SEAT HOLDS** | | | |
| GET | `/seat-hold` | Get all seat holds | - |
| POST | `/seat-hold` | Create seat hold | customer_name, movie_id, seats |
| POST | `/seat-confirm/{hold_id}` | Confirm hold to booking | hold_id (path) |
| DELETE | `/seat-release/{hold_id}` | Release/cancel hold | hold_id (path) |

## Learning Outcomes

Through building this project, I gained practical experience in:

### Backend Development
- **RESTful API Design**: Understanding CRUD operations and proper HTTP methods
- **FastAPI Framework**: Building modern, high-performance APIs with automatic validation
- **Data Validation**: Using Pydantic for robust request/response validation
- **Error Handling**: Implementing proper HTTP status codes and error messages

### Software Architecture
- **Separation of Concerns**: Organizing code into models, helpers, and endpoints
- **Code Reusability**: Creating helper functions to avoid duplication
- **Data Structure Design**: Designing efficient data models for complex operations
- **Scalability Patterns**: Understanding how to structure APIs for growth

### Feature Implementation
- **Business Logic**: Implementing complex features like promo codes and seat management
- **Search & Filtering**: Building multi-criteria search and advanced filtering
- **Pagination**: Implementing efficient data pagination for large datasets
- **Validation Rules**: Enforcing business constraints at API boundaries

### Development Best Practices
- **Code Comments**: Writing clear, meaningful documentation
- **Naming Conventions**: Using descriptive variable and function names
- **Case Handling**: Implementing case-insensitive operations for better UX
- **Testing**: Designing APIs that are testable and debuggable

## Challenges Faced

### 1. Concurrent State Management
**Challenge**: Managing movie seat availability when bookings and holds exist simultaneously.
**Solution**: Tracked seat availability carefully, ensuring both bookings and holds reduce available seats, while only bookings permanently consume them.

### 2. Data Integrity Without a Database
**Challenge**: Preventing data inconsistencies with in-memory storage and no transactions.
**Solution**: Implemented validation checks before modifications and careful ordering of operations to maintain consistency.

### 3. Complex Search Logic
**Challenge**: Implementing search that matches across multiple fields (title, genre, language) efficiently.
**Solution**: Used list comprehensions with conditional matching and case-insensitive comparisons.

### 4. Pagination Validation
**Challenge**: Accurately calculating total pages and validating page ranges.
**Solution**: Used ceiling division formula and proper boundary checking.

### 5. Duplicate Prevention
**Challenge**: Preventing duplicate movie titles while maintaining case-insensitive operations.
**Solution**: Implemented case-insensitive comparison for duplicate checking.

### 6. Seat Type Pricing
**Challenge**: Supporting dynamic pricing for different seat types with promo code discounts.
**Solution**: Created a flexible cost calculation function that applies multipliers then discounts in the correct order.

### 7. Multi-Step Filtering
**Challenge**: Combining search, filters, sorting, and pagination in the browse endpoint.
**Solution**: Applied transformations in a specific order: search → filter → sort → paginate, maintaining immutability of original data.

## Conclusion

CineStar Booking demonstrates a complete, production-ready movie booking system backend. The project successfully implements complex features like dynamic pricing, seat holds, advanced search, and pagination while maintaining clean, readable code.

Key achievements:
- ✅ 25+ API endpoints covering all CRUD operations
- ✅ Comprehensive data validation and error handling
- ✅ Advanced search, filter, and sort capabilities
- ✅ Flexible seat hold management system
- ✅ Promo code and discount implementation
- ✅ Case-insensitive operations throughout
- ✅ Well-documented, human-readable code

This project serves as a solid foundation for understanding modern backend development with FastAPI and can be extended with features like:
- Database integration (PostgreSQL/MongoDB)
- User authentication and authorization
- Payment gateway integration
- Email notifications
- Real-time seat availability updates
- Advanced analytics and reporting