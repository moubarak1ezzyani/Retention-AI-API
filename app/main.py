from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database, crud, security, services

# tables DB : Création au démarrage 
models.MyBase.metadata.create_all(bind=database.engine)

app = FastAPI(title="RetentionAI API")

# --- CORS => Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- DEPENDENCY ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.secret_key, algorithms=[security.algo])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except security.JWTError:
        raise credentials_exception
        
    token_data = schemas.TokenData(username=username) 
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ROUTES ---
@app.post("/register", response_model=schemas.UserOutput)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username déjà utilisé.")
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Predcition  
@app.post("/predict", response_model=schemas.PredictionOutput)
def predict(
    employee_data: schemas.EmployeeInput, 
    current_user: models.UserDB = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # call ML serivce
    prediction, probability = services.predict_attrition(employee_data)
    
    # save history
    crud.create_prediction_history(
        db=db, 
        user_id=current_user.id, 
        probability=probability, 
        prediction=prediction,
        emp_id=str(employee_data.EmployeeNumber) 
    )
    
    return {"prediction": prediction, "probability": probability}

@app.post("/generate-retention-plan", response_model=schemas.RetentionPlanOutput)
def generate_plan(
    data: schemas.RetentionPlanInput,
    current_user: models.UserDB = Depends(get_current_user)
):
    # call gemini service
    raw_plan = services.generate_retention_plan(data.employee_data, data.churn_probability)
    return {"plan": raw_plan}

@app.get("/")
def read_root():
    return {"message": "RetentionAI API is running"}
