from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uvicorn
import json
from database import get_db, create_tables
from models import User
from schemas import UserBase, UserResponse
from redis_config import r

app = FastAPI()

create_tables()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@app.post("/users")
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    try:
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
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
async def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user_json = r.get(f"user:{user_id}")
        if user_json:
            print("User found in cache")
            return UserResponse(**json.loads(user_json))

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("User found in database")

        # Cache the user
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
        r.set(f"user:{user_id}", json.dumps(user_dict), ex=180)
        print("User cached")

        return UserResponse(**user)
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}") 

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)