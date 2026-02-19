from fastapi import FastAPI, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
import uvicorn
import json
import time
import asyncio
from database import get_db, create_tables
from models import User
from schemas import UserBase, UserResponse
import hashlib
from redis_config import r

app = FastAPI()

create_tables()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/users", response_model=list[UserResponse])
async def get_users(response: Response, db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        response.headers["Cache-Control"] = "no-cache"
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@app.post("/users")
async def create_user(response: Response, user: UserBase, db: Session = Depends(get_db)):
    try:
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        response.headers["Cache-Control"] = "public,max-age=3600"

        db_user = User(name=user.name, email=user.email, password=user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return "user created successfully"
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    try:
        cache_key = f"user:{user_id}"

        # 1️⃣ Try Redis first
        user_json = r.get(cache_key)
        if user_json:
            print("User found in Redis")
            user_dict = json.loads(user_json)
        else:
            # 2️⃣ Stampede protection
            lock_key = f"lock:user:{user_id}"
            lock_acquired = r.set(lock_key, "1", nx=True, ex=10)

            if lock_acquired:
                print("lock acquired")
                try:
                    print("Fetching from DB")
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        raise HTTPException(status_code=404, detail="User not found")

                    user_dict = {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                    }

                    r.set(cache_key, json.dumps(user_dict), ex=180)
                finally:
                    r.delete(lock_key)
            else:
                await asyncio.sleep(0.5)
                user_json = r.get(cache_key)
                if user_json:
                    user_dict = json.loads(user_json)
                else:
                    raise HTTPException(status_code=503, detail="Temporary unavailable")

        # 3️⃣ Compute ETag AFTER final data
        body = json.dumps(user_dict, sort_keys=True).encode()
        etag = hashlib.md5(body).hexdigest()

        # 4️⃣ HTTP validation
        if request.headers.get("if-none-match") == etag:
            print("http caching worked")
            return Response(status_code=304)

        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "private, no-cache"

        return user_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        r.delete(f"user:{user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return "user deleted successfully"
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}") 

@app.patch("/users/{user_id}")
async def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        db_user.name = user.name
        db_user.email = user.email
        db_user.password = user.password

        db.commit()
        db.refresh(db_user)

        r.delete(f"user:{user_id}")
        return "user updated successfully"
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}") 

@app.get("/message")
async def get_message():
    # Add a message to the queue
    add_message("Hello World")
    return "Message added to queue"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)